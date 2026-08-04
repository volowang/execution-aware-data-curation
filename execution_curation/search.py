"""Search and query operators for curated artifacts."""

from __future__ import annotations

from typing import Iterable, List, Tuple

from .models import CuratedArtifact


def token_jaccard(left: str, right: str) -> float:
    left_set = set(left.split())
    right_set = set(right.split())
    if not left_set and not right_set:
        return 1.0
    return len(left_set & right_set) / max(1, len(left_set | right_set))


def similar_failures(artifacts: Iterable[CuratedArtifact], artifact_id: str, limit: int = 5) -> List[Tuple[str, float]]:
    items = list(artifacts)
    anchor = next(item for item in items if item.artifact_id == artifact_id)
    scored = []
    for item in items:
        if item.artifact_id == artifact_id:
            continue
        if item.cleaned_failure_tag != anchor.cleaned_failure_tag:
            continue
        score = token_jaccard(anchor.normalized_code, item.normalized_code)
        scored.append((item.artifact_id, score))
    scored.sort(key=lambda pair: (-pair[1], pair[0]))
    return scored[:limit]


def public_pass_hidden_fail(artifacts: Iterable[CuratedArtifact]) -> List[CuratedArtifact]:
    return [item for item in artifacts if item.public_passed and not item.hidden_passed]


def lineage(artifacts: Iterable[CuratedArtifact], artifact_id: str) -> List[str]:
    by_id = {item.artifact_id: item for item in artifacts}
    chain = []
    current = by_id.get(artifact_id)
    while current:
        chain.append(current.artifact_id)
        current = by_id.get(current.parent_id) if current.parent_id else None
    return list(reversed(chain))

