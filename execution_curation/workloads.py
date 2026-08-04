"""Synthetic code-agent artifact generator."""

from __future__ import annotations

import random
from typing import List

from .models import Artifact, TestOutcome


TASKS = {
    "normalize_scores": "Normalize a list of numbers and handle zero totals.",
    "top_k_unique": "Return top k unique records by score with deterministic tie breaking.",
    "parse_ints": "Extract signed integers from punctuation-heavy text.",
    "clip_values": "Clip values into an inclusive lower and upper range.",
}

BUGS = {
    "none": "",
    "boundary": "IndexError: empty input boundary case failed",
    "type_error": "TypeError: unsupported operand type for None",
    "api_error": "NameError: fake_api is not defined",
    "timeout": "TimeoutError: recursion did not terminate",
    "hidden_semantic": "AssertionError: hidden semantic case failed",
}


def _code(task: str, bug: str, variant: int) -> str:
    name = f"{task}_{variant}"
    if task == "normalize_scores":
        if bug == "hidden_semantic":
            return f"def {name}(values):\n    total = sum(values)\n    return [int(v / total) for v in values]\n"
        if bug == "boundary":
            return f"def {name}(values):\n    total = sum(values)\n    return [v / total for v in values]\n"
        return f"def {name}(values):\n    total = sum(values)\n    if total == 0:\n        return [0 for _ in values]\n    return [v / total for v in values]\n"
    if task == "top_k_unique":
        if bug == "hidden_semantic":
            return f"def {name}(items, k):\n    return sorted(items, key=lambda x: -x[1])[:k]\n"
        return f"def {name}(items, k):\n    seen = {{}}\n    for key, score in items:\n        seen[key] = max(score, seen.get(key, score))\n    return sorted(seen.items(), key=lambda x: (-x[1], x[0]))[:k]\n"
    if task == "parse_ints":
        if bug == "api_error":
            return f"def {name}(text):\n    return fake_api.parse_ints(text)\n"
        return f"def {name}(text):\n    import re\n    return [int(x) for x in re.findall(r'-?\\d+', text)]\n"
    if bug == "boundary":
        return f"def {name}(values, lo, hi):\n    return [min(lo, max(hi, x)) for x in values]\n"
    return f"def {name}(values, lo, hi):\n    return [min(hi, max(lo, x)) for x in values]\n"


def _tests_for_bug(bug: str) -> List[TestOutcome]:
    if bug == "none":
        return [TestOutcome("public", True), TestOutcome("hidden", True), TestOutcome("probe", True)]
    if bug == "hidden_semantic":
        return [TestOutcome("public", True), TestOutcome("hidden", False, BUGS[bug]), TestOutcome("probe", False, BUGS[bug])]
    if bug == "boundary":
        return [TestOutcome("public", True), TestOutcome("hidden", False, BUGS[bug]), TestOutcome("probe", False, BUGS[bug])]
    if bug == "type_error":
        return [TestOutcome("public", False, BUGS[bug]), TestOutcome("hidden", False, BUGS[bug])]
    if bug == "api_error":
        return [TestOutcome("public", False, BUGS[bug]), TestOutcome("hidden", False, BUGS[bug])]
    if bug == "timeout":
        return [TestOutcome("public", False, BUGS[bug]), TestOutcome("hidden", False, BUGS[bug])]
    return [TestOutcome("public", False, BUGS["hidden_semantic"])]


def generate_artifacts(seed: int = 12, per_task: int = 24) -> List[Artifact]:
    rng = random.Random(seed)
    artifacts: List[Artifact] = []
    models = ["llama3", "qwen", "deepseek", "gpt2"]
    bug_choices = ["none", "hidden_semantic", "boundary", "type_error", "api_error", "timeout"]
    for task_id, prompt in TASKS.items():
        parent = None
        for attempt in range(per_task):
            bug = rng.choices(bug_choices, weights=[4, 3, 2, 1, 1, 1])[0]
            task_artifacts = [item for item in artifacts if item.task_id == task_id]
            if attempt % 8 == 0 and task_artifacts:
                base = rng.choice(task_artifacts)
                code = base.code.replace(base.artifact_id[-2:], f"{attempt:02d}")
                bug = base.declared_failure_tag
            else:
                code = _code(task_id, bug, attempt)
            artifact_id = f"{task_id}_{attempt:02d}"
            artifacts.append(
                Artifact(
                    artifact_id=artifact_id,
                    task_id=task_id,
                    prompt=prompt,
                    code=code,
                    model=rng.choice(models),
                    attempt=attempt,
                    parent_id=parent if attempt % 5 in {1, 2} else None,
                    tests=_tests_for_bug(bug),
                    declared_failure_tag=bug if rng.random() > 0.12 else "semantic",
                    metadata={"temperature": round(rng.uniform(0.0, 1.0), 2)},
                )
            )
            if bug != "none" and attempt % 5 == 0:
                parent = artifact_id
    return artifacts
