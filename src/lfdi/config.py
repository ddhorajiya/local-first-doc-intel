from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import tomllib

from dotenv import load_dotenv


@dataclass
class Config:
    watch_path: Path
    db_path: Path
    chroma_path: Path
    summary_model: str
    embedding_model: str


def _read_toml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("rb") as f:
        return tomllib.load(f)


def load_config(base_dir: Path | None = None, config_name: str = "config.toml") -> Config:
    base = base_dir or Path.cwd()
    load_dotenv(base / ".env")
    data = _read_toml(base / config_name)

    watch_path = os.getenv("LFDI_WATCH_PATH", data.get("watch_path", ""))
    db_path = os.getenv("LFDI_DB_PATH", data.get("db_path", "data/lfdi.sqlite"))
    chroma_path = os.getenv("LFDI_CHROMA_PATH", data.get("chroma_path", "data/chroma"))
    summary_model = os.getenv("LFDI_SUMMARY_MODEL", data.get("summary_model", "llama3"))
    embedding_model = os.getenv("LFDI_EMBEDDING_MODEL", data.get("embedding_model", "nomic-embed-text"))

    if not watch_path:
        raise ValueError("watch_path is required. Set it in config.toml or LFDI_WATCH_PATH.")

    return Config(
        watch_path=Path(watch_path),
        db_path=Path(db_path),
        chroma_path=Path(chroma_path),
        summary_model=summary_model,
        embedding_model=embedding_model,
    )
