# [?] fix(prover): Fix panics if prover's config is not ready (#1822)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-04-29
Source: https://github.com/matter-labs/zksync-era/commit/21d90d766798fb05be95028df185e9036ec7dee9
Type: security-commit

## Details
fix(prover): Fix panics if prover's config is not ready (#1822)

Prover config caused an outage before.
As part of that change, we made prover configs return an error, rather
than panic.
Whilst this helped, there are still a few edge cases where things can go
wrong.
One of them is when we add aggregation rounds.
This commit addresses the panics, turning them into an error.

## Patch
### core/lib/config/src/configs/fri_prover_group.rs
```diff
@@ -109,7 +109,14 @@ impl FriProverGroupConfig {
         ];
         for group in groups {
             for circuit_round in group {
-                rounds[circuit_round.aggregation_round as usize].push(circuit_round.clone());
+                let round = match rounds.get_mut(circuit_round.aggregation_round as usize) {
+                    Some(round) => round,
+                    None => anyhow::bail!(
+                        "Invalid aggregation round {}.",
+                        circuit_round.aggregation_round
+                    ),
+                };
+                round.push(circuit_round.clone());
             }
         }
 
```
