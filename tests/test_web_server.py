"""Tests for web server."""

import asyncio
import pytest
import aiohttp
from servers.web_server import WebServer


@pytest.mark.asyncio
async def test_web_server_basic():
    """Test basic web server functionality."""
    test_content = "Hello, World!"
    server = WebServer(port=9997, content=test_content, bind_address='127.0.0.1')

    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.5)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://127.0.0.1:9997/') as response:
                assert response.status == 200
                text = await response.text()
                assert text == test_content

    finally:
        await server.stop()
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_web_server_html_content():
    """Test web server with HTML content."""
    html_content = "<!DOCTYPE html><html><body>Test</body></html>"
    server = WebServer(port=9996, content=html_content, bind_address='127.0.0.1')

    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.5)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://127.0.0.1:9996/test') as response:
                assert response.status == 200
                assert response.content_type.startswith('text/html')
                text = await response.text()
                assert text == html_content

    finally:
        await server.stop()
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_web_server_multiple_requests():
    """Test web server with multiple requests."""
    server = WebServer(port=9995, content="Test", bind_address='127.0.0.1')

    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.5)

    try:
        async with aiohttp.ClientSession() as session:
            # Make multiple requests
            for i in range(5):
                async with session.get(f'http://127.0.0.1:9995/path{i}') as response:
                    assert response.status == 200
                    text = await response.text()
                    assert text == "Test"

    finally:
        await server.stop()
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
