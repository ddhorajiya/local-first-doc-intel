from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import sqlite3
from typing import Iterable


@dataclass
class DocumentRecord:
    doc_id: int
    path: str
    content_hash: str
    summary: str
    tags: list[str]


SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
  id INTEGER PRIMARY KEY,
  path TEXT NOT NULL UNIQUE,
  content_hash TEXT NOT NULL,
  content TEXT NOT NULL,
  summary TEXT,
  tags TEXT,
  updated_at TEXT DEFAULT (datetime('now'))
);

CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
  content,
  summary,
  tags,
  content='documents',
  content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
  INSERT INTO documents_fts(rowid, content, summary, tags)
  VALUES (new.id, new.content, new.summary, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
  INSERT INTO documents_fts(documents_fts, rowid, content, summary, tags)
  VALUES('delete', old.id, old.content, old.summary, old.tags);
END;

CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
  INSERT INTO documents_fts(documents_fts, rowid, content, summary, tags)
  VALUES('delete', old.id, old.content, old.summary, old.tags);
  INSERT INTO documents_fts(rowid, content, summary, tags)
  VALUES (new.id, new.content, new.summary, new.tags);
END;
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def upsert_document(
    conn: sqlite3.Connection,
    path: str,
    content_hash: str,
    content: str,
    summary: str,
    tags: list[str],
) -> int:
    tags_json = json.dumps(tags)
    cur = conn.execute(
        """
        INSERT INTO documents (path, content_hash, content, summary, tags)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET
          content_hash=excluded.content_hash,
          content=excluded.content,
          summary=excluded.summary,
          tags=excluded.tags,
          updated_at=datetime('now')
        """,
        (path, content_hash, content, summary, tags_json),
    )
    conn.commit()
    return cur.lastrowid


def search_fts(conn: sqlite3.Connection, query: str, limit: int = 10) -> Iterable[DocumentRecord]:
    cur = conn.execute(
        """
        SELECT d.id, d.path, d.content_hash, d.summary, d.tags
        FROM documents_fts f
        JOIN documents d ON d.id = f.rowid
        WHERE documents_fts MATCH ?
        LIMIT ?
        """,
        (query, limit),
    )
    for row in cur.fetchall():
        yield DocumentRecord(
            doc_id=row["id"],
            path=row["path"],
            content_hash=row["content_hash"],
            summary=row["summary"] or "",
            tags=json.loads(row["tags"] or "[]"),
        )


def get_by_path(conn: sqlite3.Connection, path: str) -> DocumentRecord | None:
    cur = conn.execute(
        "SELECT id, path, content_hash, summary, tags FROM documents WHERE path = ?",
        (path,),
    )
    row = cur.fetchone()
    if not row:
        return None
    return DocumentRecord(
        doc_id=row["id"],
        path=row["path"],
        content_hash=row["content_hash"],
        summary=row["summary"] or "",
        tags=json.loads(row["tags"] or "[]"),
    )
