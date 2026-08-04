"""Cleaning and deduplication operators."""

from __future__ import annotations

import hashlib
import re
from typing import Dict, Iterable, List

from .models import Artifact, CuratedArtifact


_IDENT_RE = re.compile(r"\b[A-Za-z_][A-Za-z_0-9]*\b")
_WS_RE = re.compile(r"\s+")


def normalize_code(code: str) -> str:
    keywords = {
        "def",
        "return",
        "if",
        "else",
        "elif",
        "for",
        "in",
        "while",
        "and",
        "or",
        "not",
        "is",
        "none",
        "true",
        "false",
    }

    def repl(match: re.Match[str]) -> str:
        token = match.group(0).lower()
        if token in keywords:
            return token
        return "ID"

    no_comments = "\n".join(line.split("#", 1)[0] for line in code.splitlines())
    normalized = _IDENT_RE.sub(repl, no_comments.lower())
    return _WS_RE.sub(" ", normalized).strip()


def code_hash(normalized_code: str) -> str:
    return hashlib.blake2b(normalized_code.encode("utf-8"), digest_size=8).hexdigest()


def infer_failure_tag(artifact: Artifact) -> str:
    errors = " ".join(test.error.lower() for test in artifact.tests if not test.passed)
    if not errors and artifact.hidden_passed:
        return "none"
    if "index" in errors or "boundary" in errors or "empty" in errors:
        return "boundary"
    if "type" in errors or "attribute" in errors:
        return "type_error"
    if "api" in errors or "nameerror" in errors or "import" in errors:
        return "api_error"
    if "timeout" in errors or "recursion" in errors:
        return "timeout"
    if artifact.public_passed and not artifact.hidden_passed:
        return "hidden_semantic"
    return "semantic"


def curate_artifacts(artifacts: Iterable[Artifact]) -> List[CuratedArtifact]:
    canonical_by_hash: Dict[str, str] = {}
    curated: List[CuratedArtifact] = []
    for artifact in artifacts:
        normalized = normalize_code(artifact.code)
        digest = code_hash(normalized)
        duplicate_of = canonical_by_hash.get(digest)
        if duplicate_of is None:
            canonical_by_hash[digest] = artifact.artifact_id
            canonical = artifact.artifact_id
        else:
            canonical = duplicate_of
        curated.append(
            CuratedArtifact(
                artifact_id=artifact.artifact_id,
                canonical_id=canonical,
                task_id=artifact.task_id,
                model=artifact.model,
                normalized_code=normalized,
                cleaned_failure_tag=infer_failure_tag(artifact),
                public_passed=artifact.public_passed,
                hidden_passed=artifact.hidden_passed,
                parent_id=artifact.parent_id,
                duplicate_of=duplicate_of,
                metadata=dict(artifact.metadata),
            )
        )
    return curated

