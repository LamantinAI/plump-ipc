import asyncio
from multiprocessing.connection import Connection
from threading import Lock
from typing import Any, Callable, Optional

from plump_ipc import logger
from plump_ipc.exceptions import PlumpConnectionError


class PlumpQueue:
    def __init__(self):
        self._send_conn: Optional[Connection] = None
        self._recv_conn: Optional[Connection] = None
        self._lock = Lock()

    def set_producer(self, conn: Connection):
        self._send_conn = conn

    def set_consumer(self, conn: Connection):
        self._recv_conn = conn

    def broadcast(self, item):
        if not self._send_conn:
            raise PlumpConnectionError(
                "Bus producer not initialized. Make sure to call set_producer() in the worker process."
            )
        with self._lock:
            self._send_conn.send(item)

    def get(self) -> Any:
        if not self._recv_conn:
            raise PlumpConnectionError(
                "Bus consumer not initialized. Make sure to call set_consumer() in the main process."
            )
        return self._recv_conn.recv()

    def poll(self, timeout: float = 0) -> bool:
        return self._recv_conn.poll(timeout) if self._recv_conn else False

    def setup_listener(self, callback: Callable, *args, **kwargs):
        """
        Synchronous blocking listener.
        Usually executed in a separate Thread.
        """
        logger.info("PlumpQueue synchronous listener started")
        while True:
            try:
                # Wait for data (blocks until something is received)
                data = self.get()
                callback(data, *args, **kwargs)
            except (EOFError, BrokenPipeError):
                logger.info("PlumpQueue connection closed. Stopping listener.")
                break
            except Exception as e:
                logger.error(f"Error in PlumpQueue listener: {e}")

    def setup_async_listener(self, callback: Callable, *args, **kwargs):
        """
        Asynchronous non-blocking listener for the asyncio event loop.
        """
        loop = asyncio.get_running_loop()
        fd = self._recv_conn.fileno()

        def read_ready():
            # Check poll() to drain all accumulated messages at once
            while self._recv_conn and self._recv_conn.poll():
                try:
                    data = self.get()
                    # Check if the callback is a coroutine function
                    if asyncio.iscoroutinefunction(callback):
                        asyncio.create_task(callback(data, *args, **kwargs))
                    else:
                        # If a regular function is provided, run it in an executor to avoid blocking the loop
                        loop.run_in_executor(None, callback, data, *args, **kwargs)
                except EOFError:
                    loop.remove_reader(fd)
                    logger.info("Async listener: Pipe closed.")
                    break
                except Exception as e:
                    logger.error(f"Async listener error: {e}")

        loop.add_reader(fd, read_ready)