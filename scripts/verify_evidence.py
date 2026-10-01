"""Check the report's arithmetic against its frozen Kaggle API snapshot."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "evidence/kaggle_results_2026-10-01.json"


def main() -> None:
    evidence = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    by_ref = {row["ref"]: row for row in evidence["submissions"]}
    assert len(by_ref) == len(evidence["submissions"])
    baseline, final, other_final, private_counterexample = (
        by_ref[56069668], by_ref[56553387], by_ref[56570663], by_ref[56198176]
    )
    score = lambda row, key: Decimal(row[key])
    assert score(final, "publicScore") == score(other_final, "publicScore") == Decimal("0.949")
    assert score(final, "privateScore") == Decimal(evidence["team"]["private_score"])
    assert score(private_counterexample, "privateScore") > score(final, "privateScore")
    assert score(private_counterexample, "publicScore") < score(final, "publicScore")
    public_delta = score(final, "publicScore") - score(baseline, "publicScore")
    private_delta = score(final, "privateScore") - score(baseline, "privateScore")
    assert public_delta == private_delta == Decimal("0.008")
    print(f"P0 → P58: Public +{public_delta}; Private +{private_delta}")
    print("P8 illustrates the selection risk: Public 0.938; Private 0.918.")
    print("Snapshot arithmetic: OK. This does not verify model causality or uncertainty.")


if __name__ == "__main__":
    main()
