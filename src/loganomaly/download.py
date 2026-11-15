"""Download Loghub log datasets.

Usage:
    python -m loganomaly.download --dataset BGL_2k
"""
import argparse
import urllib.request

from loganomaly import RAW_DIR

# Loghub hosts small 2k-line samples on GitHub (good for development).
# Full datasets live on Zenodo; they are added once the pipeline works on the samples.
DATASETS = {
    "BGL_2k": "https://raw.githubusercontent.com/logpai/loghub/master/BGL/BGL_2k.log",
}


def download(name: str) -> None:
    if name not in DATASETS:
        raise SystemExit(f"Unknown dataset {name!r}. Choose from: {', '.join(DATASETS)}")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    target = RAW_DIR / f"{name}.log"
    if target.exists():
        print(f"Already downloaded: {target}")
        return
    print(f"Downloading {DATASETS[name]} ...")
    urllib.request.urlretrieve(DATASETS[name], target)
    n_lines = sum(1 for _ in target.open(encoding="utf-8", errors="replace"))
    print(f"Saved {n_lines:,} lines to {target}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="BGL_2k", choices=list(DATASETS))
    download(parser.parse_args().dataset)
