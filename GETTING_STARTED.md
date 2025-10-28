# Getting Started with SimpleTCPResponder

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Step 1: Run Setup

Create your server configuration interactively:

```bash
python setup.py
```

You'll be prompted to:
- Choose between individual or quick setup mode
- Select server types (echo or web)
- Specify ports
- Configure content (for web servers)

### Step 2: Start Servers

Once configured, start all servers:

```bash
python main.py
```

Or specify a custom config file:

```bash
python main.py --config my_config.json
```

### Step 3: Test Your Servers

**Echo Server:**
```bash
# Using telnet
telnet localhost 8000

# Using netcat
nc localhost 8000

# Type anything and it will echo back
```

**Web Server:**
```bash
# Using curl
curl http://localhost:8080

# Or open in browser
open http://localhost:8080
```

## Examples

### Quick Setup - Multiple Echo Servers

```bash
python setup.py
# Select: 2 (Quick setup)
# Enter: 3 (number of servers)
# Select: 1 (echo server)
# Enter: 9000 (starting port)
```

This creates 3 echo servers on ports 9000, 9001, 9002.

### Individual Setup - Mixed Servers

```bash
python setup.py
# Select: 1 (Configure individually)
# Enter: 2 (number of servers)
# Configure first server as echo on port 8000
# Configure second server as web on port 8080
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_echo_server.py
```

## Troubleshooting

**Port already in use:**
- Stop other services using the port, or
- Choose a different port in setup

**Configuration file not found:**
- Run `python setup.py` first to create a configuration

**Permission denied:**
- Use ports above 1024 (ports 1-1024 require root)

## Advanced Usage

**Verbose logging:**
```bash
python main.py --verbose
```

**Custom bind address:**
During setup, specify a bind address (default is 0.0.0.0 for all interfaces)

**Reuse existing configuration:**
```bash
python setup.py --use-prefs server_config.json
```
