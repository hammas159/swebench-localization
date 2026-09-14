# Method

[<- back to README](../README.md)

## Extracting the gold files

A unified diff names each file twice. The `+++ b/<path>` line is the post-image - the file
as it exists after the fix - so those lines are parsed from each instance's reference
patch.

`/dev/null` entries (file deletions) are dropped, and paths are de-duplicated while
preserving order, because a file with several hunks appears once per hunk header.

Gold files come from the **reference patch**, never from any model output.

## The matching ladder

For each instance, the gold path is matched against the issue text in three descending
forms. The strongest form present wins, so every instance lands in exactly one tier:

| Tier | Test |
|---|---|
| `full_path` | the complete path appears as a substring |
| `basename` | the filename (e.g. `separable.py`) appears |
| `stem_only` | a word-boundary regex on the module name (e.g. `separable`) |
| `not_mentioned` | none of the above |

## Word boundaries matter

The stem match uses `\bstem\b`, not a plain substring. Without it, `separable` matches
inside `inseparable` and the "module name only" tier is inflated.

`test_stem_match_respects_word_boundaries` asserts exactly that case.

## Path separators

The haystack has backslashes normalised to forward slashes before matching, so an issue
written on Windows still matches a POSIX-style gold path.

## Determinism

No model, no embeddings, no random seed. Exact string and regex matching only, so the same
input always produces the same table and the result is reproducible by anyone.

## Where the data comes from

`princeton-nlp/SWE-bench_Lite`, test split, read from the local Hugging Face cache.
Resolution order is `HF_HUB_CACHE`, then `HF_HOME/hub`, then the platform default, with a
fallback to downloading the 1.2 MB split if none of those hold it.
