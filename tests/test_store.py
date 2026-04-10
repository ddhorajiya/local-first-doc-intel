from pathlib import Path

from lfdi import store


def test_store_upsert_and_search(tmp_path: Path):
    db_path = tmp_path / "lfdi.sqlite"
    conn = store.connect(db_path)
    store.init_db(conn)

    store.upsert_document(
        conn,
        path="/tmp/doc1.md",
        content_hash="hash1",
        content="hello world",
        summary="hello",
        tags=["greeting"],
    )

    results = list(store.search_fts(conn, "hello", limit=5))
    assert len(results) == 1
    assert results[0].path == "/tmp/doc1.md"

    # Update same path
    store.upsert_document(
        conn,
        path="/tmp/doc1.md",
        content_hash="hash2",
        content="hello world again",
        summary="hello again",
        tags=["greeting", "again"],
    )

    results = list(store.search_fts(conn, "again", limit=5))
    assert len(results) == 1
    assert "again" in results[0].summary
