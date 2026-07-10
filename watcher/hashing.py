import hashlib
import time
from pathlib import Path

_CHUNK_SIZE = 65536


def hash_file(path: Path, algorithm: str = "sha256") -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(_CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def wait_until_stable(
    path: Path,
    poll_interval: float = 0.1,
    required_stable_polls: int = 3,
    timeout: float = 10.0,
) -> bool:
    """Poll the file's size until it stops changing for `required_stable_polls`
    consecutive checks, to avoid hashing a file that's still being written.
    Returns False on timeout (e.g. file never appears or keeps growing)."""
    deadline = time.monotonic() + timeout
    last_size = -1
    stable_count = 0
    while time.monotonic() < deadline:
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            size = -1
        if size == last_size:
            stable_count += 1
            if stable_count >= required_stable_polls:
                return True
        else:
            stable_count = 0
            last_size = size
        time.sleep(poll_interval)
    return False
