# [?] fix(epoch-manager): fix nondeterminism in EpochManager::compute_exempted_kickout() (#11949)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2024-08-15
Source: https://github.com/near/nearcore/commit/566e926c57f6cdc7ca3adc2bf8cc632d1aea0e4c
Type: security-commit

## Details
fix(epoch-manager): fix nondeterminism in EpochManager::compute_exempted_kickout() (#11949)

In this function, we compute and collect ratios of expected blocks and
chunks for all validators in the epoch, and we exempt the top validators
from being kicked based on the `validator_max_kickout_stake_perc` epoch
config field. We build this list from a hashmap, which has
nondeterministic iteration order, and then sort by this ratio. But if
there are many with the same ratio, then the ones we pick are not
deterministic because we don't also sort by account ID. Fix it by also
sorting by account ID

## Patch
### chain/epoch-manager/src/lib.rs
```diff
@@ -430,12 +430,13 @@ impl EpochManager {
                                 stats.block_stats.expected as i64,
                             )) / 2
                         };
-                    (account, production_ratio)
+                    (production_ratio, account)
                 })
                 .collect::<Vec<_>>();
-            sorted_validators.sort_by_key(|a| a.1);
+            sorted_validators.sort();
+
             let mut exempted_stake: Balance = 0;
-            for (account_id, _) in sorted_validators.into_iter().rev() {
+            for (_, account_id) in sorted_validators.into_iter().rev() {
                 if exempted_stake >= min_keep_stake {
                     break;
                 }
```

### chain/epoch-manager/src/tests/mod.rs
```diff
@@ -2426,6 +2426,82 @@ fn test_chunk_producers() {
     );
 }
 
+#[test]
+fn test_validator_kickout_determinism() {
+    let mut epoch_config = epoch_config_with_production_config(5, 2, 4, 4, 90, 80, 90, false)
+        .for_protocol_version(PROTOCOL_VERSION);
+    epoch_config.validator_max_kickout_stake_perc = 99;
+    let accounts = vec![
+        ("test0".parse().unwrap(), 1000),
+        ("test1".parse().unwrap(), 1000),
+        ("test2".parse().unwrap(), 1000),
+        ("test3".parse().unwrap(), 1000),
+        ("test4".parse().unwrap(), 500),
+        ("test5".parse().unwrap(), 500),
+    ];
+    let epoch_info = epoch_info(0, accounts, vec![0, 1, 2, 3], vec![vec![0, 1, 2], vec![0, 1, 3]]);
+    let block_validator_tracker = HashMap::from([
+        (0, ValidatorStats { produced: 100, expected: 100 }),
+        (1, ValidatorStats { produced: 90, expected: 100 }),
+        (2, ValidatorStats { produced: 100, expected: 100 }),
+        (3, ValidatorStats { produced: 89, expected: 100 }),
+    ]);
+    let chunk_stats0 = Vec::from([
+        (0, ChunkStats::new_with_production(100, 100)),
+        (
+            1,
+            ChunkStats {
+                production: ValidatorStats { produced: 80, expected: 100 },
+                // Note that test1 would not pass chunk endorsement
+                // threshold, but it is applied to nodes which are only
+                // chunk validators.
+                endorsement: ValidatorStats { produced: 0, expected: 100 },
+            },
+        ),
+        (2, ChunkStats::new_with_production(70, 100)),
+        (5, ChunkStats::new_with_endorsement(91, 100)),
+    ]);
+    let chunk_stats1 = Vec::from([
+        (0, ChunkStats::new_with_production(70, 100)),
+        (
+            1,
+            ChunkStats {
+                production: ValidatorStats { produced: 81, expected: 100 },
+                endorsement: ValidatorStats { produced: 1, expected: 100 },
+            },
+        ),
+        (3, ChunkStats::new_with_production(100, 100)),
+        // test4 is only a chunk validator and should be kicked out.
+        (4, ChunkStats::new_with_endorsement(89, 100)),
+    ]);
+    let chunk_stats_tracker1 = HashMap::from([
+        (0, chunk_stats0.clone().into_iter().collect()),
+        (1, chunk_stats1.clone().into_iter().collect()),
+    ]);
+    let chunk_stats0: Vec<_> = chunk_stats0.into_iter().rev().collect();
+    let chunk_stats_tracker2 = HashMap::from([
+        (0, chunk_stats0.into_iter().collect()),
+        (1, chunk_stats1.into_iter().collect()),
+    ]);
+    let (_validator_stats, kickouts1) = EpochManager::compute_validators_to_reward_and_kickout(
+        &epoch_config,
+        &epoch_info,
+        &block_validator_tracker,
+        &chunk_stats_tracker1,
+        &HashMap::new(),
+        &HashMap::new(),
+    );
+    let (_validator_stats, kickouts2) = EpochManager::compute_validators_to_reward_and_kickout(
+        &epoch_config,
+        &epoch_info,
+        &block_validator_tracker,
+        &chunk_stats_tracker2,
+        &HashMap::new(),
+        &HashMap::new(),
+    );
+    assert_eq!(kickouts1, kickouts2);
+}
+
 /// A sanity test for the compute_validators_to_reward_and_kickout function,
 /// checks that validators that don't meet their kickout thresholds are kicked out.
 #[test]
```
