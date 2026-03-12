# Perplexity Subscription MCP

## Project Overview

PyPI package: `perplexity-subscription-mcp` (https://pypi.org/project/perplexity-subscription-mcp/)
Import name: `perplexity_subscription_mcp`
Console script: `perplexity-mcp`

Unofficial MCP server + Python client wrapping Perplexity AI's **web interface** using browser session cookies. No API key needed — uses the user's existing Perplexity subscription.

## Project Structure

```
perplexity_subscription_mcp/   # Published package (PyPI)
├── __init__.py                # Exports: Client, normalize_cookies, __version__
├── __main__.py                # python -m support
├── client.py                  # Core Client class (curl_cffi, browser impersonation)
└── server.py                  # FastMCP server (search, follow_up, list_threads, get_thread)
api/                           # REST API (NOT published, local dev only)
├── main.py                    # FastAPI app — imports from perplexity_subscription_mcp
└── utils.py                   # Response extraction + logging helpers
```

## Key Architecture

- **client.py**: `Client` class uses `curl_cffi` with Chrome TLS fingerprint impersonation to call Perplexity's internal SSE API (`/rest/sse/perplexity_ask`). Authenticates via browser cookies.
- **server.py**: `FastMCP` server exposes 4 tools over stdio transport. Lazy-loads the Client. Has its own `extract_response()` to parse Perplexity's block-based response format.
- **Cookie resolution** (in `get_client()`): `PERPLEXITY_COOKIES_PATH` env → `PERPLEXITY_COOKIES` env (inline JSON) → `~/.config/perplexity/cookies.json` → `./perplexity_cookies.json`
- Two cookie formats accepted: flat dict `{"name": "value"}` or Cookie-Editor array `[{"name": "...", "value": "..."}]`

## Build & Publish

- Build system: **hatchling**
- Package manager: **uv**
- Python: `>=3.10`

### CI/CD (automatic)

Every push to `main`/`master` triggers `.github/workflows/publish.yml`:
1. Auto-bumps patch version (0.1.1 → 0.1.2)
2. Updates version in `pyproject.toml` and `__init__.py`
3. Commits `v0.1.2 [skip ci]` and creates git tag
4. Builds and publishes to PyPI

The `[skip ci]` in the version bump commit prevents infinite loops. PyPI token is stored as `UV_PUBLISH_TOKEN` GitHub Actions secret.

**To set major/minor version**: manually edit version in `pyproject.toml` + `__init__.py`, push — CI will bump patch from there.

### Manual (local)

```bash
rm -rf dist && uv build
uvx twine check dist/*
uv publish  # uses UV_PUBLISH_TOKEN from ~/.zshrc
```

## Dependencies

**Core** (published): `curl-cffi`, `mcp`
**Optional** `[api]` (local only): `fastapi`, `uvicorn`

## MCP Config (how users run it)

Users don't pip install — they use `uvx` in their MCP config:
```json
{
  "command": "uvx",
  "args": ["--from", "perplexity-subscription-mcp", "perplexity-mcp"],
  "env": {
    "PERPLEXITY_COOKIES_PATH": "/absolute/path/to/cookies.json"
  }
}
```

## Important Notes

- Perplexity's internal API uses mode names with spaces: `"deep research"` not `"deep_research"`. The MCP server normalizes underscores to spaces.
- Model mappings (e.g. `"claude 3.7 sonnet"` → `"claude2"`) are hardcoded in `client.py`. These may need updating when Perplexity changes their internal API.
- The `api/main.py` mode enum is outdated (`writing`, `coding`, `research` instead of `pro`, `reasoning`, `deep research`) — known bug, not published so low priority.
- Cookies expire periodically. The `__Secure-next-auth.session-token` is the essential one.
