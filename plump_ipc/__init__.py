from .logs import logger
from .exceptions import PlumpError, PlumpConnectionError, PlumpWorkerError
from .serialization import Serializer, PickleSerializer, JsonSerializer
from .queue import PlumpQueue
from .rpc import PlumpIPC

# Default instance for quick start
plump = PlumpIPC()
plump_bus = PlumpQueue()

__all__ = [
    "logger",
    "PlumpIPC", 
    "PlumpQueue", 
    "plump", 
    "plump_bus",
    "PlumpError",
    "PlumpConnectionError",
    "PlumpWorkerError",
    "Serializer",
    "PickleSerializer",
    "JsonSerializer"
]
