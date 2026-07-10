from pathlib import Path

from watcher.comparator import check_against_expected
from watcher.results import Status


def test_match(tmp_path):
    watched = tmp_path / "watched"
    expected = tmp_path / "expected"
    watched.mkdir()
    expected.mkdir()
    (watched / "a.txt").write_text("same")
    (expected / "a.txt").write_text("same")

    result = check_against_expected(watched / "a.txt", watched, expected)
    assert result.status is Status.MATCH
    assert result.actual_hash == result.expected_hash


def test_mismatch(tmp_path):
    watched = tmp_path / "watched"
    expected = tmp_path / "expected"
    watched.mkdir()
    expected.mkdir()
    (watched / "a.txt").write_text("actual")
    (expected / "a.txt").write_text("expected")

    result = check_against_expected(watched / "a.txt", watched, expected)
    assert result.status is Status.MISMATCH
    assert result.actual_hash != result.expected_hash


def test_no_expected_file(tmp_path):
    watched = tmp_path / "watched"
    expected = tmp_path / "expected"
    watched.mkdir()
    expected.mkdir()
    (watched / "a.txt").write_text("actual")

    result = check_against_expected(watched / "a.txt", watched, expected)
    assert result.status is Status.NO_EXPECTED_FILE


def test_nested_relative_path_is_preserved(tmp_path):
    watched = tmp_path / "watched"
    expected = tmp_path / "expected"
    (watched / "nested").mkdir(parents=True)
    (expected / "nested").mkdir(parents=True)
    (watched / "nested" / "b.txt").write_text("x")
    (expected / "nested" / "b.txt").write_text("x")

    result = check_against_expected(watched / "nested" / "b.txt", watched, expected)
    assert result.status is Status.MATCH
    assert result.relative_path == Path("nested/b.txt")
