#!/usr/bin/env python3
"""Run the execution-aware curation benchmark."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from execution_curation.benchmark import format_metrics, run_benchmark, write_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=12)
    parser.add_argument("--per-task", type=int, default=24)
    parser.add_argument("--output", default="outputs/execution_curation_results.json")
    args = parser.parse_args()

    payload = run_benchmark(seed=args.seed, per_task=args.per_task)
    write_json(payload, args.output)
    print(format_metrics(payload["metrics"]))
    print(f"\nwrote {args.output}")


if __name__ == "__main__":
    main()

