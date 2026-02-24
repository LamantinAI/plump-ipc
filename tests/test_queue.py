import asyncio
import logging
import time
import threading
import multiprocessing as mp

import pytest
from plump_ipc import plump_bus

logger = logging.getLogger(__name__)


def bus_worker(conn, count=5):
    plump_bus.set_producer(conn)
    for index in range(count):
        plump_bus.broadcast(f"msg_{index}")
        time.sleep(0.1)


def test_sync_bus_listener():
    parent_conn, child_conn = mp.Pipe()
    plump_bus.set_consumer(parent_conn)

    received_messages = []

    def callback(data):
        received_messages.append(data)

    # Start the worker process
    process = mp.Process(target=bus_worker, args=(child_conn,))
    process.start()

    # Launch the listener in a separate thread since it's a blocking call
    listener_thread = threading.Thread(target=plump_bus.setup_listener, args=(callback,), daemon=True)
    listener_thread.start()

    try:
        # Wait for the worker to finish execution
        process.join(timeout=2)
        # Allow some time for the listener to process the final message
        time.sleep(0.2)

        assert len(received_messages) == 5
        assert received_messages[0] == "msg_0"
        assert received_messages[-1] == "msg_4"
    finally:
        process.terminate()


@pytest.mark.asyncio
async def test_async_bus_listener():
    parent_conn, child_conn = mp.Pipe()
    plump_bus.set_consumer(parent_conn)

    future = asyncio.get_running_loop().create_future()
    received_messages = []

    async def async_callback(data):
        received_messages.append(data)
        if len(received_messages) == 5:
            future.set_result(True)

    # Configure the asynchronous listener
    plump_bus.setup_async_listener(async_callback)

    process = mp.Process(target=bus_worker, args=(child_conn,))
    process.start()

    try:
        await asyncio.wait_for(future, timeout=2.0)

        assert len(received_messages) == 5
        assert "msg_0" in received_messages
    finally:
        process.terminate()
        process.join()
        # Important: Remove the reader to avoid flooding logs with errors from a closed FD (File Descriptor)
        loop = asyncio.get_running_loop()
        try:
            loop.remove_reader(parent_conn.fileno())
        except Exception as e:
            logger.error(f"Cannot remove reader {e}")
