"""Tests for configuration module."""

import os
import tempfile
import pytest
from config import Config, ServerConfig


def test_server_config_validation():
    """Test ServerConfig validation."""
    # Valid echo server
    server = ServerConfig(type='echo', port=8000)
    server.validate()  # Should not raise

    # Valid web server
    server = ServerConfig(type='web', port=8080, content='Hello')
    server.validate()  # Should not raise

    # Invalid type
    server = ServerConfig(type='invalid', port=8000)
    with pytest.raises(ValueError, match="Invalid server type"):
        server.validate()

    # Invalid port
    server = ServerConfig(type='echo', port=70000)
    with pytest.raises(ValueError, match="Invalid port"):
        server.validate()

    # Web server without content
    server = ServerConfig(type='web', port=8080)
    with pytest.raises(ValueError, match="Web servers must have content"):
        server.validate()


def test_config_validation():
    """Test Config validation."""
    # Valid config
    config = Config(servers=[
        ServerConfig(type='echo', port=8000),
        ServerConfig(type='web', port=8080, content='Hello')
    ])
    config.validate()  # Should not raise

    # No servers
    config = Config(servers=[])
    with pytest.raises(ValueError, match="At least one server"):
        config.validate()

    # Too many servers
    servers = [ServerConfig(type='echo', port=8000 + i) for i in range(11)]
    config = Config(servers=servers)
    with pytest.raises(ValueError, match="Maximum of 10 servers"):
        config.validate()

    # Duplicate ports
    config = Config(servers=[
        ServerConfig(type='echo', port=8000),
        ServerConfig(type='echo', port=8000)
    ])
    with pytest.raises(ValueError, match="Port 8000 is used by multiple servers"):
        config.validate()


def test_config_save_load():
    """Test saving and loading configuration."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name

    try:
        # Create and save config
        original_config = Config(servers=[
            ServerConfig(type='echo', port=8000),
            ServerConfig(type='web', port=8080, content='Test content')
        ])
        original_config.save(temp_path)

        # Load config
        loaded_config = Config.load(temp_path)

        # Verify
        assert len(loaded_config.servers) == 2
        assert loaded_config.servers[0].type == 'echo'
        assert loaded_config.servers[0].port == 8000
        assert loaded_config.servers[1].type == 'web'
        assert loaded_config.servers[1].port == 8080
        assert loaded_config.servers[1].content == 'Test content'

    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_config_to_from_dict():
    """Test dictionary conversion."""
    config = Config(servers=[
        ServerConfig(type='echo', port=8000, bind_address='127.0.0.1')
    ])

    # Convert to dict
    config_dict = config.to_dict()
    assert 'servers' in config_dict
    assert len(config_dict['servers']) == 1
    assert config_dict['servers'][0]['type'] == 'echo'

    # Convert back to Config
    restored_config = Config.from_dict(config_dict)
    assert len(restored_config.servers) == 1
    assert restored_config.servers[0].type == 'echo'
    assert restored_config.servers[0].port == 8000
    assert restored_config.servers[0].bind_address == '127.0.0.1'
