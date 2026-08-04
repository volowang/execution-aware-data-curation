import unittest

from execution_curation.curation import infer_failure_tag, normalize_code
from execution_curation.models import Artifact, TestOutcome


class CurationTests(unittest.TestCase):
    def test_normalize_code_replaces_identifiers(self):
        left = normalize_code("def foo(values):\n    return values\n")
        right = normalize_code("def bar(scores): return scores")
        self.assertEqual(left, right)

    def test_infer_hidden_semantic(self):
        artifact = Artifact(
            "a1",
            "task",
            "prompt",
            "def f(): pass",
            "model",
            0,
            None,
            [TestOutcome("public", True), TestOutcome("hidden", False, "AssertionError: hidden semantic case failed")],
            "semantic",
        )
        self.assertEqual(infer_failure_tag(artifact), "hidden_semantic")


if __name__ == "__main__":
    unittest.main()

