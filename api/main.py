from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse


import json
from lib import perplexity

from typing import List, Optional
from datetime import datetime
from .utils import extract_answer, save_resp

# Initialize Perplexity client
try:
    with open("perplexity_cookies.json", "r", encoding="utf-8") as f:
        perplexity_cookies = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    print("Cookies file not found or invalid. Using empty cookies.")
    perplexity_cookies = {}

perplexity_cli = perplexity.Client(perplexity_cookies)
app = FastAPI(
    title="Perplexity Web API", description="Stream Perplexity AI responses using SSE"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def generate_sse_stream(
    query: str,
    answer_only: bool,
    mode: str,
    model: Optional[str],
    sources: List[str],
    language: str,
    follow_up: Optional[dict],
    incognito: bool,
):
    """Generate SSE stream from Perplexity responses."""
    response_count = 0

    # Start the streaming search in a sync function
    try:
        for stream in perplexity_cli.search(
            query,
            mode=mode,
            model=model,
            sources=sources,
            files={},
            stream=True,
            language=language,
            follow_up=follow_up,
            incognito=incognito,
        ):
            response_count += 1
            file_name = (
                f"API-{datetime.now().strftime('%Y%m%d%H%M%S')}-{response_count}"
            )
            save_resp(stream, file_name)
            if answer_only:
                ans_data = extract_answer(stream, file_name)
                if "answer" in ans_data and ans_data["answer"] is not None:
                    event_data = json.dumps(
                        {
                            "type": "content",
                            "content": ans_data,
                            "done": False,
                        }
                    )
                    yield f"data: {event_data}\n\n"

            # If not answer_only, send the full stream content
            else:
                event_data = json.dumps(
                    {"type": "content", "content": stream, "done": False}
                )
                yield f"data: {event_data}\n\n"

        # Send completion event
        event_data = json.dumps({"type": "content", "content": "", "done": True})
        yield f"data: {event_data}\n\n"

    except Exception as e:
        error_data = json.dumps({"type": "error", "error": str(e)})
        yield f"data: {error_data}\n\n"


@app.get("/api/query_async")
async def query_async(
    q: str = Query(..., description="Query string to search"),
    backend_uuid: str = Query(
        None, description="UUID of the previous response", alias="backend_uuid"
    ),
    answer_only: bool = Query(False, description="Return only the answer text"),
    mode: str = Query(
        "auto",
        description="Search mode",
        enum=["auto", "writing", "coding", "research"],
    ),
    model: Optional[str] = Query(None, description="Model to use"),
    sources: str = Query("web", description="Sources (comma-separated)"),
    language: str = Query("en-US", description="Language"),
    incognito: bool = Query(False, description="Use incognito mode"),
):
    """Stream Perplexity AI responses as Server-Sent Events (SSE). Handles both new and follow-up queries."""
    sources_list = [s.strip() for s in sources.split(",")]
    follow_up = (
        {"backend_uuid": backend_uuid, "attachments": []} if backend_uuid else None
    )
    return StreamingResponse(
        generate_sse_stream(
            query=q,
            answer_only=answer_only,
            mode=mode,
            model=model,
            sources=sources_list,
            language=language,
            follow_up=follow_up,
            incognito=incognito,
        ),
        media_type="text/event-stream",
    )


@app.get("/api/query_sync")
def query_sync(
    q: str = Query(..., description="Query string to search"),
    backend_uuid: str = Query(
        None, description="UUID of the previous response", alias="backend_uuid"
    ),
    answer_only: bool = Query(False, description="Return only the answer text"),
    mode: str = Query(
        "auto",
        description="Search mode",
        enum=["auto", "writing", "coding", "research"],
    ),
    model: Optional[str] = Query(None, description="Model to use"),
    sources: str = Query("web", description="Sources (comma-separated)"),
    language: str = Query("en-US", description="Language"),
    incognito: bool = Query(False, description="Use incognito mode"),
):
    """Query Perplexity AI and return the full response as JSON (no streaming)."""
    sources_list = [s.strip() for s in sources.split(",")]
    follow_up = (
        {"backend_uuid": backend_uuid, "attachments": []} if backend_uuid else None
    )
    try:
        result = perplexity_cli.search(
            q,
            mode=mode,
            model=model,
            sources=sources_list,
            files={},
            stream=False,
            language=language,
            follow_up=follow_up,
            incognito=incognito,
        )
        file_name = f"API-{datetime.now().strftime('%Y%m%d%H%M%S')}-sync"
        save_resp(result, file_name)
        if answer_only:
            ans_data = extract_answer(result, file_name)
            return JSONResponse(content=ans_data)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/threads")
def get_threads(limit: int = 20, offset: int = 0, search_term: str = ""):
    """Fetch a list of threads from Perplexity AI."""
    try:
        threads = perplexity_cli.get_threads(
            limit=limit, offset=offset, search_term=search_term
        )
        return JSONResponse(content=threads)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/api/threads/{slug}")
def get_thread(slug: str):
    """Fetch a specific thread by slug."""
    try:
        thread = perplexity_cli.get_thread_details_by_slug(slug)
        return JSONResponse(content=thread)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
