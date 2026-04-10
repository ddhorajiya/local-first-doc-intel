from __future__ import annotations

from pathlib import Path
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from .pipeline import Pipeline


class DocumentEventHandler(FileSystemEventHandler):
    def __init__(self, pipeline: Pipeline):
        super().__init__()
        self.pipeline = pipeline

    def on_created(self, event: FileSystemEvent) -> None:
        self._handle(event)

    def on_modified(self, event: FileSystemEvent) -> None:
        self._handle(event)

    def _handle(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        path = Path(event.src_path)
        try:
            self.pipeline.process_path(path)
        except Exception as exc:
            print(f"Error processing {path}: {exc}")


def watch_folder(pipeline: Pipeline, folder: Path) -> None:
    observer = Observer()
    handler = DocumentEventHandler(pipeline)
    observer.schedule(handler, str(folder), recursive=True)
    observer.start()
    print(f"Watching {folder}... (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
