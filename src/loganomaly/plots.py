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


LABELS = {
    "severity_rule": "Severity rule\n(FATAL/FAILURE, no labels)",
    "unseen_template_rule": "Unseen-template rule\n(no labels)",
    "known_bad_rule": "Known-bad-template rule\n(train labels)",
    "isolation_forest": "Isolation Forest\n(no labels)",
    "random_forest": "Random Forest\n(train labels)",
}


def benchmark_chart(name: str, window: int) -> None:
    df = pd.read_csv(RESULTS_DIR / f"{name}_w{window}_results.csv").sort_values("f1")
    labels = [LABELS.get(m, m) for m in df["method"]]
    y = range(len(df))
    fig, ax = plt.subplots(figsize=(10, 5.5))
    h = 0.26
    ax.barh([i + h for i in y], df["precision"], h, color="#9ecae9", label="precision")
    ax.barh([i for i in y], df["recall"], h, color="#4C78A8", label="recall")
    ax.barh([i - h for i in y], df["f1"], h, color="#E45756", label="F1")
    for i, f1 in zip(y, df["f1"]):
        ax.text(f1 + 0.01, i - h, f"{f1:.2f}", va="center", fontsize=9, color="#E45756")
    ax.set_yticks(list(y), labels, fontsize=9)
    ax.set_xlim(0, 1.08)
    ax.set_title(f"{name}: anomaly detection on {window}-line windows (chronological 80/20 split)",
                 loc="left", fontsize=11.5)
    ax.legend(frameon=False, loc="lower right")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    out = RESULTS_DIR / f"{name}_w{window}_benchmark.png"
    fig.savefig(out, dpi=160)
    print(f"Saved {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chart", choices=["templates", "benchmark"])
    parser.add_argument("--dataset", default="BGL_2k")
    parser.add_argument("--window", type=int, default=100)
    args = parser.parse_args()
    if args.chart == "templates":
        templates_chart(args.dataset)
    else:
        benchmark_chart(args.dataset, args.window)
