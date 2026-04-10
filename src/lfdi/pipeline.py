from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import extract
from .llm import summarize_and_tag
from . import store
from . import vector


@dataclass
class Pipeline:
    conn: object
    collection: object
    summary_model: str
    embedding_model: str

    def process_path(self, path: Path) -> bool:
        if not extract.is_supported(path):
            return False
        text = extract.extract_text(path)
        normalized = extract.normalize_text(text)
        content_hash = extract.hash_text(normalized)

        existing = store.get_by_path(self.conn, str(path))
        if existing and existing.content_hash == content_hash:
            return False

        summary, tags = summarize_and_tag(normalized, self.summary_model)
        store.upsert_document(
            self.conn,
            path=str(path),
            content_hash=content_hash,
            content=normalized,
            summary=summary,
            tags=tags,
        )
        vector.upsert_document(
            self.collection,
            path=str(path),
            content=normalized,
            summary=summary,
            tags=tags,
            embedding_model=self.embedding_model,
        )
        return True


def scan_folder(pipeline: Pipeline, folder: Path) -> int:
    count = 0
    for path in folder.rglob("*"):
        if path.is_file():
            if pipeline.process_path(path):
                count += 1
    return count
