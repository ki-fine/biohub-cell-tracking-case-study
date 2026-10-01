import unittest

from biohub_case_study.graph_checks import GraphContractError, validate_graph
from biohub_case_study.mechanisms import (
    Edge,
    Node,
    density_gates,
    lineage_window,
    prune_weak_leaves,
)


def node(node_id: int, t: int, x: float = 0.0) -> Node:
    return Node(node_id, t, 0.0, 0.0, x)


class DensityAndLeafTests(unittest.TestCase):
    def test_locked_physical_gates(self):
        self.assertEqual(density_gates("low"), (7.25, 11.0))
        self.assertEqual(density_gates("middle"), (6.5, 9.0))
        self.assertEqual(density_gates("high"), (5.5, 10.0))
        with self.assertRaises(ValueError):
            density_gates("other")

    def test_only_scored_early_terminal_leaf_is_pruned_once(self):
        nodes = {i: node(i, t) for i, t in [(1, 0), (2, 1), (3, 1), (4, 1), (5, 2)]}
        edges = [Edge(1, 2, .20), Edge(1, 3, .90), Edge(1, 4), Edge(4, 5, .10)]
        kept, links = prune_weak_leaves(nodes, edges, density_group="middle")
        self.assertEqual(set(kept), {1, 3, 4, 5})
        self.assertEqual({(e.source, e.target) for e in links}, {(1, 3), (1, 4), (4, 5)})
        # P58 exempts high-density movies even when the same weak leaf exists.
        high, high_links = prune_weak_leaves(nodes, edges, density_group="high")
        self.assertEqual(high, nodes)
        self.assertEqual(high_links, edges)

    def test_final_frame_and_unscored_links_survive(self):
        nodes = {1: node(1, 0), 2: node(2, 1), 3: node(3, 2), 4: node(4, 1)}
        edges = [Edge(1, 2), Edge(2, 3, .01), Edge(1, 4)]
        kept, links = prune_weak_leaves(nodes, edges, density_group="low")
        self.assertEqual(kept, nodes)
        self.assertEqual(links, edges)


class LineageTests(unittest.TestCase):
    def test_window_stops_at_both_sides_of_a_division(self):
        nodes = {i: node(i, t, x) for i, t, x in [
            (1, 0, 20), (2, 1, 20), (3, 2, 20),
            (4, 3, 30), (5, 4, 30), (6, 5, 30), (7, 3, 10),
        ]}
        edges = [Edge(a, b) for a, b in [(1, 2), (2, 3), (3, 4),
                                          (4, 5), (5, 6), (3, 7)]]
        self.assertEqual(lineage_window(4, nodes, edges), ((0, 4), (1, 5), (2, 6)))
        self.assertEqual(lineage_window(3, nodes, edges), ((-2, 1), (-1, 2), (0, 3)))
        validate_graph(nodes, edges, frame_count=6, shape_zyx=(64, 256, 256))

    def test_invalid_graph_is_rejected(self):
        nodes = {1: node(1, 0), 2: node(2, 1), 3: node(3, 0)}
        for edges in ([Edge(1, 2), Edge(3, 2)], [Edge(1, 9)], [Edge(1, 3)]):
            with self.subTest(edges=edges), self.assertRaises(GraphContractError):
                validate_graph(nodes, edges, frame_count=2, shape_zyx=(64, 256, 256))
        with self.assertRaises(GraphContractError):
            validate_graph({1: node(1, 0, 300)}, [], frame_count=2,
                           shape_zyx=(64, 256, 256))


if __name__ == "__main__":
    unittest.main()
