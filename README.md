<h1 align="center">swebench-localization</h1>
<p align="center"><i>Is the answer even in the question?</i></p>

<p align="center">
  <a href="docs/RESULTS.md">Results</a> &middot;
  <a href="docs/METHOD.md">Method</a> &middot;
  <a href="docs/PROBLEMS.md">Problems hit</a> &middot;
  <a href="docs/LIMITATIONS.md">Limitations</a> &middot;
  <a href="docs/FUTURE.md">Future work</a> &middot;
  <a href="#reproduce">Reproduce</a>
</p>

<p align="center">
  <a href="https://github.com/hammas159/swebench-localization/actions/workflows/ci.yml"><img src="https://github.com/hammas159/swebench-localization/actions/workflows/ci.yml/badge.svg" alt="ci"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/hammas159/swebench-localization" alt="license"></a>
  <img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="python">
  <img src="https://img.shields.io/badge/tests-16%20passing-brightgreen" alt="tests">
  <img src="https://img.shields.io/badge/data-SWE--bench%20Lite-orange" alt="data">
  <img src="https://img.shields.io/badge/downloads%20needed-1.2%20MB-success" alt="size">
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/badge/lint-ruff-261230" alt="ruff"></a>
</p>

---

> ### 51.3% of SWE-bench Lite never names the file you have to fix.

SWE-bench is reported as **one number**. But solving an instance needs two different
things - **find the file**, then **write the patch** - and a single score cannot say which
one failed.

A model that fails on an issue that never names the file has not failed at *reasoning
about code*. It has failed at **search**. Those are different problems with different
fixes.

---

## The result

All 300 instances. Every one is a single-file fix, so localization is exactly *"rank the
one correct file first"*.

| How the gold file is referenced | Instances | Share |
|---|---:|---:|
| Full path, verbatim | 51 | 17.0% |
| Filename only | 18 | 6.0% |
| Module name only | 77 | 25.7% |
| **Never mentioned at all** | **154** | **51.3%** |

### Two more findings that fell out of it

**Hints change the task.** Including `hints_text` drops "never mentioned" from **51.3% to
38.0%** and doubles the full-path cases. Results using hints are not comparable to results
without them - and papers do not always say which they used.

**The aggregate score hides a repo effect.** Difficulty ranges from **astropy 16.7%** to
**sphinx 87.5%**, and `django/django` alone is 38% of the benchmark.

&#128202; **[Full tables, per-repo breakdown, and the hints comparison &rarr;](docs/RESULTS.md)**

---

## How it works

```mermaid
flowchart LR
    A["SWE-bench Lite<br/>300 instances - 1.2 MB"] --> B["parse gold files<br/>from reference patches"]
    B --> C{"single-file fix?"}
    C -->|"300 / 300"| D["match gold path<br/>against issue text"]
    D --> E["full path 17.0%"]
    D --> F["filename 6.0%"]
    D --> G["module name 25.7%"]
    D --> H["never mentioned 51.3%"]
    H --> I["retrieval must<br/>INFER the location"]

    style H fill:#dc2626,color:#fff
    style I fill:#dc2626,color:#fff
```

Matching is a strict ladder - full path, then basename, then a word-boundary regex on the
module stem - so each instance lands in exactly one tier and the strongest form present
wins.

&#128269; **[How the gold files and matching actually work &rarr;](docs/METHOD.md)**

---

## Why this matters

A SWE-bench agent that scores badly is usually assumed to need a bigger model. This says:
**establish first how much of the failure was ever a retrieval problem.** For 154 of 300
instances, no amount of code reasoning helps until the right file has been found.

It also makes a model-size comparison far more informative - you can say **which half** the
bigger model improved.

---

## Reproduce

```bash
python src/data.py              # dataset integrity + gold file extraction
python src/mention_analysis.py  # every number in this README
pytest -q                       # 16 tests, no network, no dataset needed
```

Nothing is hard-coded. Every figure is recomputed from the same functions.

---

## Input

![input](docs/images/input.png)

## Output

![output](docs/images/output.png)

*Half the benchmark is a retrieval problem wearing a reasoning problem's clothes. When the
issue never names the file, a single pass@1 score cannot tell you whether the model reasoned
badly or was simply shown the wrong file — and a bigger model fed the wrong file still fails.*

---

## Also worth reading

| | |
|---|---|
| &#128202; **[Results](docs/RESULTS.md)** | Full tables, per-repo difficulty, hints comparison |
| &#128269; **[Method](docs/METHOD.md)** | Gold file extraction, the matching ladder, determinism |
| &#128736; **[Problems hit](docs/PROBLEMS.md)** | A hardcoded path, a broken CI cache, and an overcounting regex |
| &#9888; **[Limitations](docs/LIMITATIONS.md)** | What Phase 1 does and does not establish |
| &#128640; **[Future work](docs/FUTURE.md)** | Phase 2 retrieval scoring, BM25 vs embeddings vs LLM |

---

## Status

&#9989; **Phase 1 complete** - benchmark discoverability measured.

&#128308; **Phase 2 not started** - retrieval baselines scored as recall@k. See
[FUTURE.md](docs/FUTURE.md).

## Layout

```
src/data.py               load from HF cache, parse gold files from patches
src/mention_analysis.py   discoverability tiers + per-repo breakdown
tests/                    16 tests, no network, no dataset
docs/                     detailed documentation
data/sources.json         provenance, counts, checksum
```

## Stack

`Python 3.11+` &middot; `pandas` &middot; `pyarrow`
&middot; `pytest` &middot; `ruff` &middot; `GitHub Actions` &middot; dataset via
`Hugging Face Hub`

## Keywords

SWE-bench &middot; SWE-bench Lite &middot; bug localization &middot; fault localization
&middot; code retrieval &middot; LLM benchmark &middot; benchmark evaluation &middot;
benchmark contamination &middot; retrieval vs reasoning &middot; automated program repair
&middot; issue-to-file mapping &middot; coding agent evaluation &middot; AI software
engineering &middot; LLM evaluation harness &middot; reproducible benchmarks &middot; BM25

## References

Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., & Narasimhan, K.
**SWE-bench: Can Language Models Resolve Real-World GitHub Issues?** *ICLR 2024.*

&#9888; Citation written from the standard reference - confirm against the paper before
relying on it.

## Licence

MIT - see [LICENSE](LICENSE).
