"""Curated artifact store."""

from __future__ import annotations

from collections import defaultdict
from typing import DefaultDict, Dict, Iterable, List

from .curation import curate_artifacts
from .graph import ProvenanceGraph, build_graph
from .models import Artifact, CuratedArtifact
from .search import lineage, public_pass_hidden_fail, similar_failures


class ArtifactStore:
    def __init__(self, artifacts: Iterable[Artifact]):
        self.raw = list(artifacts)
        self.curated = curate_artifacts(self.raw)
        self.by_id: Dict[str, CuratedArtifact] = {item.artifact_id: item for item in self.curated}
        self.by_failure: DefaultDict[str, List[str]] = defaultdict(list)
        self.by_task: DefaultDict[str, List[str]] = defaultdict(list)
        for item in self.curated:
            self.by_failure[item.cleaned_failure_tag].append(item.artifact_id)
            self.by_task[item.task_id].append(item.artifact_id)
        self.graph: ProvenanceGraph = build_graph(self.raw, self.curated)

    def risk_cases(self) -> List[CuratedArtifact]:
        return public_pass_hidden_fail(self.curated)

    def similar_failures(self, artifact_id: str, limit: int = 5):
        return similar_failures(self.curated, artifact_id, limit)

    def lineage(self, artifact_id: str) -> List[str]:
        return lineage(self.curated, artifact_id)

    def unique_canonical_count(self) -> int:
        return len({item.canonical_id for item in self.curated})

