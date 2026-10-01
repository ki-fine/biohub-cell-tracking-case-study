"""Lightweight structural checks for the synthetic showcase graphs.

The competition's pinned RoyerLab scorer remains the authoritative metric.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from math import isfinite

from .mechanisms import Edge, Node


class GraphContractError(ValueError):
    pass


def validate_graph(
    nodes: Mapping[int, Node],
    edges: list[Edge],
    *,
    frame_count: int,
    shape_zyx: tuple[int, int, int],
) -> None:
    """Reject missing endpoints, invalid coordinates, and impossible lineage degrees."""
    if frame_count <= 0 or len(shape_zyx) != 3 or any(dim <= 0 for dim in shape_zyx):
        raise GraphContractError("invalid volume shape")
    for node_id, node in nodes.items():
        if node_id != node.id or not 0 <= node.t < frame_count:
            raise GraphContractError("node identity or time is invalid")
        if any(not isfinite(v) or not 0 <= round(v) < dim
               for v, dim in zip((node.z, node.y, node.x), shape_zyx, strict=True)):
            raise GraphContractError("coordinate would leave the exported volume")

    incoming: Counter[int] = Counter()
    outgoing: Counter[int] = Counter()
    seen: set[tuple[int, int]] = set()
    for edge in edges:
        if edge.source not in nodes or edge.target not in nodes:
            raise GraphContractError("edge references a missing node")
        key = (edge.source, edge.target)
        if key in seen:
            raise GraphContractError("duplicate edge")
        seen.add(key)
        if nodes[edge.target].t != nodes[edge.source].t + 1:
            raise GraphContractError("edge must move forward by one frame")
        if edge.probability is not None and (
            not isfinite(edge.probability) or not 0 <= edge.probability <= 1
        ):
            raise GraphContractError("invalid learned edge probability")
        incoming[edge.target] += 1
        outgoing[edge.source] += 1
        if incoming[edge.target] > 1 or outgoing[edge.source] > 2:
            raise GraphContractError("lineage has too many parents or daughters")
