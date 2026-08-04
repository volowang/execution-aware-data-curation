"""Simple provenance graph for generated-code artifacts."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import DefaultDict, Dict, Iterable, List, Set, Tuple

from .models import Artifact, CuratedArtifact


class ProvenanceGraph:
    def __init__(self) -> None:
        self.nodes: Dict[str, Dict[str, object]] = {}
        self.edges: DefaultDict[str, List[Tuple[str, str]]] = defaultdict(list)

    def add_node(self, node_id: str, node_type: str, **attrs: object) -> None:
        self.nodes[node_id] = {"type": node_type, **attrs}

    def add_edge(self, source: str, target: str, relation: str) -> None:
        self.edges[source].append((target, relation))

    def descendants(self, node_id: str, max_depth: int = 4) -> Set[str]:
        seen: Set[str] = set()
        queue = deque([(node_id, 0)])
        while queue:
            current, depth = queue.popleft()
            if depth >= max_depth:
                continue
            for target, _ in self.edges.get(current, []):
                if target not in seen:
                    seen.add(target)
                    queue.append((target, depth + 1))
        return seen

    @property
    def edge_count(self) -> int:
        return sum(len(values) for values in self.edges.values())


def build_graph(raw: Iterable[Artifact], curated: Iterable[CuratedArtifact]) -> ProvenanceGraph:
    graph = ProvenanceGraph()
    curated_by_id = {item.artifact_id: item for item in curated}
    for artifact in raw:
        prompt_id = f"prompt:{artifact.task_id}"
        artifact_id = f"artifact:{artifact.artifact_id}"
        graph.add_node(prompt_id, "prompt", task_id=artifact.task_id)
        graph.add_node(artifact_id, "artifact", model=artifact.model, attempt=artifact.attempt)
        graph.add_edge(prompt_id, artifact_id, "generated")
        if artifact.parent_id:
            graph.add_edge(f"artifact:{artifact.parent_id}", artifact_id, "repaired_into")
        for test in artifact.tests:
            test_id = f"test:{artifact.artifact_id}:{test.suite}"
            graph.add_node(test_id, "test", suite=test.suite, passed=test.passed, error=test.error)
            graph.add_edge(artifact_id, test_id, "executed")
        curated_item = curated_by_id[artifact.artifact_id]
        tag_id = f"failure:{curated_item.cleaned_failure_tag}"
        graph.add_node(tag_id, "failure_tag", tag=curated_item.cleaned_failure_tag)
        graph.add_edge(artifact_id, tag_id, "has_failure_tag")
        if curated_item.duplicate_of:
            graph.add_edge(artifact_id, f"artifact:{curated_item.duplicate_of}", "duplicate_of")
    return graph

