import traceback
import multiprocessing as mp
import asyncio
from typing import Any, Callable, Optional

from plump_ipc.logs import logger
from plump_ipc.serialization import PickleSerializer, Serializer


class PlumpIPC:
    def __init__(self, serializer: Serializer = PickleSerializer):
        self.parent_conn, self.child_conn = mp.Pipe()
        self._registry: dict[str, Callable] = {}
        self._serializer = serializer
        self._instance = None

    def command(self, name: Optional[str] = None):
        def decorator(func: Callable):
            method_name = name or func.__name__
            self._registry[method_name] = func
            return func

        return decorator

    def set_context(self, instance: Any):
        self._instance = instance

    def run_worker(self):
        logger.info("PlumpIPC worker started")
        while True:
            try:
                raw_data = self.child_conn.recv_bytes()
                method_name, args, kwargs = self._serializer.loads(raw_data)

                if method_name == "__shutdown__":
                    logger.debug("Shutdown signal received")
                    break

                if method_name in self._registry:
                    try:
                        func = self._registry[method_name]
                        res = func(self._instance, *args, **kwargs) if self._instance else func(*args, **kwargs)
                        response = {"status": "ok", "data": res}
                    except Exception:
                        response = {"status": "error", "msg": traceback.format_exc()}
                else:
                    response = {"status": "error", "msg": f"Method {method_name} not found"}

                self.child_conn.send_bytes(self._serializer.dumps(response))

            except EOFError:
                break
            except Exception as e:
                logger.critical(f"Critical worker error: {e}")
                break

    def call(self, method_name: str, *args, **kwargs) -> Any:
        payload = self._serializer.dumps((method_name, args, kwargs))
        self.parent_conn.send(payload)
        response = self._serializer.loads(self.parent_conn.recv())

        if response["status"] == "ok":
            return response["data"]
        raise RuntimeError(response["msg"])

    async def acall(self, method_name: str, *args, **kwargs) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.call, method_name, *args, **kwargs)

    def stop_worker(self):
        try:
            payload = self._serializer.dumps(("__shutdown__", (), {}))
            self.parent_conn.send_bytes(payload)
        except (BrokenPipeError, OSError):
            pass
