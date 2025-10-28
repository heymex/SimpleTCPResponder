"""Tests for echo server."""

import asyncio
import pytest
from servers.echo_server import EchoServer


@pytest.mark.asyncio
async def test_echo_server_basic():
    """Test basic echo server functionality."""
    server = EchoServer(port=9999, bind_address='127.0.0.1')

    # Start server in background
    server_task = asyncio.create_task(server.start())

    # Give server time to start
    await asyncio.sleep(0.5)

    try:
        # Connect and send data
        reader, writer = await asyncio.open_connection('127.0.0.1', 9999)

        # Send test message
        test_message = b'Hello, Echo!'
        writer.write(test_message)
        await writer.drain()

        # Read response
        response = await reader.read(1024)
        assert response == test_message

        # Close connection
        writer.close()
        await writer.wait_closed()

    finally:
        # Stop server
        await server.stop()
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_echo_server_multiple_messages():
    """Test echo server with multiple messages."""
    server = EchoServer(port=9998, bind_address='127.0.0.1')

    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.5)

    try:
        reader, writer = await asyncio.open_connection('127.0.0.1', 9998)

        # Send multiple messages
        messages = [b'Message 1', b'Message 2', b'Message 3']
        for msg in messages:
            writer.write(msg)
            await writer.drain()

            response = await reader.read(1024)
            assert response == msg

        writer.close()
        await writer.wait_closed()

    finally:
        await server.stop()
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
