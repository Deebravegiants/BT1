# [?] fix - shard assignment out of bounds (#13934)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2025-07-18
Source: https://github.com/near/nearcore/commit/685f92e3b9efafc966c9dafcb7815f172d4bb557
Type: security-commit

## Details
fix - shard assignment out of bounds (#13934)

Fix `index out of bounds` panic in shard assignment when number of
shards increases between epochs.

## Patch
### chain/epoch-manager/src/shard_assignment.rs
```diff
@@ -156,22 +156,29 @@ fn get_initial_chunk_producer_assignment(
         return vec![vec![]; num_shards as usize];
     }
 
+    let mut assignment = vec![vec![]; num_shards as usize];
+
     let chunk_producer_indices = chunk_producers
         .iter()
         .enumerate()
         .map(|(i, vs)| (vs.account_id().clone(), i))
         .collect::<HashMap<_, _>>();
 
-    let mut assignment = vec![];
-    for validator_stakes in prev_assignment {
+    // Copy over assignments from previous epoch, but only up to the minimum of
+    // current and previous shard counts to handle shard count changes
+    let max_shards_to_copy = prev_assignment.len().min(num_shards as usize);
+
+    for (shard_index, validator_stakes) in
+        prev_assignment.iter().take(max_shards_to_copy).enumerate()
+    {
         let mut chunk_producers = vec![];
         for validator_stake in validator_stakes {
             let chunk_producer_index = chunk_producer_indices.get(validator_stake.account_id());
             if let Some(&index) = chunk_producer_index {
                 chunk_producers.push(index);
             }
         }
-        assignment.push(chunk_producers);
+        assignment[shard_index] = chunk_producers;
     }
     assignment
 }
@@ -873,6 +880,53 @@ mod tests {
         assert_eq!(original_chunk_producer_ids, chunk_producer_ids);
     }
 
+    #[test]
+    /// Tests that shard assignment handles changing number of shards correctly.
+    fn test_shard_assignment_with_changing_shard_count() {
+        let num_chunk_producers = 4;
+        let min_validators_per_shards = 1;
+
+        // Previous epoch had 2 shards
+        let prev_assignment = assignment_for_test(vec![vec![0, 1], vec![2, 3]]);
+
+        // Current epoch has 3 shards
+        let num_shards = 3;
+
+        let assignment = assign_chunk_producers_to_shards(
+            (0..num_chunk_producers).into_iter().map(validator_stake_for_test).collect(),
+            num_shards,
+            min_validators_per_shards,
+            10,
+            RngSeed::default(),
+            prev_assignment,
+            true,
+            None,
+        )
+        .unwrap();
+
+        // Assignments should have 3 shards
+        assert_eq!(assignment.len(), 3);
+
+        // All chunk producers should be assigned to a shard
+        let assigned_producers: HashSet<_> = assignment
+            .iter()
+            .flat_map(|shard| shard.iter().map(|cp| cp.account_id().clone()))
+            .collect();
+        let expected_producers: HashSet<_> = (0..num_chunk_producers)
+            .map(|i| validator_stake_for_test(i).account_id().clone())
+            .collect();
+        assert_eq!(assigned_producers, expected_producers);
+
+        // Each shard should have at least the minimum required validators
+        for shard_assignment in &assignment {
+            assert!(
+                !shard_assignment.is_empty(),
+                "Each shard should have at least {} validator",
+                min_validators_per_shards
+            );
+        }
+    }
+
     impl super::HasStake for (usize, Balance) {
         fn get_stake(&self) -> Balance {
             self.1
```
