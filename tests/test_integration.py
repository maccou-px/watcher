import time

from watchdog.observers import Observer

from watcher.handler import ExpectedHashEventHandler
from watcher.results import Status


def _run_observer(watched_dir, expected_dir, results):
    handler = ExpectedHashEventHandler(watched_dir, expected_dir, results.append)
    observer = Observer()
    observer.schedule(handler, str(watched_dir), recursive=True)
    observer.start()
    return observer


def _wait_for(results, count, timeout=8.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if len(results) >= count:
            return True
        time.sleep(0.05)
    return False


def test_matching_file_created_in_watched_dir_is_detected_as_match(tmp_path):
    watched = tmp_path / "watched"
    expected = tmp_path / "expected"
    watched.mkdir()
    expected.mkdir()
    (expected / "output.txt").write_text("golden content")

    results = []
    observer = _run_observer(watched, expected, results)
    try:
        (watched / "output.txt").write_text("golden content")
        assert _wait_for(results, 1), "watcher did not report a result in time"
    finally:
        observer.stop()
        observer.join()

    assert results[0].status is Status.MATCH


def test_mismatching_file_created_in_watched_dir_is_detected_as_mismatch(tmp_path):
    watched = tmp_path / "watched"
    expected = tmp_path / "expected"
    watched.mkdir()
    expected.mkdir()
    (expected / "output.txt").write_text("golden content")

    results = []
    observer = _run_observer(watched, expected, results)
    try:
        (watched / "output.txt").write_text("different content")
        assert _wait_for(results, 1)
    finally:
        observer.stop()
        observer.join()

    assert results[0].status is Status.MISMATCH


def test_file_with_no_expected_counterpart_is_flagged(tmp_path):
    watched = tmp_path / "watched"
    expected = tmp_path / "expected"
    watched.mkdir()
    expected.mkdir()

    results = []
    observer = _run_observer(watched, expected, results)
    try:
        (watched / "unexpected.txt").write_text("surprise")
        assert _wait_for(results, 1)
    finally:
        observer.stop()
        observer.join()

    assert results[0].status is Status.NO_EXPECTED_FILE
