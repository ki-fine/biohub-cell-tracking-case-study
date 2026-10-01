# Biohub 3D Cell Tracking: an experiment-engineering case study

**Context.** The [Biohub competition](https://www.kaggle.com/competitions/biohub-cell-tracking-during-development/) asks participants to detect cells in 3D zebrafish microscopy videos, link them through time, and reconstruct divisions. A prediction is a lineage graph, so a plausible cell location is useful only if the resulting nodes, edges, and branches remain coherent. The private leaderboard evaluates the hidden 71% of the test set; the public score covers about 29%.

**Outcome.** The selected P58 entry scored **0.949 Public / 0.915 Private**. The [2026-10-01 Kaggle snapshot](../evidence/kaggle_results_2026-10-01.json) placed the team at Public rank **1110** and private leaderboard position **1364**. The second pre-deadline choice, P60, scored 0.949 / 0.914. This was a practical research and software-engineering project rather than a podium result.

## Starting point and ownership

I adapted a [public community Notebook](https://www.kaggle.com/code/anhadmahajan06/biohub-track-your-cells-development), publicly available detector/linker checkpoints, and the [RoyerLab official metric](https://github.com/royerlab/kaggle-cell-tracking-competition). I did **not** train the principal 3D detector or temporal edge model from scratch. My work was to audit component provenance and control flow, implement fixed graph-level experiments, check that their changes survived into final predictions, and document the difference between structural evidence and held-out accuracy. AI coding assistants supported the implementation; upstream architectures and weights are credited in [PROVENANCE.md](PROVENANCE.md).

## Engineering decisions that mattered

### 1. Fix a silent density-gate wiring error

The parent post-processor computed per-movie `tight_um` and `relaxed_um` thresholds, but its matching loop still read global constants. The printed low/middle/high settings therefore overstated what the code actually did. P53 made the loop use the passed thresholds: low **7.25/11**, middle **6.5/9**, and high **5.5/10 µm**. A small synthetic conflict graph changed from one selected edge to two, verifying the control path before a GPU run.

The first graph-diff audit then failed because a 1 µm nearest-neighbour coordinate match did not preserve identity after smoothing. Instead of adjusting the intervention, I kept that failed receipt, verified identical upstream GEFF file hashes, and compared the final edges using shared original node IDs. The common-node edge sets changed by **1.238%, 0.743%, and 0.439%** on the three low/middle-density visible movies; the high-density control changed **0%**. This established mechanism activation, not generalization. P53 combined multiple changes and scored **0.949 / 0.914**, so its gain cannot be assigned to the wiring fix alone.

### 2. Test interacting detection and filtering choices

P58 restricted a third detector's replacements to sparse frames, kept the effective density-conditioned motion gates, and performed one conservative weak-leaf pruning pass only outside the high-density group. A terminal node was eligible only if it was not in the last frame, had exactly one incoming edge, no outgoing edge, and a learned incoming probability below **0.30**. Unscored safe-division additions were exempt.

Before the formal submission, the P58 run passed source and checkpoint identity checks, full 100-frame coverage on each of four visible movies, CSV and coordinate constraints, and graph checks. Its detector replacement counts were `0/0/36/0`; 20 weak leaves were actually removed, with the high-density exemption active. The official result was **0.949 Public / 0.915 Private**. The visible movies overlapped the public checkpoints' training set, so their labels were diagnostic, not an independent validation split.

### 3. Make smoothing lineage-aware

The parent linear-fit smoother could trace backward from a daughter through a division edge into the mother's trajectory. P60 stopped the fitting window at any edge that was not one-to-one at both ends. A synthetic division graph demonstrated the intended boundary. In the four visible movies, the node IDs, frames, and edge sets matched P53 exactly; only **344 final coordinates** changed. P60 scored **0.949 / 0.914**. It was chosen alongside P58 because it addressed a different possible failure mode, not because the rounded Public scores proved either would win on Private.

## Evaluation: what worked and what did not

| Entry | Public | Private | Interpretation |
| --- | ---: | ---: | --- |
| P0 control | 0.941 | 0.907 | Reproduced public-backbone starting point |
| P53 joint change | 0.949 | 0.914 | Detector, motion-gate fix, and leaf policy together |
| **P58 final choice** | **0.949** | **0.915** | Sparse detection plus density/leaf interaction |
| P60 second final choice | 0.949 | 0.914 | Lineage-aware smoothing on P53 |
| P8 earlier D4 variant | 0.938 | **0.918** | Retrospective selection counterexample |
| P94 fusion variant | 0.945 | 0.916 | Another Public/Private ranking reversal |

The observed P0→P58 difference was **+0.008** on both displayed scores. That is an end-to-end comparison of several changes, not an ablation or causal attribution. The most instructive miss was P8: its Public score was **0.011 lower** than P58's, yet its final Private score was **0.003 higher**. P94 displayed a smaller version of the same reversal. A future study would need genuinely embryo-disjoint validation with checkpoints trained without the held-out embryo; the available public weights did not establish that guarantee for this final pipeline.

The late P96–P100 submissions were accepted by the platform but had blank score fields in the final API snapshot. They are excluded from the scored comparison. Successful upload, valid output, and high-quality prediction are different claims.

## Reproducibility and transferability

For each Kaggle candidate, the project recorded parent and Notebook hashes, model identities, canonical kernel/version, mechanism preflights, output coverage, graph checks, and a single formal submission receipt. Ambiguous CLI responses were reconciled rather than retried. The compact code in this repository uses **synthetic graphs only** and lets a reviewer inspect density gates, one-pass pruning, lineage boundaries, and structural checks in minutes:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python scripts/verify_evidence.py
```

This code companion is not the full scoring pipeline. Competition data, checkpoints, and the original Kaggle environment are required for a full rerun and are not redistributed here.

### Résumé-ready summary

> Built an auditable 3D cell-tracking experiment workflow on top of public detection/linking checkpoints. Found and repaired a density-gate parameter wiring error, tested detector–linker–leaf interactions and division-safe trajectory smoothing, and verified mechanism activation through synthetic tests and exact graph diffs. Final selected entry: 0.949 Public / 0.915 Private. Documented a Public/Private ranking reversal and the limits of training-overlapping local validation.
