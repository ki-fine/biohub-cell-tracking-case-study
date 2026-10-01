"""Generate the report figure from the captured Kaggle results snapshot.

Optional dependency: matplotlib. No Kaggle credentials or raw image data needed.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence/kaggle_results_2026-10-01.json"
OUTPUT = ROOT / "assets/public_private_gap.svg"


def main() -> None:
    snapshot = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    by_name = {row["description"].split()[0]: row for row in snapshot["submissions"]}
    names = ("P0", "P8", "P40", "P58", "P60", "P94")
    fig, ax = plt.subplots(figsize=(8.5, 5.5), layout="constrained")
    fig.patch.set_facecolor("#f8fafc")
    ax.set_facecolor("#ffffff")
    colors = {"P58": "#d35b2d", "P60": "#d35b2d", "P8": "#286eb2"}
    offsets = {
        "P0": (7, 8), "P8": (7, 8), "P40": (7, -14),
        "P58": (7, 7), "P60": (7, -15), "P94": (7, 8),
    }
    for name in names:
        row = by_name[name]
        x, y = float(row["publicScore"]), float(row["privateScore"])
        color = colors.get(name, "#67788a")
        ax.scatter(x, y, s=125 if name in ("P58", "P60") else 92,
                   c=color, edgecolors="white", linewidths=1.3, zorder=3)
        ax.annotate(name, (x, y), xytext=offsets[name], textcoords="offset points",
                    fontsize=10, weight="bold" if name in ("P58", "P60") else "normal",
                    color=color)
    ax.set(xlim=(0.936, 0.952), ylim=(0.904, 0.921),
           xlabel="Public score (29% test subset)",
           ylabel="Private score (remaining 71%)",
           title="Public ranking did not predict the best private outcome")
    ax.grid(alpha=.22)
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(.5, .015, "Source: author's Kaggle submissions, final snapshot 2026-10-01; scores rounded to 3 decimals.",
             ha="center", fontsize=8, color="#526273")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, format="svg", facecolor=fig.get_facecolor())
    # Matplotlib's path formatter adds end-of-line spaces; keep Git diffs clean.
    svg = OUTPUT.read_text(encoding="utf-8")
    OUTPUT.write_text("\n".join(line.rstrip() for line in svg.splitlines()) + "\n",
                      encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
