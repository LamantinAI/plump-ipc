import logging
import multiprocessing as mp

import pytest
from plump_ipc import plump

logger = logging.getLogger(__name__)


# Defining the command
@plump.command()
def update_stream(stream_id: str, settings: dict):
    logger.debug("got rpc call")
    return {"status": True, "received_id": stream_id, "applied_settings": settings}


# Process worker
def start_worker(conn):
    logging.basicConfig()
    plump.child_conn = conn
    plump.run_worker()


def test_basic_command_execution():
    # Create a Pipe for inter-process communication
    parent_conn, child_conn = mp.Pipe()

    # Start the worker in a separate process
    process = mp.Process(target=start_worker, args=(child_conn,), daemon=True)
    process.start()
    logger.debug("process started")

    # Configure the main instance in the parent process
    plump.parent_conn = parent_conn

    try:
        # 3. Perform a synchronous call
        stream_id = 1
        settings = {"bitrate": 5000, "codec": "h264"}

        result = plump.call("update_stream", stream_id, settings)

        # 4. Verify the integrity of returned data
        assert result["status"] is True
        assert result["received_id"] == stream_id
        assert result["applied_settings"] == settings

    finally:
        # Shutdown the worker and the process
        try:
            plump.stop_worker()
        except Exception as e:
            logger.error(f"Cannot stop worker: {e}")
        process.join(timeout=1)
        if process.is_alive():
            process.terminate()


@pytest.mark.asyncio
async def test_basic_async_command_execution():
    parent_conn, child_conn = mp.Pipe()
    process = mp.Process(target=start_worker, args=(child_conn,), daemon=True)
    process.start()

    plump.parent_conn = parent_conn

    try:
        # Perform an asynchronous call
        result = await plump.acall("update_stream", 777, {"fps": 60})

        assert result["received_id"] == 777
        assert result["applied_settings"]["fps"] == 60

    finally:
        try:
            plump.stop_worker()
        except Exception as e:
            logger.error(f"Cannot stop worker: {e}")
        process.join(timeout=1)
        if process.is_alive():
            process.terminate()
