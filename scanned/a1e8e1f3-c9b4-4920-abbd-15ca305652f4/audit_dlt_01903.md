# [?] fix: Fixes panic on unknown FRI prover group id (#522)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2023-11-20
Source: https://github.com/matter-labs/zksync-era/commit/1c315f3245be770ad729c19977861b79d9e438a5
Type: security-commit

## Details
fix: Fixes panic on unknown FRI prover group id (#522)

## What ❔

Fixes panic on unknown FRI prover group id.
<!-- What are the changes this PR brings about? -->
<!-- Example: This PR adds a PR template to the repo. -->
<!-- (For bigger PRs adding more context is appreciated) -->

## Why ❔

<!-- Why are these changes done? What goal do they contribute to? What
are the principles behind them? -->
<!-- Example: PR templates ensure PR reviewers, observers, and future
iterators are in context about the evolution of repos. -->

## Checklist

<!-- Check your PR fulfills the following items. -->
<!-- For draft PRs check the boxes as you complete them. -->

- [x] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [ ] Tests for the changes have been added / updated.
- [ ] Documentation comments have been added / updated.
- [x] Code has been formatted via `zk fmt` and `zk lint`.

## Patch
### core/lib/zksync_core/src/house_keeper/fri_prover_queue_monitor.rs
```diff
@@ -37,7 +37,7 @@ impl PeriodicJob for FriProverStatsReporter {
             let group_id = self
                 .config
                 .get_group_id_for_circuit_id_and_aggregation_round(circuit_id, aggregation_round)
-                .unwrap();
+                .unwrap_or(u8::MAX);
 
             metrics::gauge!(
               "fri_prover.prover.jobs",
```
