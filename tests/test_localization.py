"""Tests that never touch the network or the dataset.

Every case below is built from a constructed diff or a fake cache root, so CI stays
green whether or not Hugging Face is reachable - a dataset outage should not look
like a code failure.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from data import Instance, _hf_cache_roots, find_parquet, gold_files_from_patch
from mention_analysis import tier_for

# --- gold file extraction ------------------------------------------------------------

SIMPLE = """--- a/astropy/modeling/separable.py
+++ b/astropy/modeling/separable.py
@@ -240,7 +240,7 @@ def _cstack(left, right):
-        cright[-right.shape[0]:, -right.shape[1]:] = 1
+        cright[-right.shape[0]:, -right.shape[1]:] = right
"""


def test_extracts_single_file():
    assert gold_files_from_patch(SIMPLE) == ("astropy/modeling/separable.py",)


def test_extracts_multiple_files_in_order():
    patch = (
        SIMPLE
        + """--- a/zzz/other.py
+++ b/zzz/other.py
@@ -1 +1 @@
-a
+b
"""
    )
    assert gold_files_from_patch(patch) == (
        "astropy/modeling/separable.py",
        "zzz/other.py",
    )


def test_deduplicates_repeated_file():
    """A file with several hunks is named once per hunk header, not once per file."""
    patch = SIMPLE + SIMPLE
    assert gold_files_from_patch(patch) == ("astropy/modeling/separable.py",)


def test_drops_dev_null_for_deletions():
    patch = """--- a/gone.py
+++ /dev/null
@@ -1 +0,0 @@
-x
"""
    assert gold_files_from_patch(patch) == ()


def test_empty_and_none_are_safe():
    assert gold_files_from_patch("") == ()
    assert gold_files_from_patch(None) == ()


# --- discoverability tiers -----------------------------------------------------------


def make(gold: str) -> Instance:
    return Instance("i", "r", "c", "", "", (gold,))


GOLD = "astropy/modeling/separable.py"


@pytest.mark.parametrize(
    "text,expected",
    [
        (f"crash in {GOLD} line 240", "full_path"),
        ("the bug is in separable.py somewhere", "basename"),
        ("something in the separable module", "stem_only"),
        ("the model output is transposed", "not_mentioned"),
    ],
)
def test_tiers(text, expected):
    assert tier_for(make(GOLD), text) == expected


def test_stem_match_respects_word_boundaries():
    """`separable` must not match inside `inseparable` - that would overcount."""
    assert tier_for(make(GOLD), "the axes are inseparable here") == "not_mentioned"


def test_windows_path_separators_still_match():
    text = r"see astropy\modeling\separable.py"
    assert tier_for(make(GOLD), text) == "full_path"


def test_full_path_beats_basename():
    """Tiers are ranked: the strongest form present must win."""
    assert tier_for(make(GOLD), f"separable.py and also {GOLD}") == "full_path"


# --- cache resolution ----------------------------------------------------------------


def test_cache_roots_honour_env(monkeypatch, tmp_path):
    monkeypatch.setenv("HF_HUB_CACHE", str(tmp_path / "explicit"))
    monkeypatch.setenv("HF_HOME", str(tmp_path / "home"))
    roots = _hf_cache_roots()
    assert roots[0] == tmp_path / "explicit"
    assert roots[1] == tmp_path / "home" / "hub"
    # The platform default is always the last resort, never the only option.
    assert roots[-1] == Path.home() / ".cache" / "huggingface" / "hub"


def test_find_parquet_returns_none_when_absent(monkeypatch, tmp_path):
    """No cache must give None, not a crash - the caller decides how to recover."""
    monkeypatch.setenv("HF_HUB_CACHE", str(tmp_path / "nothing-here"))
    monkeypatch.setenv("HF_HOME", str(tmp_path / "nothing-here-either"))
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    assert find_parquet() is None


def test_find_parquet_finds_a_planted_file(monkeypatch, tmp_path):
    planted = tmp_path / "datasets--princeton-nlp--SWE-bench_Lite" / "snapshots" / "abc123" / "data"
    planted.mkdir(parents=True)
    target = planted / "test-00000-of-00001.parquet"
    target.write_bytes(b"")
    monkeypatch.setenv("HF_HUB_CACHE", str(tmp_path))
    assert find_parquet() == target


def test_instance_single_file_flag():
    assert make(GOLD).is_single_file
    assert not Instance("i", "r", "c", "", "", ("a.py", "b.py")).is_single_file
