class PlumpError(Exception):
    """Base exception for the PlumpIPC library."""
    pass


class PlumpConnectionError(PlumpError):
    """Raised when a connection or initialization error occurs (e.g., producer not set)."""
    pass


class PlumpWorkerError(PlumpError):
    """Raised when an error occurs on the worker side (e.g., method not found or an exception inside the function)."""
    pass


class PlumpSerializationError(PlumpError):
    """Raised when an error occurs during data packing or unpacking (serialization/deserialization)."""
    pass
