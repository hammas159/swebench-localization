# Limitations

[<- back to README](../README.md)

## This measures discoverability, not retrieval

The headline says the gold file is not *mentioned* in 51.3% of issues. It does **not** say
a retriever fails on those - a good retriever may well find the file from described
behaviour without the name ever appearing.

What the number establishes is that for those instances, **retrieval has real work to do**,
and a benchmark reporting one score cannot show whether that work succeeded.

Phase 2 would measure actual retrieval. It is not done. See [FUTURE.md](FUTURE.md).

## Lite is not SWE-bench

`SWE-bench_Lite` is 300 instances, and **every one is a single-file fix**. Full SWE-bench
has 2,294 instances, many touching several files. Localization there is a harder problem,
and these proportions may not carry over.

## String matching is a floor, not a measure of difficulty

An issue can make the file obvious without naming it - quoting a distinctive error message
or a function unique to one file. Those count as `not_mentioned` here.

So 51.3% is an **upper bound on how many issues hand you the answer**, not a claim that the
other half are equally hard.

## Small per-repo samples

Four of the twelve repositories have fewer than 10 instances. `pallets/flask` has three.
Their individual rates are noisy; the **spread** across repositories is the finding, not any
single row.

## Hints are ambiguous by nature

`hints_text` is issue-thread discussion. Some of it is genuine context available before a
fix; some may reference the eventual solution. This repo reports both settings and does not
try to adjudicate which is legitimate.
