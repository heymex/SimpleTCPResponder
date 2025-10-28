#!/usr/bin/env python3
"""Main entry point for SimpleTCPResponder."""

import argparse
import asyncio
import logging
import signal
import socket
import sys
from typing import List, Union

from config import Config, get_default_config_path
from servers.echo_server import EchoServer
from servers.web_server import WebServer


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def get_active_ip_addresses() -> List[str]:
    """Get list of active IP addresses on this system, excluding localhost.

    Returns:
        List of IP addresses
    """
    ip_addresses = []

    try:
        # Get hostname
        hostname = socket.gethostname()

        # Get all IP addresses associated with the hostname
        addr_info = socket.getaddrinfo(hostname, None, socket.AF_INET)

        for info in addr_info:
            ip = info[4][0]
            # Exclude localhost addresses
            if not ip.startswith('127.'):
                if ip not in ip_addresses:
                    ip_addresses.append(ip)

        # Also try to get IPs by connecting to an external address
        # This helps find the primary network interface IP
        try:
            # Create a socket and connect to a public DNS server
            # This doesn't actually send data, just determines routing
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            primary_ip = s.getsockname()[0]
            s.close()

            if primary_ip and not primary_ip.startswith('127.') and primary_ip not in ip_addresses:
                ip_addresses.insert(0, primary_ip)  # Put primary IP first
        except Exception:
            pass  # If this fails, we'll just use what we got from getaddrinfo

    except Exception as e:
        logger.debug(f"Error getting IP addresses: {e}")

    return ip_addresses


class ServerManager:
    """Manages multiple server instances."""

    def __init__(self, config: Config):
        """Initialize server manager.

        Args:
            config: Configuration object
        """
        self.config = config
        self.servers: List[Union[EchoServer, WebServer]] = []
        self.tasks: List[asyncio.Task] = []
        self._shutdown = False

    def create_servers(self) -> None:
        """Create server instances from configuration."""
        for server_config in self.config.servers:
            if server_config.type == 'echo':
                server = EchoServer(
                    port=server_config.port,
                    bind_address=server_config.bind_address
                )
            elif server_config.type == 'web':
                server = WebServer(
                    port=server_config.port,
                    content=server_config.content,
                    bind_address=server_config.bind_address
                )
            else:
                logger.error(f"Unknown server type: {server_config.type}")
                continue

            self.servers.append(server)

        logger.info(f"Created {len(self.servers)} server instance(s)")

    async def start_all(self) -> None:
        """Start all configured servers."""
        if not self.servers:
            logger.error("No servers configured")
            return

        logger.info(f"Starting {len(self.servers)} server(s)...")

        # Start each server in its own task
        for server in self.servers:
            task = asyncio.create_task(server.start())
            self.tasks.append(task)

        # Log server summary
        print("\n" + "="*60)
        print("SimpleTCPResponder - Active Servers")
        print("="*60)

        # Check if any server is bound to all interfaces
        has_wildcard_bind = any(
            server.bind_address == '0.0.0.0' for server in self.servers
        )

        # Get active IP addresses if we have wildcard binds
        active_ips = []
        if has_wildcard_bind:
            active_ips = get_active_ip_addresses()

        for server in self.servers:
            server_type = server.__class__.__name__.replace('Server', '')
            print(f"  {server_type.upper()}: {server.bind_address}:{server.port}")

        # Display active IP addresses if binding to all interfaces
        if active_ips:
            print("="*60)
            print("Active IP addresses on this system:")
            for ip in active_ips:
                print(f"  {ip}")
            print()
            print("Servers bound to 0.0.0.0 are accessible via any of the")
            print("above IP addresses.")

        print("="*60)
        print("Press Ctrl+C to stop all servers")
        print("="*60 + "\n")

        # Wait for all tasks
        try:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        except asyncio.CancelledError:
            logger.info("Server tasks cancelled")

    async def stop_all(self) -> None:
        """Stop all running servers."""
        if self._shutdown:
            return

        self._shutdown = True
        logger.info("Shutting down all servers...")

        # Stop all servers
        stop_tasks = []
        for server in self.servers:
            if hasattr(server, 'stop'):
                stop_tasks.append(server.stop())

        if stop_tasks:
            await asyncio.gather(*stop_tasks, return_exceptions=True)

        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()

        logger.info("All servers stopped")

    def setup_signal_handlers(self, loop: asyncio.AbstractEventLoop) -> None:
        """Set up signal handlers for graceful shutdown.

        Args:
            loop: Event loop
        """
        def signal_handler(sig):
            logger.info(f"Received signal {sig}")
            loop.create_task(self.stop_all())

        # Handle SIGINT (Ctrl+C) and SIGTERM
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda s=sig: signal_handler(s))


async def run_servers(config: Config) -> None:
    """Run all configured servers.

    Args:
        config: Configuration object
    """
    manager = ServerManager(config)
    manager.create_servers()

    if not manager.servers:
        logger.error("No servers to start")
        sys.exit(1)

    # Set up signal handlers for graceful shutdown
    loop = asyncio.get_event_loop()
    manager.setup_signal_handlers(loop)

    try:
        await manager.start_all()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        await manager.stop_all()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='SimpleTCPResponder - Network diagnostic server tool'
    )
    parser.add_argument(
        '--config',
        '-c',
        help='Configuration file path (default: server_config.json)',
        default=get_default_config_path()
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load configuration
    try:
        config = Config.load(args.config)
        logger.info(f"Loaded configuration from {args.config}")
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {args.config}")
        logger.error("Run 'python setup.py' to create a configuration file")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        sys.exit(1)

    # Run servers
    try:
        asyncio.run(run_servers(config))
    except KeyboardInterrupt:
        logger.info("Shutdown complete")


if __name__ == '__main__':
    main()
