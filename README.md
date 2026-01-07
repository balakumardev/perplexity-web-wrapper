# About

Unofficial Python wrapper and API server for Perplexity AI's web interface.

## Requirements

- Python 3.13+
- See `pyproject.toml` for dependencies (curl-cffi, fastapi, uvicorn, websocket-client)

## Installation

1. Clone this repository:
   ```sh
   git clone <your-repo-url>
   cd perplexity-web-wrapper
   ```
2. Install dependencies using [uv](https://github.com/astral-sh/uv):
   ```sh
   uv sync
   ```

## Configuration

- Place your Perplexity cookies in `perplexity_cookies.json` (see example in repo).
- The API and library will use these cookies for authenticated requests.

## Running the API Server

From the project root, start the FastAPI server using Uvicorn:

```sh
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

## Supported Library Functionality

| Functionality | Method/Attribute       | Description                                                               |
| ------------- | ---------------------- | ------------------------------------------------------------------------- |
| Search        | `Client.search()`      | Query Perplexity AI with various modes, models, sources, and file uploads |
| List Threads  | `Client.get_threads()` | Fetch a list of threads from Perplexity AI                                |

## API Endpoints

See `/docs` (Swagger UI) for full API details and interactive usage.

## Library Usage

You can use the Python client directly:

```python
from lib.perplexity import Client
import json

with open("perplexity_cookies.json") as f:
    cookies = json.load(f)

client = Client(cookies)
result = client.search("What is Perplexity AI?", mode="auto")
print(result)
```

## Notes

- This is an unofficial project and not affiliated with Perplexity AI.
- For production, restrict CORS and secure your cookies.

## License

MIT. Contributions welcome!
