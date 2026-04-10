from __future__ import annotations

import argparse
from pathlib import Path

from .config import load_config
from .pipeline import Pipeline, scan_folder
from . import store
from . import vector
from .watcher import watch_folder


def _build_pipeline(config) -> Pipeline:
    conn = store.connect(config.db_path)
    store.init_db(conn)
    collection = vector.get_collection(config.chroma_path)
    return Pipeline(
        conn=conn,
        collection=collection,
        summary_model=config.summary_model,
        embedding_model=config.embedding_model,
    )


def cmd_scan(args: argparse.Namespace) -> None:
    config = load_config(Path.cwd())
    pipeline = _build_pipeline(config)
    count = scan_folder(pipeline, config.watch_path)
    print(f"Processed {count} files.")


def cmd_watch(args: argparse.Namespace) -> None:
    config = load_config(Path.cwd())
    pipeline = _build_pipeline(config)
    watch_folder(pipeline, config.watch_path)


def cmd_search(args: argparse.Namespace) -> None:
    config = load_config(Path.cwd())
    conn = store.connect(config.db_path)
    store.init_db(conn)

    if args.semantic:
        collection = vector.get_collection(config.chroma_path)
        results = vector.query(collection, args.query, config.embedding_model, limit=args.limit)
        for item in results:
            meta = item.get("metadata", {}) or {}
            print(f"{meta.get('path', 'unknown')}\n  tags: {meta.get('tags', '')}\n  summary: {meta.get('summary', '')}\n")
        return

    for record in store.search_fts(conn, args.query, limit=args.limit):
        tags = ", ".join(record.tags)
        print(f"{record.path}\n  tags: {tags}\n  summary: {record.summary}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lfdi")
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="Scan existing files in the watch folder")
    scan.set_defaults(func=cmd_scan)

    watch = sub.add_parser("watch", help="Watch for file changes")
    watch.set_defaults(func=cmd_watch)

    search = sub.add_parser("search", help="Search documents")
    search.add_argument("query", help="Search query")
    search.add_argument("--semantic", action="store_true", help="Use semantic search")
    search.add_argument("--limit", type=int, default=5)
    search.set_defaults(func=cmd_search)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
