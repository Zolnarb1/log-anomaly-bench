import numpy as np
import pandas as pd

from loganomaly.features import chronological_split, make_windows
from loganomaly.parse import make_miner


def events(template_ids, anomalies):
    return pd.DataFrame({
        "timestamp": range(len(template_ids)),
        "level": ["INFO"] * len(template_ids),
        "is_anomaly": anomalies,
        "template_id": template_ids,
    })


def test_windows_count_templates_and_label_any_anomaly():
    ev = events([1, 1, 2, 3, 3, 3], [0, 0, 0, 0, 1, 0])
    w = make_windows(ev, size=3)
    assert w.counts.shape == (2, 3)                     # 2 windows, 3 distinct templates
    assert w.counts.toarray().tolist() == [[2, 1, 0], [0, 0, 3]]
    assert w.labels.tolist() == [0, 1]                   # window 2 holds the anomaly


def test_last_partial_window_is_kept():
    w = make_windows(events([1] * 5, [0] * 5), size=2)
    assert len(w.labels) == 3
    assert w.counts.sum() == 5


def test_split_is_chronological():
    assert chronological_split(10, 0.8) == 8


def test_drain_masks_numbers_into_one_template():
    miner = make_miner()
    a = miner.add_log_message("generating core.2275")["cluster_id"]
    b = miner.add_log_message("generating core.862")["cluster_id"]
    assert a == b
    assert "<NUM>" in miner.drain.id_to_cluster[a].get_template()
