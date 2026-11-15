"""Charts for the README and progress posts.

Usage:
    python -m loganomaly.plots templates --dataset BGL_2k
"""
import argparse
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from loganomaly import PROCESSED_DIR, RESULTS_DIR

NORMAL, ANOMALY = "#4C78A8", "#E45756"


def templates_chart(name: str, top: int = 15) -> None:
    summary = pd.read_csv(PROCESSED_DIR / f"{name}_templates.csv").head(top).iloc[::-1]
    labels = [textwrap.shorten(t, 55, placeholder="…") for t in summary["template"]]
    normal = summary["count"] - summary["anomalies"]

    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.barh(labels, normal, color=NORMAL, label="normal")
    ax.barh(labels, summary["anomalies"], left=normal, color=ANOMALY, label="anomaly")
    ax.set_xlabel("number of log lines")
    ax.set_title(f"{name}: top {top} log templates found by Drain\n"
                 f"(2,000 raw lines → {len(pd.read_csv(PROCESSED_DIR / f'{name}_templates.csv'))} templates)",
                 loc="left", fontsize=12)
    ax.legend(frameon=False, loc="lower right")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="y", labelsize=8.5)
    fig.tight_layout()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"{name}_top_templates.png"
    fig.savefig(out, dpi=160)
    print(f"Saved {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chart", choices=["templates"])
    parser.add_argument("--dataset", default="BGL_2k")
    args = parser.parse_args()
    templates_chart(args.dataset)
