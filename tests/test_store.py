import unittest

from execution_curation.store import ArtifactStore
from execution_curation.workloads import generate_artifacts


class StoreTests(unittest.TestCase):
    def test_store_builds_indexes(self):
        artifacts = generate_artifacts(seed=2, per_task=6)
        store = ArtifactStore(artifacts)
        self.assertEqual(len(store.curated), len(artifacts))
        self.assertGreater(store.graph.edge_count, 0)

    def test_risk_cases_public_pass_hidden_fail(self):
        artifacts = generate_artifacts(seed=3, per_task=8)
        store = ArtifactStore(artifacts)
        for item in store.risk_cases():
            self.assertTrue(item.public_passed)
            self.assertFalse(item.hidden_passed)


if __name__ == "__main__":
    unittest.main()

