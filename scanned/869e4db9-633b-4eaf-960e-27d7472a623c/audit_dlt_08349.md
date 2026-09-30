# [?] Fix nondeterministic fail-point registration in large consensus commit prologue test (#27143)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2026-07-03
Source: https://github.com/MystenLabs/sui/commit/6a2e653d11140058ed554dd5fc8313ece5e4de2b
Type: security-commit

## Details
Fix nondeterministic fail-point registration in large consensus commit prologue test (#27143)

## Patch
### crates/sui-benchmark/tests/simtest.rs
```diff
@@ -737,8 +737,6 @@ mod test {
     // simtest has low timeout tolerance and it is not designed to test performance.
     #[sim_test(config = "test_config_low_latency()")]
     async fn test_simulated_load_large_consensus_commit_prologue_size() {
-        let test_cluster = build_test_cluster(4, 10_000, 1).await;
-
         let mut additional_cancelled_txns = Vec::new();
         let num_txns = thread_rng().gen_range(500..2000);
         info!("Adding additional {num_txns} cancelled txns in consensus commit prologue.");
@@ -758,10 +756,20 @@ mod test {
             additional_cancelled_txns.push((TransactionDigest::random(), assigned_object_versions));
         }
 
+        // Register the fail point before the cluster starts processing any consensus commits.
+        // `register_fail_point_arg` mutates process-global state with no synchronization to
+        // consensus rounds; registering it after `build_test_cluster` had already let validators
+        // start committing meant different validators could observe it becoming active on
+        // different rounds (whichever round each validator happened to be processing at the
+        // moment the registration landed), causing them to build different (but individually
+        // self-consistent) ConsensusCommitPrologue transactions for the same round - a real
+        // checkpoint fork.
         register_fail_point_arg("additional_cancelled_txns_for_tests", move || {
             Some(additional_cancelled_txns.clone())
         });
 
+        let test_cluster = build_test_cluster(4, 10_000, 1).await;
+
         test_simulated_load(test_cluster.clone(), 30).await;
     }
 
```
