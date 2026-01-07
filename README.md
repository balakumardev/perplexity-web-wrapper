# Perplexity Web Wrapper & MCP Server

Unofficial Python wrapper for Perplexity AI's web interface, providing both a REST API and MCP (Model Context Protocol) server for integration with coding agents.

## Overview

This project enables programmatic access to Perplexity AI through:

- **Python Library**: Direct client for searching and managing threads
- **REST API**: FastAPI server with synchronous and streaming endpoints
- **MCP Server**: Model Context Protocol integration for AI coding assistants

## Features

### Search Modes

| Mode | Description | Pro Subscription Required |
|------|-------------|--------------------------|
| `auto` | Quick answers using Perplexity's default model | No |
| `pro` | Enhanced search with model selection | Yes |
| `reasoning` | Deep reasoning with thinking models | Yes |
| `deep_research` | Comprehensive multi-step research | Yes |

### Available Models

| Mode | Available Models |
|------|-----------------|
| `auto` | Default (turbo) |
| `pro` | Default, `sonar`, `gpt-4.5`, `gpt-4o`, `claude 3.7 sonnet`, `gemini 2.0 flash`, `grok-2` |
| `reasoning` | Default, `r1`, `o3-mini`, `claude 3.7 sonnet` |
| `deep_research` | Default (alpha) |

### Sources

- `web` - General web search (default)
- `scholar` - Academic papers and research
- `social` - Social media content

### Additional Features

- **Token-efficient `answer_only` mode**: Returns only the answer and `backend_uuid`, reducing response size
- **Follow-up conversations**: Continue discussions using `backend_uuid` from previous responses
- **Thread management**: List and retrieve past conversation threads
- **Incognito mode**: Search without saving to history
- **File uploads**: Attach files to queries (Pro subscription)

## Installation

