from pathlib import Path

import lfdi.pipeline as pipeline
from lfdi import store


def test_pipeline_process_path(tmp_path: Path, monkeypatch):
    watch = tmp_path / "watch"
    watch.mkdir()
    doc = watch / "doc.txt"
    doc.write_text("hello local first", encoding="utf-8")

    db_path = tmp_path / "lfdi.sqlite"
    conn = store.connect(db_path)
    store.init_db(conn)

    class StubCollection:
        pass

    def fake_summarize(text: str, model: str):
        return "summary", ["tag1", "tag2"]

    def fake_upsert(*args, **kwargs):
        return None

    monkeypatch.setattr(pipeline, "summarize_and_tag", fake_summarize)
    monkeypatch.setattr(pipeline.vector, "upsert_document", fake_upsert)

    pipe = pipeline.Pipeline(
        conn=conn,
        collection=StubCollection(),
        summary_model="llama3",
        embedding_model="nomic-embed-text",
    )

    processed = pipe.process_path(doc)
    assert processed is True

    again = pipe.process_path(doc)
    assert again is False
