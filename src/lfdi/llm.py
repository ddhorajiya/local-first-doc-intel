from __future__ import annotations

import json
from typing import Any

import ollama


MAX_CONTEXT_CHARS = 6000


def _truncate(text: str, max_chars: int = MAX_CONTEXT_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars]


def summarize_and_tag(text: str, model: str) -> tuple[str, list[str]]:
    prompt = (
        "You are a local document assistant. "
        "Summarize the document in 2-3 sentences and return 3-8 concise tags. "
        "Respond as strict JSON with keys 'summary' and 'tags'."
    )
    content = _truncate(text)
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": content},
        ],
    )
    raw = response.get("message", {}).get("content", "{}")
    summary, tags = _parse_json(raw)
    return summary, tags


def embed(text: str, model: str) -> list[float]:
    content = _truncate(text, max_chars=4000)
    result = ollama.embeddings(model=model, prompt=content)
    return result.get("embedding", [])


def _parse_json(raw: str) -> tuple[str, list[str]]:
    try:
        data: Any = json.loads(raw)
        summary = str(data.get("summary", "")).strip()
        tags = [str(t).strip() for t in data.get("tags", []) if str(t).strip()]
        return summary, tags
    except json.JSONDecodeError:
        # Fallback: naive extraction if the model didn't return JSON
        summary = raw.strip()
        return summary[:500], []
