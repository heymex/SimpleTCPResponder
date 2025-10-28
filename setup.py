#!/usr/bin/env python3
"""Interactive setup script for SimpleTCPResponder."""

import argparse
import os
import sys
from typing import List

from config import Config, ServerConfig, get_default_config_path


def get_yes_no(prompt: str, default: bool = False) -> bool:
    """Get yes/no input from user.

    Args:
        prompt: Question to ask
        default: Default value if user just presses enter

    Returns:
        True for yes, False for no
    """
    default_str = 'Y/n' if default else 'y/N'
    while True:
        response = input(f"{prompt} [{default_str}]: ").strip().lower()
        if not response:
            return default
        if response in ['y', 'yes']:
            return True
        if response in ['n', 'no']:
            return False
        print("Please answer 'y' or 'n'")


def get_number(prompt: str, min_val: int = None, max_val: int = None, default: int = None) -> int:
    """Get numeric input from user.

    Args:
        prompt: Question to ask
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        default: Default value if user just presses enter

    Returns:
        Valid integer
    """
    while True:
        if default is not None:
            response = input(f"{prompt} [default: {default}]: ").strip()
        else:
            response = input(f"{prompt}: ").strip()

        if not response and default is not None:
            return default

        try:
            value = int(response)
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"Value must be at most {max_val}")
                continue
            return value
        except ValueError:
            print("Please enter a valid number")


def get_server_type() -> str:
    """Get server type from user.

    Returns:
        'echo' or 'web'
    """
    while True:
        print("\nServer types:")
        print("  1. Echo server (echoes back received data)")
        print("  2. Web server (serves HTTP content)")
        choice = input("Select server type [1-2]: ").strip()

        if choice == '1':
            return 'echo'
        elif choice == '2':
            return 'web'
        else:
            print("Please enter 1 or 2")


def configure_server(server_num: int, used_ports: List[int]) -> ServerConfig:
    """Configure a single server.

    Args:
        server_num: Server number (for display)
        used_ports: List of already used ports

    Returns:
        Configured ServerConfig
    """
    print(f"\n{'='*60}")
    print(f"Configuring Server {server_num}")
    print('='*60)

    server_type = get_server_type()

    while True:
        port = get_number("Enter port number", min_val=1, max_val=65535)
        if port in used_ports:
            print(f"Port {port} is already in use by another server. Choose a different port.")
        else:
            break

    bind_address = input("Enter bind address [default: 0.0.0.0]: ").strip() or '0.0.0.0'

    content = None
    if server_type == 'web':
        print("\nWeb server content options:")
        print("  1. Enter custom text/HTML")
        print("  2. Use default HTML page")
        choice = input("Select option [1-2]: ").strip()

        if choice == '1':
            print("\nEnter content (press Ctrl+D or Ctrl+Z when done):")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass
            content = '\n'.join(lines)
        else:
            content = f"""<!DOCTYPE html>
<html>
<head>
    <title>SimpleTCPResponder - Port {port}</title>
</head>
<body>
    <h1>SimpleTCPResponder</h1>
    <p>This is a diagnostic web server running on port {port}.</p>
    <p>Server type: {server_type}</p>
    <p>Timestamp: {{timestamp}}</p>
</body>
</html>"""

    return ServerConfig(
        type=server_type,
        port=port,
        content=content,
        bind_address=bind_address
    )


def setup_sequential_ports(start_port: int, count: int, server_type: str) -> List[ServerConfig]:
    """Set up multiple servers on sequential ports.

    Args:
        start_port: Starting port number
        count: Number of servers
        server_type: Type of server ('echo' or 'web')

    Returns:
        List of ServerConfig objects
    """
    servers = []
    for i in range(count):
        port = start_port + i
        content = None
        if server_type == 'web':
            content = f"""<!DOCTYPE html>
<html>
<head>
    <title>SimpleTCPResponder - Port {port}</title>
</head>
<body>
    <h1>SimpleTCPResponder - Server {i+1}</h1>
    <p>This is a diagnostic web server running on port {port}.</p>
</body>
</html>"""

        servers.append(ServerConfig(
            type=server_type,
            port=port,
            content=content
        ))

    return servers


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description='SimpleTCPResponder Setup')
    parser.add_argument('--use-prefs', help='Use existing preferences file')
    parser.add_argument('--output', '-o', help='Output configuration file path')
    args = parser.parse_args()

    config_path = args.output or get_default_config_path()

    print("="*60)
    print("SimpleTCPResponder Setup")
    print("="*60)

    # Check for existing configuration
    if args.use_prefs:
        if os.path.exists(args.use_prefs):
            print(f"\nUsing existing configuration: {args.use_prefs}")
            try:
                config = Config.load(args.use_prefs)
                print(f"\nLoaded {len(config.servers)} server(s):")
                for i, server in enumerate(config.servers, 1):
                    print(f"  {i}. {server.type.upper()} server on port {server.port}")
                return
            except Exception as e:
                print(f"Error loading configuration: {e}")
                sys.exit(1)
        else:
            print(f"Configuration file not found: {args.use_prefs}")
            sys.exit(1)

    if not args.use_prefs and os.path.exists(config_path):
        if get_yes_no(f"\nConfiguration file already exists at {config_path}. Reuse it?", default=True):
            try:
                config = Config.load(config_path)
                print(f"\nUsing existing configuration with {len(config.servers)} server(s)")
                return
            except Exception as e:
                print(f"Error loading configuration: {e}")
                print("Creating new configuration...\n")

    # Setup mode
    print("\nSetup modes:")
    print("  1. Configure servers individually")
    print("  2. Quick setup - multiple servers on sequential ports")
    mode = input("Select mode [1-2]: ").strip()

    servers = []

    if mode == '2':
        # Quick setup
        num_servers = get_number("\nHow many servers?", min_val=1, max_val=10)
        server_type = get_server_type()
        start_port = get_number("Starting port number", min_val=1, max_val=65535-num_servers)

        servers = setup_sequential_ports(start_port, num_servers, server_type)
        print(f"\nCreated {num_servers} {server_type} server(s) on ports {start_port}-{start_port+num_servers-1}")

    else:
        # Individual configuration
        num_servers = get_number("\nHow many servers do you want to configure?", min_val=1, max_val=10)

        used_ports = []
        for i in range(num_servers):
            server = configure_server(i + 1, used_ports)
            servers.append(server)
            used_ports.append(server.port)

    # Create and save configuration
    config = Config(servers=servers)

    try:
        config.validate()
    except ValueError as e:
        print(f"\nConfiguration error: {e}")
        sys.exit(1)

    config.save(config_path)
    print(f"\n{'='*60}")
    print(f"Configuration saved to: {config_path}")
    print(f"Total servers configured: {len(servers)}")
    print(f"\nTo start the servers, run:")
    print(f"  python main.py")
    print(f"  # or")
    print(f"  python main.py --config {config_path}")
    print('='*60)


if __name__ == '__main__':
    main()
