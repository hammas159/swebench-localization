"""Interactive view of how discoverable SWE-bench Lite's gold files actually are.

Nothing here is precomputed. The app calls the same functions the analysis scripts
call, against the same cached parquet, so every number on screen is recomputed live
from the real benchmark. Change the matching rule in the sidebar and the whole
report moves.

Run:  streamlit run ui/app.py
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from data import load
from mention_analysis import TIERS, tier_for

st.set_page_config(page_title="SWE-bench localization", layout="wide")

BLUE, AMBER, GREY, RED, GREEN = "#2563eb", "#f59e0b", "#94a3b8", "#dc2626", "#16a34a"
TIER_COLOR = {"full_path": GREEN, "basename": BLUE, "stem_only": AMBER, "not_mentioned": RED}
TIER_LABEL = {
    "full_path": "full path given",
    "basename": "filename only",
    "stem_only": "module name only",
    "not_mentioned": "never mentioned",
}


@st.cache_data
def get_data():
    return load()


data = get_data()

st.title("Is the answer even in the question?")
st.caption(
    "SWE-bench Lite is scored as one number, but solving an instance needs two "
    "different things: **find the file**, then **write the patch**. This measures the "
    "first one - before any model is involved. All 300 instances are single-file "
    "fixes, so localization is exactly 'rank the one correct file first'."
)

# --- controls ------------------------------------------------------------------------

with st.sidebar:
    st.header("What may the retriever read?")
    use_hints = st.checkbox("Include `hints_text`", value=False)
    st.caption(
        "`hints_text` is discussion from the issue thread. It makes localization much "
        "easier - but it is arguably a different, easier task than the issue alone. "
        "Toggle it and watch the red bar move."
    )
    repos = sorted({d.repo for d in data})
    chosen = st.multiselect("Repositories", repos, default=repos)

subset = [d for d in data if d.repo in chosen]
if not subset:
    st.warning("Select at least one repository.")
    st.stop()


def text_of(inst) -> str:
    return inst.problem_statement + ("\n" + inst.hints_text if use_hints else "")


tiers = Counter(tier_for(d, text_of(d)) for d in subset)
total = len(subset)
hidden = tiers["not_mentioned"]

# --- headline ------------------------------------------------------------------------

a, b, c, d_ = st.columns(4)
a.metric("Instances", f"{total}")
b.metric("Gold file named outright", f"{tiers['full_path'] / total:.1%}")
c.metric("Never mentioned", f"{hidden / total:.1%}")
d_.metric("Repos", f"{len({x.repo for x in subset})}")

if hidden / total > 0.5:
    st.error(
        f"**{hidden} of {total} instances ({hidden / total:.1%}) never name the file "
        "anywhere in the text** - not the path, not the filename, not even the module "
        "name. For these, a retriever has to infer the location from described "
        "behaviour. A model that fails here has not failed at *reasoning about code*; "
        "it has failed at *search*, and the benchmark's single score cannot tell the "
        "two apart."
    )
else:
    st.success(
        f"{total - hidden} of {total} ({(total - hidden) / total:.1%}) mention the gold "
        "file in some form."
    )

# --- distribution --------------------------------------------------------------------

left, right = st.columns([3, 2])

with left:
    st.subheader("How the gold file is referenced")
    tier_frame = pd.DataFrame(
        [
            {"tier": TIER_LABEL[t], "instances": tiers[t], "share": tiers[t] / total, "key": t}
            for t in TIERS
        ]
    )
    bars = (
        alt.Chart(tier_frame)
        .mark_bar()
        .encode(
            x=alt.X("tier:N", sort=[TIER_LABEL[t] for t in TIERS], title=None),
            y=alt.Y("instances:Q", title="instances"),
            color=alt.Color(
                "key:N",
                legend=None,
                scale=alt.Scale(domain=TIERS, range=[TIER_COLOR[t] for t in TIERS]),
            ),
            tooltip=["tier", "instances", alt.Tooltip("share:Q", format=".1%")],
        )
    )
    labels = bars.mark_text(dy=-8, fontSize=13).encode(
        text=alt.Text("share:Q", format=".1%"), color=alt.value("#334155")
    )
    st.altair_chart((bars + labels).properties(height=340), width="stretch")

with right:
    st.subheader("Difficulty tiers")
    st.dataframe(
        [{"tier": TIER_LABEL[t], "n": tiers[t], "share": f"{tiers[t] / total:.1%}"} for t in TIERS],
        hide_index=True,
        width="stretch",
    )

# --- per-repo skew -------------------------------------------------------------------

st.subheader("The aggregate score hides a repo effect")
st.caption(
    "If 'never mentioned' varies this much between repositories, then an aggregate "
    "SWE-bench score is partly measuring which repos the benchmark happens to contain."
)

rows = []
for repo in sorted({x.repo for x in subset}):
    items = [x for x in subset if x.repo == repo]
    miss = sum(tier_for(x, text_of(x)) == "not_mentioned" for x in items)
    rows.append(
        {"repo": repo, "instances": len(items), "never_mentioned": miss, "rate": miss / len(items)}
    )
rows.sort(key=lambda r: -r["rate"])

overall = hidden / total
repo_frame = pd.DataFrame(rows)
order = [r["repo"] for r in rows]

repo_bars = (
    alt.Chart(repo_frame)
    .mark_bar()
    .encode(
        x=alt.X("repo:N", sort=order, title=None, axis=alt.Axis(labelAngle=-40)),
        y=alt.Y("rate:Q", title="share never mentioning the gold file", axis=alt.Axis(format="%")),
        color=alt.condition(alt.datum.rate > 0.5, alt.value(RED), alt.value(BLUE)),
        tooltip=["repo", "instances", "never_mentioned", alt.Tooltip("rate:Q", format=".1%")],
    )
)
repo_labels = repo_bars.mark_text(dy=-8, fontSize=11).encode(
    text=alt.Text("rate:Q", format=".0%"), color=alt.value("#334155")
)
mean_line = (
    alt.Chart(pd.DataFrame({"y": [overall]}))
    .mark_rule(strokeDash=[6, 4], color=GREY, size=2)
    .encode(y="y:Q")
)
st.altair_chart(
    (repo_bars + repo_labels + mean_line).properties(height=400),
    width="stretch",
)
st.caption(f"Dashed line: overall rate across the selected repos ({overall:.1%}).")

# --- inspect -------------------------------------------------------------------------

st.subheader("Look at one instance")
tier_filter = st.selectbox(
    "Filter by tier", ["all", *TIERS], format_func=lambda t: TIER_LABEL.get(t, "all")
)
pool = [d for d in subset if tier_filter == "all" or tier_for(d, text_of(d)) == tier_filter]
st.caption(f"{len(pool)} instances match.")

if pool:
    pick = st.selectbox("Instance", pool, format_func=lambda d: d.instance_id)
    tier = tier_for(pick, text_of(pick))
    x, y = st.columns([1, 3])
    x.metric("Tier", TIER_LABEL[tier])
    x.write(f"**Repo**  \n`{pick.repo}`")
    x.write(f"**Gold file**  \n`{pick.gold_files[0]}`")
    x.write(f"**Issue length**  \n{len(pick.problem_statement):,} chars")
    y.markdown("**Problem statement**")
    y.code(pick.problem_statement[:4000] or "(empty)", language="text")
    if use_hints and pick.hints_text:
        y.markdown("**Hints**")
        y.code(pick.hints_text[:2000], language="text")

st.divider()
st.caption(
    "Data: `princeton-nlp/SWE-bench_Lite` (test split, 300 instances), read from the "
    "local Hugging Face cache. Gold files are parsed from each instance's reference "
    "patch. Matching is exact string / word-boundary matching - deterministic, no model, "
    "no seed."
)
