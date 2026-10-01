"""Illustrative versions of three post-processing decisions used in the project.

This module is deliberately small enough to run on synthetic graphs. It is not
the competition notebook, detector, learned linker, or official scorer.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Node:
    id: int
    t: int
    z: float
    y: float
    x: float


@dataclass(frozen=True)
class Edge:
    source: int
    target: int
    probability: float | None = None


# Fixed values used by P53/P58. The P53 bug fix made the per-density arguments
# reach the matching loop; this function documents that policy, not a new search.
_GATES_UM = {
    "low": (7.25, 11.0),
    "middle": (6.5, 9.0),
    "high": (5.5, 10.0),
}


def density_gates(group: str) -> tuple[float, float]:
    """Return the tight and relaxed physical-distance gates in micrometres."""
    try:
        return _GATES_UM[group]
    except KeyError as exc:
        raise ValueError(f"unknown density group: {group!r}") from exc


def prune_weak_leaves(
    nodes: Mapping[int, Node],
    edges: list[Edge],
    *,
    density_group: str,
    threshold: float = 0.30,
) -> tuple[dict[int, Node], list[Edge]]:
    """One conservative P58-style pass; high-density movies are exempt.

    Only a non-final-frame terminal node with one incoming learned edge below
    ``threshold`` is removed. Unscored edges, including safe-division links,
    are retained. The function never cascades pruning into earlier frames.
    """
    density_gates(density_group)  # reject unknown groups before any early exit
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")
    if density_group == "high" or not nodes or not edges:
        return dict(nodes), list(edges)

    final_t = max(node.t for node in nodes.values())
    incoming: dict[int, list[Edge]] = {}
    outgoing: dict[int, int] = {}
    for edge in edges:
        incoming.setdefault(edge.target, []).append(edge)
        outgoing[edge.source] = outgoing.get(edge.source, 0) + 1

    removed: set[int] = set()
    for node_id, node in nodes.items():
        parent_edges = incoming.get(node_id, [])
        if node.t >= final_t or outgoing.get(node_id, 0) or len(parent_edges) != 1:
            continue
        probability = parent_edges[0].probability
        if probability is not None and isfinite(probability) and probability < threshold:
            removed.add(node_id)

    return (
        {node_id: node for node_id, node in nodes.items() if node_id not in removed},
        [edge for edge in edges if edge.source not in removed and edge.target not in removed],
    )


def lineage_window(
    node_id: int,
    nodes: Mapping[int, Node],
    edges: list[Edge],
    *,
    radius: int = 2,
) -> tuple[tuple[int, int], ...]:
    """Collect a local trajectory without crossing a division/merge boundary.

    P60 used this condition before linear coordinate fitting. The returned
    pairs are ``(relative_time, node_id)``; fitting is left out of this small
    example so the graph decision can be inspected directly.
    """
    if node_id not in nodes or radius < 0:
        raise ValueError("unknown node or negative radius")
    predecessors: dict[int, list[int]] = {}
    successors: dict[int, list[int]] = {}
    for edge in edges:
        if edge.source not in nodes or edge.target not in nodes:
            raise ValueError("edge references a missing node")
        if nodes[edge.target].t != nodes[edge.source].t + 1:
            raise ValueError("window expects consecutive-frame edges")
        predecessors.setdefault(edge.target, []).append(edge.source)
        successors.setdefault(edge.source, []).append(edge.target)

    def unbranched(source: int, target: int) -> bool:
        return len(successors.get(source, [])) == 1 and len(predecessors.get(target, [])) == 1

    window = [(0, node_id)]
    current = node_id
    for step in range(1, radius + 1):
        parents = predecessors.get(current, [])
        if len(parents) != 1 or not unbranched(parents[0], current):
            break
        current = parents[0]
        window.append((-step, current))
    current = node_id
    for step in range(1, radius + 1):
        children = successors.get(current, [])
        if len(children) != 1 or not unbranched(current, children[0]):
            break
        current = children[0]
        window.append((step, current))
    return tuple(sorted(window))
