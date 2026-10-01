# Provenance and publication boundary

This repository is a **case study**, not a claim that the full scored system was
built or trained from scratch. The published Python package is a small,
dependency-free explanation of graph decisions. It is not the complete Kaggle
Notebook and does not reproduce the leaderboard score by itself.

## Upstream work

- **Competition, data format, and evaluation:** [Biohub – Cell Tracking During
  Development](https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/)
  and its [data description](https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/data).
- **Public engineering backbone:** Anhad Mahajan's
  [Biohub – Track Your Cells Development](https://www.kaggle.com/code/anhadmahajan06/biohub-track-your-cells-development).
  This project adapted and audited public 3D detection, temporal association,
  DeepCenter, motion, and graph post-processing components and publicly
  available model weights. Those upstream assets are **not** in this repository.
- **Official metric implementation:** [RoyerLab's competition
  repository](https://github.com/royerlab/kaggle-cell-tracking-competition),
  pinned in the research workspace at commit
  `075fc5f5a52d11077f9dc2b074644618f26939e2`. It is linked, not copied.

## What this repository represents

The report covers the participant's experiment design, integration,
source/provenance auditing, density-gate bug fix, detector/leaf interactions,
lineage-boundary smoothing, structural validation, and analysis of external
scores. AI coding assistants supported implementation and research; the
upstream authors retain credit for their notebooks, architectures, and weights.

`src/biohub_case_study/` reconstructs **three selected post-processing
decisions on synthetic graphs** for inspection and testing. It omits learned
model inference, the optimization solver, and competition data. It should not
be represented as the exact scored Notebook or as an independent scientific
validation.

## Result evidence

`evidence/kaggle_results_2026-10-01.json` is a small snapshot of this team's
submission entries from the authenticated Kaggle submissions API, plus the
team's public leaderboard rank and its position in the final private
leaderboard response on 2026-10-01. The private leaderboard API enumerated
the team at position 1364; this is a leaderboard position, not an independent
statistical confidence statement. The final two checked entries were P58 and
P60 in the participant's [pre-deadline screenshot](../assets/final_selection.png);
the submissions API exposes
their scores but not the checkbox selection itself. Five late P96–P100 entries
had blank Public and Private fields in the API snapshot, so they are not
counted as scored results.

The snapshot contains no competition images, model weights, submission CSVs,
credentials, API tokens, or other participants' private information. The
public and private scores are rounded to three decimal places.

[`evidence/key_artifacts.json`](../evidence/key_artifacts.json) records the
canonical kernel, version, submission reference, Notebook SHA-256, and final
CSV SHA-256 for P53/P58/P60, transcribed from the sealed research receipts.
It supports identity checks if the original artifacts are available; a hash
alone is not proof of model accuracy.

## Reproduction limit

`python -m unittest discover -s tests` reproduces the **synthetic mechanism
tests** only. `python scripts/verify_evidence.py` checks report arithmetic
against the frozen score snapshot. Full-score reproduction requires the
competition assets, upstream checkpoints, and the original Kaggle runtime;
those are deliberately outside this portfolio repository.