### Requirements

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/perplexity-web-wrapper.git
   cd perplexity-web-wrapper
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Set up your Perplexity cookies (see [Cookie Setup Guide](#cookie-setup-guide))

## MCP Server Setup for Coding Agents

The MCP server provides tools for AI coding assistants to search Perplexity AI directly.

### Claude Code CLI

```bash
claude mcp add --transport stdio perplexity --scope user -- /path/to/perplexity-web-wrapper/.venv/bin/python -m mcp_server.server
```

Or using the installed console script:
```bash
claude mcp add --transport stdio perplexity --scope user -- /path/to/perplexity-web-wrapper/.venv/bin/perplexity-mcp
```

### Cursor IDE

Configuration file: `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "perplexity": {
      "command": "/path/to/perplexity-web-wrapper/.venv/bin/python",
      "args": ["-m", "mcp_server.server"],
      "env": {}
    }
  }
}
```

### Windsurf IDE

Configuration file: `~/.codeium/windsurf/mcp_config.json`

```json
{
  "mcpServers": {
    "perplexity": {
      "command": "/path/to/perplexity-web-wrapper/.venv/bin/python",
      "args": ["-m", "mcp_server.server"],
      "env": {}
    }
  }
}
```

### OpenAI Codex CLI

Configuration file: `~/.codex/config.toml`

```toml
[mcp_servers.perplexity]
command = "/path/to/perplexity-web-wrapper/.venv/bin/python"
args = ["-m", "mcp_server.server"]
```

### VS Code with Continue Extension

Add to your Continue configuration (`.continue/config.json` or VS Code settings):

```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "/path/to/perplexity-web-wrapper/.venv/bin/python",
          "args": ["-m", "mcp_server.server"]
        }
      }
    ]
  }
}
```

### VS Code with Cline Extension

Add to Cline's MCP settings in VS Code:

```json
{
  "cline.mcpServers": {
    "perplexity": {
      "command": "/path/to/perplexity-web-wrapper/.venv/bin/python",
      "args": ["-m", "mcp_server.server"]
    }
  }
}
```

## MCP Tools Reference

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `search` | Search Perplexity AI | `query` (required), `mode`, `model`, `sources`, `answer_only`, `language`, `incognito` |
| `follow_up` | Continue a previous conversation | `query` (required), `backend_uuid` (required), `mode`, `model`, `answer_only` |
| `list_threads` | List conversation threads | `limit`, `search_term` |
| `get_thread` | Get thread details by slug | `slug` (required) |

### Tool Details

#### search

Search Perplexity AI with various modes and models.

```python
# Example response with answer_only=True (default)
{
    "answer": "Perplexity AI is an AI-powered search engine...",
    "backend_uuid": "abc-123-def-456"
}

# Example response with answer_only=False
{
    "answer": "Perplexity AI is an AI-powered search engine...",
    "backend_uuid": "abc-123-def-456",
    "sources": ["https://example.com/article1", "https://example.com/article2"],
    "related_queries": ["How does Perplexity AI work?", "Perplexity AI vs ChatGPT"]
}
```

#### follow_up

Continue a conversation using the `backend_uuid` from a previous response.

```python
# Use the backend_uuid from search response
follow_up(query="Can you elaborate on that?", backend_uuid="abc-123-def-456")
```

#### list_threads

Retrieve a list of conversation threads.

```python
# Returns list of threads with metadata (title, slug, timestamps)
list_threads(limit=10, search_term="python")
```

#### get_thread

Get full details of a specific thread including all messages.

```python
# Use the slug from list_threads
get_thread(slug="thread-slug-here")
```

## REST API (Optional)

Start the API server for HTTP access:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Access the interactive API documentation at `http://localhost:8000/docs`

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/query_sync` | GET | Synchronous search, returns complete response |
| `/api/query_async` | GET | Server-Sent Events (SSE) streaming response |
| `/api/threads` | GET | List conversation threads |
| `/api/threads/{slug}` | GET | Get thread details by slug |

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `q` | string | required | Search query |
| `mode` | string | `auto` | Search mode: `auto`, `pro`, `reasoning`, `deep_research` |
| `model` | string | null | Specific model (depends on mode) |
| `sources` | string | `web` | Comma-separated sources: `web`, `scholar`, `social` |
| `answer_only` | bool | `false` | Return only answer text |
| `backend_uuid` | string | null | UUID for follow-up queries |
| `language` | string | `en-US` | Language code |
| `incognito` | bool | `false` | Enable incognito mode |

## Python Library Usage

```python
from lib.perplexity import Client
import json

# Load cookies
with open("perplexity_cookies.json") as f:
    cookies = json.load(f)

# Initialize client
client = Client(cookies)

# Basic search
result = client.search("What is quantum computing?", mode="auto")
print(result)

# Pro search with specific model
result = client.search(
    "Explain transformer architecture",
    mode="pro",
    model="claude 3.7 sonnet",
    sources=["web", "scholar"]
)

# Follow-up query
follow_up_result = client.search(
    "Can you provide code examples?",
    follow_up={
        "backend_uuid": result["backend_uuid"],
        "attachments": []
    }
)

# List threads
threads = client.get_threads(limit=10)

# Get thread details
thread_details = client.get_thread_details_by_slug("thread-slug")
```

## Cookie Setup Guide

Perplexity AI requires authentication cookies for API access. Here's how to obtain them:

### Method 1: Browser Developer Tools

1. Open [Perplexity AI](https://www.perplexity.ai) in your browser
2. Log in to your account
3. Open Developer Tools (F12 or right-click -> Inspect)
4. Go to the **Application** tab (Chrome) or **Storage** tab (Firefox)
5. Under **Cookies**, select `https://www.perplexity.ai`
6. Copy all cookies and format them as JSON

### Method 2: Cookie Export Extension

1. Install a cookie export extension like "EditThisCookie" or "Cookie-Editor"
2. Navigate to [Perplexity AI](https://www.perplexity.ai) and log in
3. Click the extension and export cookies as JSON
4. Save to `perplexity_cookies.json`

### Cookie File Format

Create `perplexity_cookies.json` in the project root:

```json
{
  "session_token": "your_session_token_value",
  "__cf_bm": "cloudflare_bot_management_token",
  "cf_clearance": "cloudflare_clearance_token"
}
```

The essential cookies typically include:
- `session_token` or similar session identifier
- Cloudflare tokens (`__cf_bm`, `cf_clearance`)

**Note**: Cookie names and requirements may change. Export all cookies from your authenticated session for best results.

### Cookie File Location

The MCP server and API look for cookies in this order:

1. `perplexity_cookies.json` in the project root
2. Path specified by `PERPLEXITY_COOKIES_PATH` environment variable

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PERPLEXITY_COOKIES_PATH` | Custom path to cookies JSON file | `./perplexity_cookies.json` |

Example:
```bash
export PERPLEXITY_COOKIES_PATH="/path/to/my/cookies.json"
```

## Troubleshooting

### Common Issues

**"No remaining pro queries"**
- Your Perplexity Pro subscription may have reached its query limit
- Use `mode="auto"` for unlimited free searches

**"No cookies file found"**
- Ensure `perplexity_cookies.json` exists in the project root
- Or set `PERPLEXITY_COOKIES_PATH` environment variable

**"Invalid model for the selected mode"**
- Check the model compatibility table above
- Some models are only available in specific modes

**Connection or authentication errors**
- Re-export cookies from your browser (they expire)
- Ensure you're logged into Perplexity AI when exporting

## Notes

- This is an **unofficial** project and not affiliated with Perplexity AI
- Respect Perplexity AI's terms of service and rate limits
- For production use, secure your cookies and restrict CORS appropriately
- Cookie sessions may expire and require periodic refresh

## License

MIT License. Contributions welcome!
