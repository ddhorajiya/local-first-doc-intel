from __future__ import annotations

from pathlib import Path
from typing import Iterable
import hashlib

import chromadb

from .llm import embed


COLLECTION_NAME = "lfdi_documents"


def _doc_id(path: str) -> str:
    return hashlib.sha256(path.encode("utf-8")).hexdigest()


def get_collection(chroma_path: Path):
    chroma_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(chroma_path))
    return client.get_or_create_collection(name=COLLECTION_NAME)


def upsert_document(
    collection,
    path: str,
    content: str,
    summary: str,
    tags: list[str],
    embedding_model: str,
) -> None:
    vec = embed(content, embedding_model)
    doc_id = _doc_id(path)
    metadata = {
        "path": path,
        "summary": summary,
        "tags": ", ".join(tags),
    }
    collection.upsert(
        ids=[doc_id],
        embeddings=[vec],
        documents=[content],
        metadatas=[metadata],
    )


def query(collection, text: str, embedding_model: str, limit: int = 5) -> Iterable[dict]:
    vec = embed(text, embedding_model)
    results = collection.query(query_embeddings=[vec], n_results=limit)
    items = []
    for i in range(len(results.get("ids", [[]])[0])):
        items.append(
            {
                "id": results["ids"][0][i],
                "document": results.get("documents", [[]])[0][i],
                "metadata": results.get("metadatas", [[]])[0][i],
                "distance": results.get("distances", [[]])[0][i],
            }
        )
    return items
