import os
import json

logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../logs")
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)


def extract_answer(res, file_name):
    """Extract answer from Perplexity API response."""
    backend_uuid = res.get("backend_uuid", None)
    blocks = res.get("blocks", [])
    if not isinstance(blocks, list):
        print(f"Unexpected blocks format in {file_name}: {blocks}")
        return {"answer": None, "backend_uuid": backend_uuid}

    for block in blocks:
        intended_usage = block.get("intended_usage", "")
        if not intended_usage == "ask_text":
            continue

        mardown_block = block.get("markdown_block", {})
        if not isinstance(mardown_block, dict):
            print(f"Unexpected markdown_block format in {file_name}: {mardown_block}")
            continue

        progress = mardown_block.get("progress")
        if progress == "IN_PROGRESS":
            chunks = mardown_block.get("chunks", [])
            if not isinstance(chunks, list):
                print(f"Unexpected chunks format in {file_name}: {chunks}")
                continue

            answer = "".join(chunks)
            return {
                "progress": progress,
                "answer": answer,
                "backend_uuid": backend_uuid,
            }

        if progress == "DONE":
            answer = mardown_block.get("answer")

            return {
                "progress": progress,
                "answer": answer,
                "backend_uuid": backend_uuid,
            }

        else:
            print(
                f"Unexpected progress state in {file_name}: {progress} for block {block}"
            )
            return {"answer": None, "backend_uuid": backend_uuid}

    return {"answer": None, "backend_uuid": backend_uuid}


def save_resp(res, file_name):
    """Save response to file for logging/debugging."""
    try:
        with open(os.path.join(logs_dir, file_name), "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2, ensure_ascii=False)
    except Exception:
        # Silently fail if we can't save
        pass
