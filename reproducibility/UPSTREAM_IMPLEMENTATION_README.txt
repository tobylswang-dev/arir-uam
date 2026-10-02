# Admission--Release Interaction Report (ARIR), reference implementation

A proposed reporting workflow, not an adopted U-space standard or an operational-capacity estimator. No new third-party citations or calibration are implied by this name.

## Reproduce

Dependencies: Python 3.12, numpy, pandas, scipy, networkx; matplotlib for figures. The original and new runs in this package used the recorded environment; see ENVIRONMENT.json.

1. `python transfer/validate.py` checks the instrumented scan against 108 historical configurations and an analytic omit-both free-flow case.
2. `python transfer/run.py` verifies frozen source hashes, creates the new input files and executes the full experiment. Existing completed runs are protected against overwrite. To rerun, use a separate copy and move the previous runs directory aside. This uses eight local worker processes, not eight independent experiments.
3. `python transfer/arir.py --runs transfer/runs --output transfer/report --events transfer/logs` regenerates the diagnostic report and tables.

## Inputs and semantics

Each JSONL run row needs demand, B, node, link, seed, policy (`bypass`/`fifo`), mode (`joint`/`vertiport_only`/`corridor_only`/`omit_both`), C/X/U/N, WC, request_sha256 and trajectory_sha256. `vertiport_only` means omit-links (10); `corridor_only` means omit-nodes (01). Hashes refer to the canonical definition in model.py; unrelated log encodings cannot be compared just by their hash. Optional dictionaries carry scan counts and FIFO-eligible exposures by final fate.

The tool checks conservation, duplicate/missing factorial blocks, input identity, applicable cross-rule/rate trajectory agreement, and the separability restriction. It reports absolute means, seed-wise D/I/G/H/T, strict seed reversal and ties, pointwise paired bootstrap intervals and a declared simultaneous approximate family for delta G/T.

To adapt another simulator, supply identical definitions and explicit eligibility/timing semantics. Hash equality is meaningful only with common request IDs, event encoding and ordering. Failure may indicate violated assumptions, unmatched inputs, encoding or implementation differences; the tool cannot determine the cause automatically.

## Process diagnostics

A visit is one live request checked in one node scan. Each visit has exactly one state, including whether FIFO has already stopped departures at that node. `fifo_eligible` means all retained gates are feasible at that visit's actual state, but the node scan is stopped. Summing such visits is not a count of uniquely lost requests or a counterfactual throughput improvement. The same request may contribute many visits. Request exposure counts by fate are kept separately from visit counts.

Only 24 preselected joint runs retain full visit logs; all 43,200 runs retain state counts, exposure/fate totals and canonical trajectory hashes. Summary inputs alone cannot establish unrecorded event-level diagnoses. No event histories are reconstructed from summary means.

## Correct diagnostic interpretation

- Invariant C_L and changed D_L: the contrast shift comes entirely from joint.
- Changed G: the omitted representations' relative outcome changed; joint alone cannot cause it.
- Invariant C_L and changed G: the change is determined by C_N.
- Expected invariant but unequal canonical trajectories: check matched inputs, assumptions, encoding and implementation.

Node departure budget is an abstract departure-admission allowance; link entry budget is an abstract entry allowance. Neither implements pad occupancy, volume occupancy, separation, flight authorisation or a real bankable slot product. No investment regret is inferred from deleting constraints.
