from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEventHandler

from .comparator import check_against_expected
from .hashing import wait_until_stable
from .results import CheckResult, Status


class ExpectedHashEventHandler(FileSystemEventHandler):
    def __init__(
        self,
        watched_root: Path,
        expected_root: Path,
        on_result: Callable[[CheckResult], None],
    ):
        self.watched_root = watched_root.resolve()
        self.expected_root = expected_root.resolve()
        self.on_result = on_result

    def on_created(self, event):
        if event.is_directory:
            return
        # Resolve because the OS may report a realpath (e.g. macOS FSEvents
        # resolving /tmp -> /private/tmp) that differs from watched_root's
        # original spelling.
        self._handle(Path(event.src_path).resolve())

    def _handle(self, file_path: Path) -> None:
        if not wait_until_stable(file_path):
            self.on_result(CheckResult(file_path.relative_to(self.watched_root), Status.UNSTABLE))
            return
        result = check_against_expected(file_path, self.watched_root, self.expected_root)
        self.on_result(result)
