"""
MCP Server for Perplexity AI.

Provides tools for searching, follow-up queries, and thread management
via the Model Context Protocol.
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

# Add parent directory to path for lib imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.perplexity import Client

# Initialize FastMCP server
mcp = FastMCP("Perplexity AI")

# Lazy-loaded client instance
_client: Optional[Client] = None


def get_client() -> Client:
    """
    Get or create the Perplexity client instance.

    Loads cookies from perplexity_cookies.json in the project root,
    or from the path specified in PERPLEXITY_COOKIES_PATH env var.
    """
    global _client
    if _client is None:
        cookies = {}

        # Check project root first
        project_root = Path(__file__).parent.parent
        cookies_path = project_root / "perplexity_cookies.json"

        # Fall back to env var if not found in project root
        if not cookies_path.exists():
            env_path = os.environ.get("PERPLEXITY_COOKIES_PATH")
            if env_path:
                cookies_path = Path(env_path)

        # Load cookies if file exists
        if cookies_path.exists():
            try:
                with open(cookies_path, "r", encoding="utf-8") as f:
                    cookies = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load cookies from {cookies_path}: {e}", file=sys.stderr)
        else:
            print("Warning: No cookies file found. Using empty cookies.", file=sys.stderr)

        _client = Client(cookies)

    return _client


def extract_response(raw: dict, answer_only: bool = True) -> dict:
    """
    Extract structured data from Perplexity API response.

    Args:
        raw: Raw response from Perplexity API
        answer_only: If True, return only answer and backend_uuid.
                     If False, also include sources and related_queries.

    Returns:
        Dictionary with extracted fields
    """
    backend_uuid = raw.get("backend_uuid")
    answer = None

    # Extract answer from blocks
    blocks = raw.get("blocks", [])
    if isinstance(blocks, list):
        for block in blocks:
            if block.get("intended_usage") == "ask_text":
                md_block = block.get("markdown_block", {})
                if isinstance(md_block, dict):
                    progress = md_block.get("progress")
                    if progress == "DONE":
                        answer = md_block.get("answer")
                    elif progress == "IN_PROGRESS":
                        chunks = md_block.get("chunks", [])
                        if isinstance(chunks, list):
                            answer = "".join(chunks)
                break

    if answer_only:
        return {
            "answer": answer,
            "backend_uuid": backend_uuid
        }

    # Extract sources from text array (SEARCH_RESULTS)
    sources = []
    text_items = raw.get("text", [])
    if isinstance(text_items, list):
        for item in text_items:
            if isinstance(item, dict) and item.get("step_type") == "SEARCH_RESULTS":
                content = item.get("content", {})
                if isinstance(content, dict):
                    web_results = content.get("web_results", [])
                    if isinstance(web_results, list):
                        for wr in web_results[:10]:
                            if isinstance(wr, dict):
                                url = wr.get("url")
                                if url and url not in sources:
                                    sources.append(url)

    # Also check widget_data for additional sources
    widget_data = raw.get("widget_data", [])
    if isinstance(widget_data, list):
        for wd in widget_data[:5]:
            if isinstance(wd, dict):
                url = wd.get("url")
                if url and url not in sources:
                    sources.append(url)

    # Extract related queries
    related = raw.get("related_queries", [])
    if isinstance(related, list):
        related = related[:5]
    else:
        related = []

    return {
        "answer": answer,
        "backend_uuid": backend_uuid,
        "sources": sources,
        "related_queries": related
    }


@mcp.tool()
def search(
    query: str,
    mode: str = "auto",
    model: Optional[str] = None,
    sources: Optional[list[str]] = None,
    answer_only: bool = True,
    language: str = "en-US",
    incognito: bool = False
) -> dict:
    """
    Search Perplexity AI with the given query.

    Args:
        query: The search query string
        mode: Search mode - 'auto', 'pro', 'reasoning', or 'deep_research'
        model: Specific model to use (depends on mode):
               - auto: None
               - pro: None, 'sonar', 'gpt-4.5', 'gpt-4o', 'claude 3.7 sonnet',
                      'gemini 2.0 flash', 'grok-2'
               - reasoning: None, 'r1', 'o3-mini', 'claude 3.7 sonnet'
               - deep_research: None
        sources: List of sources to use - 'web', 'scholar', 'social'
        answer_only: If True, return only answer and backend_uuid.
                     If False, also include sources and related_queries.
        language: Language code (ISO 639, e.g., 'en-US')
        incognito: Whether to enable incognito mode

    Returns:
        Dictionary with 'answer' and 'backend_uuid'.
        If answer_only=False, also includes 'sources' and 'related_queries'.
    """
    if sources is None:
        sources = ["web"]

    # Normalize mode: "deep_research" -> "deep research"
    normalized_mode = mode.replace("_", " ")

    client = get_client()

    try:
        result = client.search(
            query=query,
            mode=normalized_mode,
            model=model,
            sources=sources,
            files={},
            stream=False,
            language=language,
            follow_up=None,
            incognito=incognito
        )

        return extract_response(result, answer_only)

    except Exception as e:
        return {
            "error": str(e),
            "answer": None,
            "backend_uuid": None
        }


@mcp.tool()
def follow_up(
    query: str,
    backend_uuid: str,
    mode: str = "auto",
    model: Optional[str] = None,
    answer_only: bool = True
) -> dict:
    """
    Send a follow-up query to continue a previous conversation.

    Args:
        query: The follow-up query string
        backend_uuid: The backend_uuid from the previous response
        mode: Search mode - 'auto', 'pro', 'reasoning', or 'deep_research'
        model: Specific model to use (see search tool for options)
        answer_only: If True, return only answer and backend_uuid.
                     If False, also include sources and related_queries.

    Returns:
        Dictionary with 'answer' and 'backend_uuid'.
        If answer_only=False, also includes 'sources' and 'related_queries'.
    """
    # Normalize mode: "deep_research" -> "deep research"
    normalized_mode = mode.replace("_", " ")

    # Build follow_up parameter for the client
    follow_up_param = {
        "backend_uuid": backend_uuid,
        "attachments": []
    }

    client = get_client()

    try:
        result = client.search(
            query=query,
            mode=normalized_mode,
            model=model,
            sources=["web"],
            files={},
            stream=False,
            language="en-US",
            follow_up=follow_up_param,
            incognito=False
        )

        return extract_response(result, answer_only)

    except Exception as e:
        return {
            "error": str(e),
            "answer": None,
            "backend_uuid": None
        }


@mcp.tool()
def list_threads(
    limit: int = 10,
    search_term: str = ""
) -> dict:
    """
    List conversation threads from Perplexity AI.

    Args:
        limit: Maximum number of threads to return (default 10)
        search_term: Optional search term to filter threads

    Returns:
        Dictionary containing list of threads with their metadata
    """
    client = get_client()

    try:
        result = client.get_threads(
            limit=limit,
            offset=0,
            search_term=search_term
        )
        return result

    except Exception as e:
        return {
            "error": str(e),
            "threads": []
        }


@mcp.tool()
def get_thread(slug: str) -> dict:
    """
    Get details of a specific thread by its slug.

    Args:
        slug: The thread slug (identifier from thread URL or list_threads)

    Returns:
        Dictionary containing thread details including all messages
    """
    client = get_client()

    try:
        result = client.get_thread_details_by_slug(slug)
        return result

    except Exception as e:
        return {
            "error": str(e),
            "thread": None
        }


def main():
    """Main entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
