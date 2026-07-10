from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class Status(Enum):
    MATCH = "match"
    MISMATCH = "mismatch"
    NO_EXPECTED_FILE = "no_expected_file"
    UNSTABLE = "unstable"


@dataclass(frozen=True)
class CheckResult:
    relative_path: Path
    status: Status
    actual_hash: str | None = None
    expected_hash: str | None = None
