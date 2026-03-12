"""Perplexity AI web wrapper - uses your subscription, not the API."""

from perplexity_subscription_mcp.client import Client, normalize_cookies

__all__ = ["Client", "normalize_cookies"]
__version__ = "0.1.1"
