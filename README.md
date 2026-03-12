# Perplexity Subscription MCP

Unofficial Python wrapper for Perplexity AI's web interface, providing an MCP (Model Context Protocol) server and Python client for integration with coding agents.

**Use your existing Perplexity subscription** — no API costs. This wrapper uses your Perplexity web session cookies, so all queries use your existing Pro subscription instead of the paid Perplexity API.

## Why This Wrapper?

| Approach | Cost | Rate Limits |
|----------|------|-------------|
| **This wrapper** (web session) | $0 (uses your existing subscription) | Your subscription limits |
| Perplexity API | $5/1000 requests (sonar), $200/month (pro tier) | API tier limits |

If you already have a Perplexity Pro subscription ($20/month), this wrapper lets you integrate Perplexity into your coding workflow without additional API costs.

## Quick Start

No install needed — your MCP config runs the server via `uvx` automatically.

> **Prerequisites:** [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.10+

### 1. Get Your Perplexity Cookies

The MCP server authenticates using your browser's Perplexity session cookies. You need to export them once (and re-export when they expire).

#### Option A: Cookie-Editor Extension (Recommended)

1. Install the [Cookie-Editor](https://cookie-editor.com/) browser extension ([Chrome](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm), [Firefox](https://addons.mozilla.org/en-US/firefox/addon/cookie-editor/))
2. Go to [perplexity.ai](https://www.perplexity.ai) and **log in** to your account
3. Click the Cookie-Editor extension icon
4. Click **Export** (bottom-left) → copies JSON to clipboard
5. Save the clipboard content to a file:
   ```bash
   # Create the config directory
   mkdir -p ~/.config/perplexity

   # Paste your clipboard into this file
   # macOS:
   pbpaste > ~/.config/perplexity/cookies.json

   # Linux:
   xclip -selection clipboard -o > ~/.config/perplexity/cookies.json

   # Windows (PowerShell):
   Get-Clipboard | Out-File -Encoding utf8 ~/.config/perplexity/cookies.json

   # Or just create the file manually and paste the JSON content
   ```

This gives you an array format like:
```json
[
  {"domain": ".perplexity.ai", "name": "__Secure-next-auth.session-token", "value": "eyJ...", ...},
  {"domain": ".perplexity.ai", "name": "pplx.visitor-id", "value": "...", ...}
]
```

#### Option B: Browser DevTools (Manual)

1. Go to [perplexity.ai](https://www.perplexity.ai) and **log in**
2. Open DevTools (`F12` or `Cmd+Opt+I` / `Ctrl+Shift+I`)
3. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
4. Click **Cookies** → `https://www.perplexity.ai`
5. Copy cookie names and values into a JSON file:

```json
{
  "__Secure-next-auth.session-token": "eyJ...",
  "pplx.visitor-id": "...",
  "__cf_bm": "..."
}
```

Save as `~/.config/perplexity/cookies.json`.

> **Tip:** Export **all** cookies from perplexity.ai for best results. The essential one is `__Secure-next-auth.session-token`, but exporting everything avoids issues with missing tokens.

Both formats (array from Cookie-Editor and flat object from manual export) are supported automatically.

### 2. Add to Your Coding Agent

Pick your agent below. Each config uses `uvx` to run the server directly from PyPI — no install step needed. Replace `YOUR_ABSOLUTE_PATH` with your actual home directory path (e.g., `/home/user` or `/Users/yourname`).

#### Claude Code CLI

```bash
claude mcp add --transport stdio perplexity --scope user \
  -e PERPLEXITY_COOKIES_PATH=$HOME/.config/perplexity/cookies.json \
  -- uvx --from perplexity-subscription-mcp perplexity-mcp
```

Verify: `claude mcp list` · Remove: `claude mcp remove perplexity -s user`

#### Augment CLI (Auggie)

```bash
auggie mcp add perplexity \
  -e PERPLEXITY_COOKIES_PATH=$HOME/.config/perplexity/cookies.json \
  -- uvx --from perplexity-subscription-mcp perplexity-mcp
```

Verify: `auggie mcp list` · Remove: `auggie mcp remove perplexity`

#### Cursor IDE

File: `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "perplexity": {
      "command": "uvx",
      "args": ["--from", "perplexity-subscription-mcp", "perplexity-mcp"],
      "env": {
        "PERPLEXITY_COOKIES_PATH": "YOUR_ABSOLUTE_PATH/.config/perplexity/cookies.json"
      }
    }
  }
}
```

#### Windsurf IDE

File: `~/.codeium/windsurf/mcp_config.json`

```json
{
  "mcpServers": {
    "perplexity": {
      "command": "uvx",
      "args": ["--from", "perplexity-subscription-mcp", "perplexity-mcp"],
      "env": {
        "PERPLEXITY_COOKIES_PATH": "YOUR_ABSOLUTE_PATH/.config/perplexity/cookies.json"
      }
    }
  }
}
```

#### OpenAI Codex CLI

File: `~/.codex/config.toml`

```toml
[mcp_servers.perplexity]
command = "uvx"
args = ["--from", "perplexity-subscription-mcp", "perplexity-mcp"]

[mcp_servers.perplexity.env]
PERPLEXITY_COOKIES_PATH = "YOUR_ABSOLUTE_PATH/.config/perplexity/cookies.json"
```

#### VS Code with Continue Extension

File: `.continue/config.json`

```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "stdio",
          "command": "uvx",
          "args": ["--from", "perplexity-subscription-mcp", "perplexity-mcp"],
          "env": {
            "PERPLEXITY_COOKIES_PATH": "YOUR_ABSOLUTE_PATH/.config/perplexity/cookies.json"
          }
        }
      }
    ]
  }
}
```

#### VS Code with Cline Extension

```json
{
  "cline.mcpServers": {
    "perplexity": {
      "command": "uvx",
      "args": ["--from", "perplexity-subscription-mcp", "perplexity-mcp"],
      "env": {
        "PERPLEXITY_COOKIES_PATH": "YOUR_ABSOLUTE_PATH/.config/perplexity/cookies.json"
      }
    }
  }
}
```

### Cookie Location Resolution

If `PERPLEXITY_COOKIES_PATH` is not set, the server checks these locations in order:

1. `PERPLEXITY_COOKIES_PATH` env var — explicit file path
2. `PERPLEXITY_COOKIES` env var — inline JSON string (useful for CI/Docker)
3. `~/.config/perplexity/cookies.json` — default user config location
4. `./perplexity_cookies.json` — current working directory

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

- `web` — General web search (default)
- `scholar` — Academic papers and research
- `social` — Social media content

### Additional Features

- **Token-efficient `answer_only` mode**: Returns only the answer and `backend_uuid`, reducing response size
- **Follow-up conversations**: Continue discussions using `backend_uuid` from previous responses
- **Thread management**: List and retrieve past conversation threads
- **Incognito mode**: Search without saving to history
- **File uploads**: Attach files to queries (Pro subscription)

## MCP Tools Reference

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `search` | Search Perplexity AI | `query` (required), `mode`, `model`, `sources`, `answer_only`, `language`, `incognito` |
| `follow_up` | Continue a previous conversation | `query` (required), `backend_uuid` (required), `mode`, `model`, `answer_only` |
| `list_threads` | List conversation threads | `limit`, `search_term` |
| `get_thread` | Get thread details by slug | `slug` (required) |

### Tool Details

#### search

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
follow_up(query="Can you elaborate on that?", backend_uuid="abc-123-def-456")
```

#### list_threads / get_thread

```python
list_threads(limit=10, search_term="python")
get_thread(slug="thread-slug-here")
```

## Agent Instructions (Optional)

To help coding agents use Perplexity MCP efficiently, add these instructions to your agent's rules file:

```markdown
# Perplexity MCP - Web Research

**Use Perplexity MCP instead of web search. Use fetch/WebFetch only when you need full page content.**

| Tool | Use For |
|------|---------|
| `perplexity.search` | ALL web research - replaces web search |
| `fetch` | Reading full page content in detail when needed |

## Mode Selection

| Research Type | Mode | Use Case |
|--------------|------|----------|
| Quick lookup | `auto` | Simple facts, definitions, quick answers |
| Standard research | `pro` | API docs, library usage, best practices, debugging |
| Deep research | `deep_research` | PRDs, design docs, comprehensive analysis |

## When to Use Each Mode

- **auto**: "What is X?", simple lookups, quick facts
- **pro**: Technical questions, debugging, API research, implementation guidance
- **deep_research**: Creating PRDs, design documents, competitive analysis, comprehensive guides
```

| Agent | Instructions File |
|-------|------------------|
| Claude Code | `~/.claude/CLAUDE.md` |
| Auggie | `~/.augment/rules/perplexity.md` |
| Cursor | `~/.cursor/CURSOR_INSTRUCTIONS.md` |
| Codex CLI | `~/.codex/AGENTS.md` |

## Python Library Usage

Install the package if using as a Python library:

```bash
pip install perplexity-subscription-mcp
```

```python
from perplexity_subscription_mcp import Client
from pathlib import Path
import json

# Load cookies
with open(Path.home() / ".config/perplexity/cookies.json") as f:
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

## REST API (Optional — for development)

The REST API is not included in the PyPI package. To use it, clone the repo and install with the `api` extra:

```bash
git clone https://github.com/balakumardev/perplexity-web-wrapper.git
cd perplexity-web-wrapper
uv sync --extra api
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/query_sync` | GET | Synchronous search |
| `/api/query_async` | GET | SSE streaming response |
| `/api/threads` | GET | List conversation threads |
| `/api/threads/{slug}` | GET | Get thread details by slug |

## Troubleshooting

**"No cookies file found"**
- Export cookies following the [setup guide](#2-get-your-perplexity-cookies) above
- Verify the file exists: `cat ~/.config/perplexity/cookies.json`
- Check your MCP config has `PERPLEXITY_COOKIES_PATH` set correctly

**"No remaining pro queries"**
- Your Pro subscription may have hit its limit. Use `mode="auto"` for free searches.

**"Invalid model for the selected mode"**
- Check the [model compatibility table](#available-models). Some models only work in specific modes.

**Connection or authentication errors**
- Cookies expire periodically. Re-export from your browser and replace the file.
- Make sure you're logged in to Perplexity when exporting cookies.

## Notes

- This is an **unofficial** project and not affiliated with Perplexity AI
- Respect Perplexity AI's terms of service and rate limits
- Cookie sessions expire periodically — re-export when you get auth errors

## License

MIT License. Contributions welcome!
