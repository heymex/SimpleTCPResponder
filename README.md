# SimpleTCPResponder

A Python-based network diagnostic tool that creates configurable TCP servers for troubleshooting network connections.

## Overview

SimpleTCPResponder provides a quick and easy way to stand up one or more diagnostic servers on specified ports. Perfect for testing network connectivity, debugging firewall rules, or validating application behavior.

## Features

- **Two Server Types:**
  - **Echo Server**: Returns all received data back to the client
  - **Web Server**: Serves customizable HTTP content

- **Flexible Configuration:**
  - Support up to 10 concurrent servers
  - Individual port configuration or sequential port ranges
  - Mix echo and web servers in the same configuration
  - Reusable configuration files

- **Easy Setup:**
  - Interactive setup wizard
  - Quick setup mode for multiple servers
  - JSON-based configuration

- **Production Ready:**
  - Async architecture using Python asyncio
  - Graceful shutdown handling
  - Comprehensive logging
  - Full test suite

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd SimpleTCPResponder

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Create Configuration

Run the interactive setup:

```bash
python setup.py
```

Choose from two setup modes:
- **Individual Configuration**: Customize each server separately
- **Quick Setup**: Create multiple servers on sequential ports

### 2. Start Servers

```bash
python main.py
```

Your servers are now running! Press Ctrl+C to stop.

### 3. Test Your Servers

**Test Echo Server:**
```bash
telnet localhost 8000
# or
nc localhost 8000
```

**Test Web Server:**
```bash
curl http://localhost:8080
# or open in your browser
```

## Usage Examples

### Example 1: Single Echo Server

```bash
python setup.py
# Select: Individual configuration
# Servers: 1
# Type: Echo
# Port: 9000
```

Test it:
```bash
echo "Hello" | nc localhost 9000
```

### Example 2: Multiple Web Servers

```bash
python setup.py
# Select: Quick setup
# Servers: 3
# Type: Web
# Starting port: 8080
```

This creates web servers on ports 8080, 8081, and 8082.

### Example 3: Mixed Configuration

Configure different server types on custom ports:
- Echo server on port 9000
- Web server on port 8080 with custom HTML
- Web server on port 8081 with different content

## Command Reference

### Setup Script

```bash
python setup.py                          # Interactive setup
python setup.py --use-prefs config.json  # Reuse existing config
python setup.py --output my_config.json  # Save to custom path
```

### Main Application

```bash
python main.py                           # Use default config
python main.py --config my_config.json   # Use custom config
python main.py --verbose                 # Enable debug logging
```

### Testing

```bash
pytest                                    # Run all tests
pytest --cov=. --cov-report=term-missing # Run with coverage
pytest tests/test_echo_server.py         # Run specific test
```

## Configuration File Format

Configuration is stored as JSON:

```json
{
  "servers": [
    {
      "type": "echo",
      "port": 9000,
      "bind_address": "0.0.0.0"
    },
    {
      "type": "web",
      "port": 8080,
      "content": "<html>...</html>",
      "bind_address": "0.0.0.0"
    }
  ]
}
```

## Use Cases

- **Network Troubleshooting**: Test if ports are accessible
- **Firewall Testing**: Verify firewall rules and port forwarding
- **Application Testing**: Mock backend services during development
- **Load Balancer Testing**: Create multiple endpoints for testing
- **Network Diagnostics**: Quick connectivity verification

## Requirements

- Python 3.8 or higher
- aiohttp (for web servers)
- pytest (for testing)

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.