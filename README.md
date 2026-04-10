# Local-First Document Intelligence

Local-First Document Intelligence is a privacy-first service that watches a folder on your machine, summarizes new documents, generates tags, and lets you search your files with semantic search. All processing happens locally using Ollama.

## Why
Most knowledge tools require uploading documents to a third-party server. This project keeps data on your machine while still providing AI-powered organization.

## Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com) installed and running locally
- Models pulled:
  - `ollama pull llama3`
  - `ollama pull nomic-embed-text`

## Quickstart
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .

# Copy env config
copy .env.example .env

# Edit config.toml to point at your watch folder
lfdi scan
lfdi watch
```

## Configuration
Edit `config.toml`:
- `watch_path`: Folder to monitor
- `db_path`: SQLite DB file path
- `chroma_path`: Vector index storage
- `summary_model`: Ollama chat model
- `embedding_model`: Ollama embedding model

`.env` can override:
- `LFDI_WATCH_PATH`
- `LFDI_DB_PATH`
- `LFDI_CHROMA_PATH`
- `LFDI_SUMMARY_MODEL`
- `LFDI_EMBEDDING_MODEL`

## CLI
```bash
lfdi scan            # Scan existing files in watch folder
lfdi watch           # Watch for new/updated files
lfdi search "query"  # Search locally (FTS or semantic)
```

Semantic search:
```bash
lfdi search "local-first" --semantic
```

## Project Structure
- `src/lfdi/` core package
- `tests/` pytest suite

## Open Source
MIT licensed. Contributions welcome.
