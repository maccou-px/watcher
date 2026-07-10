import argparse
import sys
import time
from pathlib import Path

from watchdog.observers import Observer

from .handler import ExpectedHashEventHandler
from .results import CheckResult, Status

_LABELS = {
    Status.MATCH: "OK",
    Status.MISMATCH: "MISMATCH",
    Status.NO_EXPECTED_FILE: "NO EXPECTED FILE",
    Status.UNSTABLE: "UNSTABLE",
}


def print_result(result: CheckResult) -> None:
    print(f"[{_LABELS[result.status]}] {result.relative_path}")


def run(watched_dir: Path, expected_dir: Path) -> None:
    handler = ExpectedHashEventHandler(watched_dir, expected_dir, print_result)
    observer = Observer()
    observer.schedule(handler, str(watched_dir), recursive=True)
    observer.start()
    print(f"Watching {watched_dir} against {expected_dir} (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Watch a folder and verify new files' hashes against an expected folder."
    )
    parser.add_argument("watched_dir", type=Path)
    parser.add_argument("expected_dir", type=Path)
    args = parser.parse_args(argv)

    if not args.watched_dir.is_dir():
        parser.error(f"{args.watched_dir} is not a directory")
    if not args.expected_dir.is_dir():
        parser.error(f"{args.expected_dir} is not a directory")

    run(args.watched_dir, args.expected_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
