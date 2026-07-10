from pathlib import Path

from .hashing import hash_file
from .results import CheckResult, Status


def check_against_expected(watched_file: Path, watched_root: Path, expected_root: Path) -> CheckResult:
    relative_path = watched_file.relative_to(watched_root)
    expected_file = expected_root / relative_path

    if not expected_file.is_file():
        return CheckResult(relative_path, Status.NO_EXPECTED_FILE)

    actual_hash = hash_file(watched_file)
    expected_hash = hash_file(expected_file)
    status = Status.MATCH if actual_hash == expected_hash else Status.MISMATCH
    return CheckResult(relative_path, status, actual_hash, expected_hash)
