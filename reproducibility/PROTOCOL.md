# R45 prospective internal extension protocol

Scope: fresh stochastic demand under the same synthetic network and generator, not independent topology, implementation, external validation or public preregistration. This protocol is written before generating or examining new demand outcomes.

## Fixed design and stopping rule

- Demand multipliers 0.8, 1.0, 1.5; each has 100 independently generated request sets using seeds 10000--10099, 20000--20099 and 30000--30099 respectively. No reuse of seeds 42--71. Pairing is within a demand set across all modelling factors. Demand levels are independent, not paired to each other.
- Full node x link grid {0.5,1,1.5} squared; caps 2 and 4; node and link admission gates each present/absent; bypass and node FIFO. 144 simulations per request set, 43,200 actual runs. No algebraically copied simulation records.
- Fixed paths, original 5-minute timing, [0,24h) observation, 240-minute waiting limit and original generator. No tuning to observed signs. Complete all specified runs; do not stop for significance. 100 is a fixed compute-budget choice, not a power guarantee.
- Record every input file's hash, C/X/U/N, W_C, ordered release/cancellation plus final-fate hash and mutually exclusive request-scan states. Retain full diagnostic event logs for the first seed at each demand, central and (1,1.5) cells, joint, both caps and disciplines (24 runs).

## Estimands and interpretation

C_ab,s indexes node admission a and link admission b present (1) or absent (0). H_s=C_11,s-C_10,s-C_01,s+C_00,s. Three-way interaction T=H_F-H_B. These are finite-window factorial contrasts, not physical resource synergy or an operational causal effect.

D, I and demand-normalised G retain R44 definitions. Strict per-seed reversal means G_B*G_F<0; ties reported separately. Mean sign reversal is separate from the fraction of paired seeds reversing. All diagram cells are observed grid points, not a fitted continuous phase boundary. Absolute node and link rates are retained rather than collapsed to a ratio.

Primary new inferential family: 54 settings (3 demands x2 caps x9 cells) x2 effects: delta G and T, 108 effects. Report paired-seed means with 95% Bonferroni t intervals using df=99 and alpha/108 (two-sided); Student-t approximation under independent demand realisations. Correlation within a demand is retained and does not invalidate Bonferroni. Pointwise paired bootstrap intervals for G means and effect means (4000 resamples, RNG 20260928) are supplementary and not simultaneous. No claim of strong distribution-free guarantees. Mean reversal counts and seed fractions are descriptive; no selection using pointwise interval exclusion.

## Diagnostic conditions

Omit-links: within a given input, node multiplier and B, trajectories must agree across rule and link multiplier. Omit-nodes must agree across node multiplier at fixed input/B/link/rule. Omit-both must agree across all rates/caps/rules, with zero ground waiting, zero cancellations and analytic fixed-path free-flow arrivals. Check all these, conservation and the G separability restriction.

Scan states are mutually exclusive visits: released; node_gate; link_gate; both_gates; fifo_eligible (all retained gates feasible but a previous live head stopped this scan); fifo_node_gate; fifo_link_gate; fifo_both_gates; cancelled; administrative completion or invalid edge. They do not form additive completed-request losses. Per-fate exposure counts describe association with outcomes, not causal attribution or counterfactual queue state.

The instrumented model must reproduce 108 historical event/fate comparisons before the new experiment. (The validation script actually covers 108=3 seeds x3 cells x2 caps x2 rules x3 representations.) This is implementation regression, not independent implementation validation.
