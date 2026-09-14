"""Load SWE-bench Lite from the local Hugging Face cache and recover gold file paths.

No network, no repo clones. The parquet is already cached; the gold patch tells us
which files a correct solution touches, which is all the localization experiment needs.
"""

from __future__ import annotations

import glob
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

CACHE_GLOB = (
    r"C:\Users\dell\.cache\huggingface\hub"
    r"\datasets--princeton-nlp--SWE-bench_Lite\snapshots\*\data\test-*.parquet"
)

# A unified diff names the file twice; the b/ side is the post-image, which is the
# one that exists after a fix (the a/ side is /dev/null for added files).
DIFF_B_PATH = re.compile(r"^\+\+\+ b/(.+)$", re.MULTILINE)


@dataclass(frozen=True)
class Instance:
    instance_id: str
    repo: str
    base_commit: str
    problem_statement: str
    hints_text: str
    gold_files: tuple[str, ...]

    @property
    def is_single_file(self) -> bool:
        return len(self.gold_files) == 1


def gold_files_from_patch(patch: str) -> tuple[str, ...]:
    """Files a correct patch modifies, in the order they appear in the diff."""
    found = DIFF_B_PATH.findall(patch or "")
    # /dev/null appears for deletions; drop it and de-duplicate while keeping order.
    seen: dict[str, None] = {}
    for path in found:
        path = path.strip()
        if path and path != "/dev/null":
            seen.setdefault(path, None)
    return tuple(seen)


def load(limit: int | None = None) -> list[Instance]:
    matches = glob.glob(CACHE_GLOB)
    if not matches:
        raise FileNotFoundError(
            "SWE-bench Lite parquet not found in the HF cache. Expected at:\n"
            f"  {CACHE_GLOB}"
        )
    frame = pd.read_parquet(sorted(matches)[0])
    rows = []
    for _, row in frame.iterrows():
        rows.append(
            Instance(
                instance_id=row["instance_id"],
                repo=row["repo"],
                base_commit=row["base_commit"],
                problem_statement=row["problem_statement"] or "",
                hints_text=row["hints_text"] or "",
                gold_files=gold_files_from_patch(row["patch"]),
            )
        )
        if limit and len(rows) >= limit:
            break
    return rows


if __name__ == "__main__":
    data = load()
    print(f"instances      : {len(data)}")
    print(f"repos          : {len({d.repo for d in data})}")
    no_gold = [d for d in data if not d.gold_files]
    print(f"no gold file   : {len(no_gold)}")
    counts = [len(d.gold_files) for d in data]
    print(f"single-file fix: {sum(1 for c in counts if c == 1)} "
          f"({sum(1 for c in counts if c == 1) / len(data):.1%})")
    print(f"files per fix  : min {min(counts)}, max {max(counts)}, "
          f"mean {sum(counts) / len(counts):.2f}")
    print("\nsample gold paths:")
    for d in data[:5]:
        print(f"  {d.instance_id:32} {', '.join(d.gold_files)}")
