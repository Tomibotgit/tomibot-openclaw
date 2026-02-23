"""
Hyvor Relay Email Skill
一个完整的 Hyvor Relay 自托管邮箱服务 Python 客户端
"""

from .client import (
    HyvorRelayClient,
    HyvorRelayError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    EmailAddress,
    Attachment,
    EmailRequest,
    create_client
)

__version__ = "1.0.0"
__author__ = "TomiBot"
__email__ = "tomibot@163.com"

__all__ = [
    "HyvorRelayClient",
    "HyvorRelayError",
    "AuthenticationError",
    "ValidationError",
    "RateLimitError",
    "EmailAddress",
    "Attachment",
    "EmailRequest",
    "create_client",
]