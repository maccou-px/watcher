# watcher

Watches a folder for newly created files and checks each one's hash against
a same-relative-path file in an "expected" (golden) folder.

## Run

```bash
uv run python main.py <watched_dir> <expected_dir>
```

Create/copy a file into `<watched_dir>`; the watcher prints one of:

- `[OK] <path>` — hash matches the file at the same relative path in `<expected_dir>`
- `[MISMATCH] <path>` — hash differs
- `[NO EXPECTED FILE] <path>` — no counterpart exists in `<expected_dir>`
- `[UNSTABLE] <path>` — file size never stopped changing (still being written)

## How it works

- `watcher/hashing.py` — sha256 hashing + polling for file-size stability before hashing
- `watcher/comparator.py` — looks up `expected_dir/<relative_path>` and compares hashes
- `watcher/handler.py` — `watchdog` event handler wiring creation events to the checks above
- `watcher/cli.py` — starts a `watchdog` `Observer` on `watched_dir`

## Test

```bash
uv run pytest
```

Includes real end-to-end tests: a `watchdog` observer runs against `tmp_path`
directories and actual files are created on disk to prove the watch → hash →
compare pipeline works, not just its unit pieces.
