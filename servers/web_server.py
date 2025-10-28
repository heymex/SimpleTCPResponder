"""Web server implementation using aiohttp."""

import asyncio
import logging
from typing import Optional
from aiohttp import web

logger = logging.getLogger(__name__)


class WebServer:
    """HTTP server that serves configurable content."""

    def __init__(self, port: int, content: str, bind_address: str = '0.0.0.0'):
        """Initialize web server.

        Args:
            port: Port to listen on
            content: Content to serve (HTML, text, etc.)
            bind_address: Address to bind to (default: 0.0.0.0)
        """
        self.port = port
        self.content = content
        self.bind_address = bind_address
        self.app: Optional[web.Application] = None
        self.runner: Optional[web.AppRunner] = None
        self._running = False

    async def handle_request(self, request: web.Request) -> web.Response:
        """Handle HTTP request.

        Args:
            request: Incoming HTTP request

        Returns:
            HTTP response with configured content
        """
        client_ip = request.remote
        path = request.path
        method = request.method

        logger.info(f"Web server on port {self.port}: {method} {path} from {client_ip}")

        # Determine content type based on content
        if self.content.strip().startswith('<!DOCTYPE') or self.content.strip().startswith('<html'):
            content_type = 'text/html'
        else:
            content_type = 'text/plain'

        return web.Response(
            text=self.content,
            content_type=content_type,
            headers={
                'Server': 'SimpleTCPResponder',
                'X-Served-Port': str(self.port)
            }
        )

    async def start(self) -> None:
        """Start the web server."""
        try:
            self.app = web.Application()
            self.app.router.add_route('*', '/{tail:.*}', self.handle_request)

            self.runner = web.AppRunner(self.app)
            await self.runner.setup()

            site = web.TCPSite(self.runner, self.bind_address, self.port)
            await site.start()

            self._running = True
            logger.info(f"Web server started on {self.bind_address}:{self.port}")

            # Keep the server running
            while self._running:
                await asyncio.sleep(1)

        except OSError as e:
            logger.error(f"Web server failed to start on {self.bind_address}:{self.port}: {e}")
            raise
        except asyncio.CancelledError:
            logger.info(f"Web server on port {self.port} shutting down")
        finally:
            await self.stop()

    async def stop(self) -> None:
        """Stop the web server."""
        if self.runner:
            logger.info(f"Stopping web server on port {self.port}")
            await self.runner.cleanup()
            self._running = False

    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running
