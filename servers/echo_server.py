"""Echo server implementation using asyncio."""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EchoServer:
    """TCP Echo server that returns received data."""

    def __init__(self, port: int, bind_address: str = '0.0.0.0'):
        """Initialize echo server.

        Args:
            port: Port to listen on
            bind_address: Address to bind to (default: 0.0.0.0)
        """
        self.port = port
        self.bind_address = bind_address
        self.server: Optional[asyncio.Server] = None
        self._running = False

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Handle incoming client connection.

        Args:
            reader: Stream reader for incoming data
            writer: Stream writer for outgoing data
        """
        addr = writer.get_extra_info('peername')
        logger.info(f"Echo server on port {self.port}: New connection from {addr}")

        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break

                message = data.decode('utf-8', errors='replace')
                logger.debug(f"Echo server on port {self.port}: Received from {addr}: {message[:50]}")

                # Echo back the data
                writer.write(data)
                await writer.drain()

        except asyncio.CancelledError:
            logger.info(f"Echo server on port {self.port}: Connection from {addr} cancelled")
        except Exception as e:
            logger.error(f"Echo server on port {self.port}: Error handling client {addr}: {e}")
        finally:
            logger.info(f"Echo server on port {self.port}: Closing connection from {addr}")
            writer.close()
            await writer.wait_closed()

    async def start(self) -> None:
        """Start the echo server."""
        try:
            self.server = await asyncio.start_server(
                self.handle_client,
                self.bind_address,
                self.port
            )
            self._running = True

            addr = self.server.sockets[0].getsockname()
            logger.info(f"Echo server started on {addr[0]}:{addr[1]}")

            async with self.server:
                await self.server.serve_forever()

        except OSError as e:
            logger.error(f"Echo server failed to start on {self.bind_address}:{self.port}: {e}")
            raise
        except asyncio.CancelledError:
            logger.info(f"Echo server on port {self.port} shutting down")
        finally:
            self._running = False

    async def stop(self) -> None:
        """Stop the echo server."""
        if self.server:
            logger.info(f"Stopping echo server on port {self.port}")
            self.server.close()
            await self.server.wait_closed()
            self._running = False

    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running
