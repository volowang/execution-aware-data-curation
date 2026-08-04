"""Dataclasses for execution-aware data curation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class TestOutcome:
    suite: str
    passed: bool
    error: str = ""


@dataclass
class Artifact:
    artifact_id: str
    task_id: str
    prompt: str
    code: str
    model: str
    attempt: int
    parent_id: Optional[str]
    tests: List[TestOutcome]
    declared_failure_tag: str
    metadata: Dict[str, object] = field(default_factory=dict)

    @property
    def public_passed(self) -> bool:
        public = [test for test in self.tests if test.suite == "public"]
        return bool(public) and all(test.passed for test in public)

    @property
    def hidden_passed(self) -> bool:
        hidden = [test for test in self.tests if test.suite == "hidden"]
        return bool(hidden) and all(test.passed for test in hidden)


@dataclass(frozen=True)
class CuratedArtifact:
    artifact_id: str
    canonical_id: str
    task_id: str
    model: str
    normalized_code: str
    cleaned_failure_tag: str
    public_passed: bool
    hidden_passed: bool
    parent_id: Optional[str]
    duplicate_of: Optional[str]
    metadata: Dict[str, object]


@dataclass(frozen=True)
class CurationMetrics:
    raw_records: int
    curated_records: int
    duplicate_reduction: float
    tag_accuracy: float
    risk_cases: int
    provenance_nodes: int
    provenance_edges: int
    avg_query_ms: float

