# Execution-Aware Data Curation for Code-Agent Artifacts

This repository is a compact data-management prototype for curating code-agent artifacts. The work is about scalable data curation, data cleaning, data wrangling, provenance, and data lake management.

## Research Question

Can execution evidence become first-class metadata for cleaning, deduplicating, linking, and searching generated-code datasets?

## Method

The project models a generated-code data lake with heterogeneous records:

- natural-language specifications;
- generated programs;
- public, hidden, and probe test outcomes;
- runtime errors and failure tags;
- repair candidates and repair lineage;
- provenance edges connecting prompts, programs, executions, and repairs.

The curation layer supports:

- exact and normalized-code deduplication;
- failure-tag normalization from runtime evidence;
- discovery of `public_pass_hidden_fail` risk cases;
- search for similar failures;
- repair-lineage queries;
- provenance graph traversal;
- benchmark metrics for duplicate reduction, cleaning accuracy, and query latency.

This is a research prototype. It intentionally uses small deterministic generated-code artifacts so the data-cleaning and provenance behavior is inspectable.

## Project Layout

```text
execution_curation/
  benchmark.py    # benchmark driver and metrics
  curation.py     # cleaning, deduplication, failure normalization
  graph.py        # provenance graph
  models.py       # dataclasses
  search.py       # similarity and failure queries
  store.py        # curated artifact store
  workloads.py    # synthetic code-agent artifact generator
scripts/
  run_benchmark.py
tests/
  test_curation.py
  test_graph.py
  test_store.py
```

## Quick Start

```bash
python3 -m unittest discover -s tests
python3 scripts/run_benchmark.py --output outputs/execution_curation_results.json
```

Example output pattern:

```text
records  curated  duplicate_reduction  tag_accuracy  risk_cases  avg_query_ms
96       72       0.250                0.917         18          0.041
```

## Why It Matches Dong Deng

The project turns code-agent outputs into a data curation and provenance problem. It is not another LLM-agent demo: the focus is on cleaning noisy generated artifacts, deduplicating near-equivalent records, normalizing metadata, linking transformations, and supporting database-style queries over technical data lakes.

## Extensions

- Add disk-backed storage and SQL query support.
- Add AST-aware deduplication and semantic hashing.
- Integrate near-duplicate alignment and filtered ANN indexes from sibling projects.
- Use real HumanEval/MBPP-style artifacts and model execution logs.

