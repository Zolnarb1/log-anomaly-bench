# Log Anomaly Bench

**Classic ML vs. deep learning vs. LLM-based detectors for system-log anomaly detection, compared on public benchmark logs.**

> 🚧 Work in progress. This README grows with each stage.

## Why
Production systems emit millions of log lines. Finding the few that signal a failure is the core task of AIOps. Many methods exist: unsupervised detectors (Isolation Forest), sequence models (LSTM), and recent LLM-based approaches. This project compares them **on the same data, with the same evaluation**, on three axes:
1. detection quality (precision / recall / F1)
2. speed (lines per second)
3. cost (compute, or API cost for LLMs)

## Data
[Loghub](https://github.com/logpai/loghub) benchmark logs (Zhu et al., ISSRE 2023). Starting with **BGL** (BlueGene/L supercomputer), which carries per-line expert labels.

## Pipeline (planned)
| Stage | Status |
|---|---|
| 1. Download data | ✅ |
| 2. Parse raw logs into templates (Drain) | ✅ |
| 3. Build features over time/count windows | ⏳ |
| 4. Baselines: Isolation Forest, PCA | ⏳ |
| 5. Sequence model: LSTM | ⏳ |
| 6. LLM-based detector | ⏳ |
| 7. Benchmark table + charts | ⏳ |
| 8. Docker: one-command reproduction | ⏳ |

## Results so far

### Parsing (BGL, 2,000-line sample)
Drain reduces 2,000 raw lines to **105 templates**. 7.1% of lines are labelled anomalies. A single template ("data TLB error interrupt") accounts for **42% of all anomalies**, so any model must beat a simple rule-based baseline to be worth its cost.

![Top templates](results/BGL_2k_top_templates.png)

## Quick start
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
python -m loganomaly.download --dataset BGL_2k
python -m loganomaly.parse --dataset BGL_2k
```

## Project layout
```
src/loganomaly/   code (download, parse, features, models, evaluate)
data/raw/         downloaded logs (not committed)
data/processed/   parsed CSVs (not committed)
results/          metrics and charts
```

## Author
Hamza Fakhri, Computer Science engineering student, Polytech Nantes.
