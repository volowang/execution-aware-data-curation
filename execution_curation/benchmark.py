"""Benchmark execution-aware data curation."""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Dict

from .curation import infer_failure_tag
from .models import CurationMetrics
from .store import ArtifactStore
from .workloads import generate_artifacts


def run_benchmark(seed: int = 12, per_task: int = 24) -> Dict[str, object]:
    artifacts = generate_artifacts(seed=seed, per_task=per_task)
    store = ArtifactStore(artifacts)
    correct_tags = sum(1 for artifact in artifacts if infer_failure_tag(artifact) == store.by_id[artifact.artifact_id].cleaned_failure_tag)
    risk_cases = store.risk_cases()

    query_start = time.perf_counter()
    query_count = 0
    sample_queries = []
    for case in risk_cases[:10]:
        sample_queries.append(
            {
                "artifact_id": case.artifact_id,
                "lineage": store.lineage(case.artifact_id),
                "similar_failures": store.similar_failures(case.artifact_id, limit=3),
                "descendants": sorted(store.graph.descendants(f"artifact:{case.artifact_id}", max_depth=3))[:6],
            }
        )
        query_count += 3
    avg_query_ms = ((time.perf_counter() - query_start) * 1000.0) / max(1, query_count)

    metrics = CurationMetrics(
        raw_records=len(artifacts),
        curated_records=store.unique_canonical_count(),
        duplicate_reduction=1.0 - store.unique_canonical_count() / max(1, len(artifacts)),
        tag_accuracy=correct_tags / max(1, len(artifacts)),
        risk_cases=len(risk_cases),
        provenance_nodes=len(store.graph.nodes),
        provenance_edges=store.graph.edge_count,
        avg_query_ms=avg_query_ms,
    )
    return {
        "config": {"seed": seed, "per_task": per_task},
        "metrics": asdict(metrics),
        "failure_groups": {key: value[:8] for key, value in store.by_failure.items()},
        "sample_queries": sample_queries,
    }


def write_json(payload: Dict[str, object], output: str | Path) -> None:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def format_metrics(metrics: Dict[str, object]) -> str:
    return (
        "records  curated  duplicate_reduction  tag_accuracy  risk_cases  provenance_edges  avg_query_ms\n"
        f"{metrics['raw_records']:>7}  "
        f"{metrics['curated_records']:>7}  "
        f"{metrics['duplicate_reduction']:.3f}                "
        f"{metrics['tag_accuracy']:.3f}         "
        f"{metrics['risk_cases']:>5}       "
        f"{metrics['provenance_edges']:>7}          "
        f"{metrics['avg_query_ms']:.4f}"
    )

