from pathlib import Path

from lfdi import extract


def test_extract_markdown(tmp_path: Path):
    doc = tmp_path / "doc.md"
    doc.write_text("---\ntitle: Test\n---\nHello world\n", encoding="utf-8")

    text = extract.extract_text(doc)
    assert "Hello world" in text

    normalized = extract.normalize_text(text)
    assert normalized == "Hello world"

    digest = extract.hash_text(normalized)
    assert len(digest) == 64
