"""Configuration module for SimpleTCPResponder."""

import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class ServerConfig:
    """Configuration for a single server."""
    type: str  # 'echo' or 'web'
    port: int
    content: Optional[str] = None  # For web servers: content to serve
    bind_address: str = '0.0.0.0'

    def validate(self) -> None:
        """Validate server configuration."""
        if self.type not in ['echo', 'web']:
            raise ValueError(f"Invalid server type: {self.type}. Must be 'echo' or 'web'")

        if not isinstance(self.port, int) or self.port < 1 or self.port > 65535:
            raise ValueError(f"Invalid port: {self.port}. Must be between 1 and 65535")

        if self.type == 'web' and not self.content:
            raise ValueError("Web servers must have content specified")


@dataclass
class Config:
    """Main configuration container."""
    servers: List[ServerConfig]

    def validate(self) -> None:
        """Validate entire configuration."""
        if not self.servers:
            raise ValueError("At least one server must be configured")

        if len(self.servers) > 10:
            raise ValueError("Maximum of 10 servers allowed")

        # Validate each server and check for port conflicts
        ports = []
        for server in self.servers:
            server.validate()
            if server.port in ports:
                raise ValueError(f"Port {server.port} is used by multiple servers")
            ports.append(server.port)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'servers': [asdict(s) for s in self.servers]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create configuration from dictionary."""
        servers = [ServerConfig(**s) for s in data.get('servers', [])]
        return cls(servers=servers)

    def save(self, filepath: str) -> None:
        """Save configuration to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> 'Config':
        """Load configuration from JSON file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Configuration file not found: {filepath}")

        with open(filepath, 'r') as f:
            data = json.load(f)

        config = cls.from_dict(data)
        config.validate()
        return config


def get_default_config_path() -> str:
    """Get the default configuration file path."""
    return os.path.join(os.getcwd(), 'server_config.json')
