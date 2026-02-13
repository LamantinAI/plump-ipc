# PlumpIPC

PlumpIPC is a lightweight inter-process communication (IPC) framework designed to simplify command execution and message broadcasting between Python processes. It bridges the gap between high-performance multiprocessing and modern asynchronous applications.

## Purpose

Python's Global Interpreter Lock (GIL) and the single-threaded nature of the `asyncio` event loop can become bottlenecks when dealing with CPU-bound tasks. PlumpIPC allows you to:

* **Offload Heavy Computations**: Move blocking tasks to a separate process to keep the `asyncio` loop responsive.
* **Bypass the GIL**: Utilize multiple CPU cores effectively by distributing logic across process boundaries.
* **Unified Interface**: Interact with remote processes using both synchronous and asynchronous APIs.

## Key Features

* **Dual Interface**: Support for standard synchronous `call()` and `asyncio`-native `acall()`.
* **Command Registry**: Easily register methods via decorators to create an RPC-like gateway.
* **State Flexibility**: Supports both instance-based (stateful) services and standalone (stateless) functions.
* **Asynchronous Event Bus**: `PlumpQueue` provides a mechanism for broadcasting events with non-blocking listeners for `asyncio`.
* **Custom Serialization**: Includes built-in support for `Pickle` and `JSON`, with an extensible interface for custom formats.

## Installation

```bash
pip install plump-ipc
```

## Quick Start

### 1. Define and Run a Worker

You can use the built-in `plump` instance for quick setup.

```python
from plump_ipc import plump

@plump.command()
def update_stream(stream_id: int, settings: dict):
    # Logic to update stream
    return True

def start_worker(conn):
    plump.child_conn = conn
    plump.run_worker()
```

### 2. Execute Commands

```python
# Asynchronous call
result = await plump.acall("update_stream", message.stream_id, message.settings)

# Synchronous call
result = plump.call("update_stream", 1, {"bitrate": 5000})
```

### 3. Using the Event Bus

```python
from plump_ipc import plump_bus

async def on_event(data):
    print(f"Received event: {data}")

# Setup async listener in your main loop
plump_bus.setup_async_listener(on_event)

# Broadcast from the worker process
plump_bus.broadcast("Processing started")
```

## Architecture

PlumpIPC utilizes `multiprocessing.Pipe` for low-latency communication. The `PlumpIPC` class manages the command-response cycle (RPC), while `PlumpQueue` handles unidirectional or broadcast event streams. By integrating with `loop.add_reader`, PlumpIPC ensures that incoming data from pipes triggers `asyncio` tasks immediately without polling overhead.
