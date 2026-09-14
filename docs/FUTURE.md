# Future work

[<- back to README](../README.md)

## 1. Phase 2 - actual retrieval scoring

The main unfinished piece. Fetch each repository's file tree at its `base_commit` via the
GitHub trees API - **paths only, no file contents**, so the download stays small - then
score three retrievers as recall@k:

- **BM25** over file paths and contents
- **Embeddings** (`nomic-embed-text` locally)
- **LLM-as-locator**, the model asked directly which file to change

**BM25 may well win.** If it does, that is the finding: the expensive option did not earn
its cost.

## 2. Condition patch validity on localization

The number that actually matters: *given the right file was found, how often is the patch
correct?* That separates retrieval failure from reasoning failure cleanly, and it is the
metric a model-size comparison should move.

## 3. Extend to full SWE-bench

2,294 instances, many multi-file. Checking whether Lite's 100%-single-file property
distorts these proportions is the obvious validity check on everything here.

## 4. Correlate difficulty with issue length

`problem_statement` spans 230 to 24,770 characters. Long prose naming no file is likely the
hardest tier, and that is directly testable with data already loaded.

## 5. Semantic discoverability, not just string matching

An issue quoting a unique error message effectively names the file without naming it.
Measuring that needs retrieval rather than string comparison - and the gap between the two
is itself a result.

## 6. Report per-repo scores by default

Given the 16.7%-87.5% spread, any SWE-bench evaluation should break results down by
repository. A single aggregate is partly a measurement of benchmark composition.
