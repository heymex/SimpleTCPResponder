# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SimpleTCPResponder is a diagnostic network tool written in Python that creates TCP servers for troubleshooting network connections. It supports two types of servers:

1. **Echo Server**: Echoes back received data
2. **Web Server**: Serves HTTP content (can display different content on different ports)

The tool is designed for network diagnostics and testing, allowing users to quickly stand up one or multiple servers on specified ports.

## Project Requirements

Key requirements from .project-profile:
- Python-based implementation
- Support up to 10 concurrent servers
- Each server can be either web or echo type
- Ports can be user-specified or sequential starting from a base port
- Interactive setup script that creates/loads preference files
- Preference file reuse capability for quick setup

## Development Commands

### Running the Application
```bash
# Run the setup script (interactive configuration)
python setup.py

# Run with existing preferences
python setup.py --use-prefs [preferences_file]

# Run the server(s)
python main.py [--config preferences_file]
```

### Testing
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_echo_server.py

# Run with coverage
python -m pytest --cov=. --cov-report=term-missing
```

### Testing Servers Manually
```bash
# Test echo server
telnet localhost <port>
# or
nc localhost <port>

# Test web server
curl http://localhost:<port>
# or visit in browser
```

## Architecture

### Core Components

**Server Types** (to be implemented in `servers/`):
- `echo_server.py`: TCP echo server that returns received data
- `web_server.py`: HTTP server with configurable content per port

**Configuration** (to be implemented):
- `setup.py`: Interactive setup script that creates preference files
- `config.py`: Configuration loader/validator for preference files
- Preference files stored as JSON/YAML with server definitions

**Main Application**:
- `main.py`: Entry point that reads preferences and spawns server instances
- Multi-threaded or async architecture to handle multiple concurrent servers

### Server Lifecycle

1. User runs setup script (or uses existing preferences)
2. Setup creates/loads preference file with server configurations
3. Main script reads preferences and validates configuration
4. Each server spawned in separate thread/async task
5. Servers run concurrently until interrupted
6. Graceful shutdown handling for all servers

### Configuration Format

Preference files should define:
- Server type (echo or web)
- Port number
- For web servers: content to serve (file path or inline content)
- Optional: bind address (default 0.0.0.0 or localhost)

## Implementation Notes

- Use Python 3.8+ for compatibility
- Consider `asyncio` for concurrent server handling
- For web servers, consider simple HTTP server (http.server) or lightweight framework
- Echo servers can use raw sockets or asyncio streams
- Handle port conflicts gracefully with clear error messages
- Implement proper signal handling (SIGINT, SIGTERM) for clean shutdown
- Log server start/stop events and connections for diagnostics
