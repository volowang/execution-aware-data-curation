import unittest

from execution_curation.graph import ProvenanceGraph


class GraphTests(unittest.TestCase):
    def test_descendants(self):
        graph = ProvenanceGraph()
        graph.add_node("a", "artifact")
        graph.add_node("b", "test")
        graph.add_edge("a", "b", "executed")
        self.assertEqual(graph.descendants("a"), {"b"})


if __name__ == "__main__":
    unittest.main()

