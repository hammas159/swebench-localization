# Problems hit while building this

[<- back to README](../README.md)

## 1. A hardcoded cache path

`src/data.py` pointed at an absolute `C:\Users\...` path. The repo worked on exactly one
machine on earth, and a clone by anyone else failed immediately.

**Fix:** resolve `HF_HUB_CACHE`, then `HF_HOME/hub`, then the platform default - at call
time, not import time - with a download fallback and an error message that names every
location searched.

**Tests:** `test_cache_roots_honour_env`, `test_find_parquet_returns_none_when_absent`,
`test_find_parquet_finds_a_planted_file`

## 2. CI failed on the very first push

`setup-uv` defaults its cache to a `**/uv.lock` glob and **errors out** when nothing
matches. Not a cache miss - a hard job failure. No lock file is committed here, so every
run died before installing anything.

**Fix:** keyed the cache on `pyproject.toml`, which exists and changes when dependencies do.

## 3. Lint drift would have broken CI again

`ruff` found 4 errors and 4 unformatted files before the first push - the same drift that
had previously reddened CI on another repository.

**Fix:** ran `ruff check --fix` and `ruff format` before pushing, and pinned ruff to a
minor range in `pyproject.toml`. The *formatter* changes between minor versions, so an open
bound means CI reformats differently from whatever version the code was committed with, and
the lint step fails on files nobody touched.

## 4. Substring matching overcounted

The module-stem match was a plain substring, so `separable` matched inside `inseparable`.
That inflated the "module name only" tier with instances that never mentioned the module
at all.

**Fix:** word-boundary regex, with a test asserting the `inseparable` case.

## 5. Phase 2 blocked by the network

Scoring retrieval needs each repository's file list at its `base_commit`. The GitHub trees
API call timed out.

**Fix:** recorded as explicitly not-done rather than estimated. The README says Phase 2 is
not started, and no retrieval number appears anywhere.

## 6. A unicode crash during inspection

Printing a non-ASCII character to a `cp1252` Windows console killed an inspection script
mid-run. Not a repo bug, but it cost time.

**Fix:** `PYTHONIOENCODING=utf-8`, and non-ASCII kept out of program output.
