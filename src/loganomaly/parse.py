"""Parse raw BGL logs into structured rows + Drain templates.

A raw BGL line looks like:
    - 1117838570 2005.06.03 R02-M1-N0-C:J12-U11 2005-06-03-15.42.50.675872 R02-M1-N0-C:J12-U11 RAS KERNEL INFO instruction cache parity error corrected
    ^label        ^unix ts  ^date      ^node                ^full time                ^node again           ^type ^comp ^level ^message

Label: "-" means normal; anything else (e.g. "KERNDTLB") is an alert category -> anomaly.

Drain (He et al., ICWS 2017) groups messages that differ only in variable parts:
    "generating core.2275"  and  "generating core.862"   ->   "generating <*>"
Each group is a *template*. Models then work on template IDs instead of free text.

Usage:
    python -m loganomaly.parse --dataset BGL_2k
"""
import argparse

import pandas as pd
from drain3 import TemplateMiner
from drain3.masking import MaskingInstruction
from drain3.template_miner_config import TemplateMinerConfig

from loganomaly import PROCESSED_DIR, RAW_DIR

COLUMNS = ["label", "timestamp", "date", "node", "time", "node_repeat",
           "type", "component", "level", "content"]


def make_miner() -> TemplateMiner:
    config = TemplateMinerConfig()
    # Replace obvious variables before clustering, so templates are cleaner.
    config.masking_instructions = [
        MaskingInstruction(r"0x[0-9a-fA-F]+", "HEX"),
        MaskingInstruction(r"\b\d+\b", "NUM"),
    ]
    config.drain_sim_th = 0.5   # similarity needed to join an existing template
    config.drain_depth = 4      # depth of Drain's prefix tree
    config.profiling_enabled = False
    return TemplateMiner(config=config)


def read_bgl(path) -> pd.DataFrame:
    rows = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.rstrip("\n").split(" ", 9)
            if len(parts) < 10:          # malformed line: keep the text, empty fields
                parts += [""] * (10 - len(parts))
            rows.append(parts)
    df = pd.DataFrame(rows, columns=COLUMNS)
    df["is_anomaly"] = (df["label"] != "-").astype(int)
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
    return df


def parse(name: str) -> None:
    raw = RAW_DIR / f"{name}.log"
    if not raw.exists():
        raise SystemExit(f"{raw} not found. Run: python -m loganomaly.download --dataset {name}")

    df = read_bgl(raw)
    miner = make_miner()
    template_ids = []
    for message in df["content"]:
        result = miner.add_log_message(message)
        template_ids.append(result["cluster_id"])
    df["template_id"] = template_ids

    # Final template text (clusters can generalise as more lines arrive, so read them at the end).
    templates = {c.cluster_id: c.get_template() for c in miner.drain.clusters}
    df["template"] = df["template_id"].map(templates)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = PROCESSED_DIR / f"{name}_structured.csv"
    df.to_csv(out, index=False)

    summary = (df.groupby(["template_id", "template"])
                 .agg(count=("is_anomaly", "size"), anomalies=("is_anomaly", "sum"))
                 .sort_values("count", ascending=False)
                 .reset_index())
    summary.to_csv(PROCESSED_DIR / f"{name}_templates.csv", index=False)

    print(f"Lines:      {len(df):,}")
    print(f"Anomalies:  {df['is_anomaly'].sum():,} ({df['is_anomaly'].mean():.1%})")
    print(f"Templates:  {len(templates):,}")
    print(f"Saved:      {out}")
    print("\nTop 10 templates:")
    with pd.option_context("display.max_colwidth", 70, "display.width", 140):
        print(summary.head(10).to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="BGL_2k")
    parse(parser.parse_args().dataset)
