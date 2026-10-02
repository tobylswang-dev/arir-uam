# Admission--Release Interaction Report

24 actual simulation records; 3 distinct demand sets; 1 settings.

## Observed-grid mean reversals

| demand | B | mean_reversal_cells | settings | paired_seed_reversals |
| --- | --- | --- | --- | --- |
| 1.0 | 2 | 0 | 1 | 0 |

## Interpretation

Canonical trajectory agreement failures: 0 across 12 groups. These are supplied-hash agreement checks under the stated model assumptions, not independent proof or authenticity verification.
Maximum seed-wise node-rate spread in delta G: 0 pp.

G uses generated demand. Joint cancels from G. Under omit-links invariance, IL is minus the change in joint. H is the node/link presence difference-in-differences; T is its FIFO-minus-bypass change. Neither is calibrated operational synergy.

Primary family: 2 delta-G/T means, Bonferroni t intervals; pointwise paired percentile bootstrap intervals use 50 resamples. Independence is between request sets, not between matched runs. Mean-reversal counts and seed frequencies are descriptive.

Scan states count request-scan visits. A request may have many visits. Exposure by final fate is associative; it is not a causal decomposition of lost completions.

The current model fixes topology, paths, timing, demand generator and eligibility. Generalisation to other simulators, operators or physical services is untested.