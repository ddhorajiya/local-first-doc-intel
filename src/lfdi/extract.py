from __future__ import annotations

from pathlib import Path
import hashlib
import re

from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".pdf", ".md", ".markdown", ".txt"}


def is_supported(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(path)
    if suffix in {".md", ".markdown", ".txt"}:
        return _extract_text(path)
    raise ValueError(f"Unsupported file type: {path}")


def _extract_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        parts.append(text)
    return "\n".join(parts)


def _extract_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    # Strip simple YAML front matter if present
    if raw.startswith("---"):
        raw = re.sub(r"^---[\s\S]*?---\s*", "", raw, count=1)
    return raw


def normalize_text(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()
