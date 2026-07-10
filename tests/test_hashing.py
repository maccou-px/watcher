import threading
import time

from watcher.hashing import hash_file, wait_until_stable


def test_hash_file_matches_known_sha256(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello world")
    assert hash_file(file_path) == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"


def test_hash_file_differs_for_different_content(tmp_path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("hello")
    b.write_text("world")
    assert hash_file(a) != hash_file(b)


def test_wait_until_stable_returns_true_for_static_file(tmp_path):
    file_path = tmp_path / "static.txt"
    file_path.write_text("done")
    assert wait_until_stable(file_path, poll_interval=0.01, required_stable_polls=2, timeout=1.0) is True


def test_wait_until_stable_times_out_for_growing_file(tmp_path):
    file_path = tmp_path / "growing.txt"
    file_path.write_text("")
    stop = threading.Event()

    def keep_growing():
        with file_path.open("a") as f:
            while not stop.is_set():
                f.write("x")
                f.flush()
                time.sleep(0.02)

    thread = threading.Thread(target=keep_growing)
    thread.start()
    try:
        assert wait_until_stable(file_path, poll_interval=0.01, required_stable_polls=3, timeout=0.3) is False
    finally:
        stop.set()
        thread.join()
