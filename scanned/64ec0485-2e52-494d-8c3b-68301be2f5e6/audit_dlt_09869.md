# [?] fix(iota-core): handle cost overflowing in shared object congestion tracker (#4739)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2025-01-17
Source: https://github.com/iotaledger/iota/commit/08f718502cbb57f1352a3c8d1eb53b24768b5083
Type: security-commit

## Details
fix(iota-core): handle cost overflowing in shared object congestion tracker (#4739)

* handle cost overflowing in shared object congestion tracker

* ci-fmt

## Patch
### crates/iota-core/src/authority/shared_object_congestion_tracker.rs
```diff
@@ -93,7 +93,8 @@ impl SharedObjectCongestionTracker {
         }
         let start_cost = self.compute_tx_start_at_cost(&shared_input_objects);
 
-        if start_cost + tx_cost <= max_accumulated_txn_cost_per_object_in_commit {
+        let (end_cost, cost_overflow) = start_cost.overflowing_add(tx_cost);
+        if !cost_overflow && end_cost <= max_accumulated_txn_cost_per_object_in_commit {
             return None;
         }
 
@@ -148,12 +149,12 @@ impl SharedObjectCongestionTracker {
 
         let shared_input_objects: Vec<_> = cert.shared_input_objects().collect();
         let start_cost = self.compute_tx_start_at_cost(&shared_input_objects);
-        let end_cost = start_cost + tx_cost;
+        let end_cost = start_cost.saturating_add(tx_cost);
 
         for obj in shared_input_objects {
             if obj.mutable {
                 let old_end_cost = self.object_execution_cost.insert(obj.id, end_cost);
-                assert!(old_end_cost.is_none() || old_end_cost.unwrap() < end_cost);
+                assert!(old_end_cost.is_none() || old_end_cost.unwrap() <= end_cost);
             }
         }
     }
@@ -556,4 +557,158 @@ mod object_cost_tests {
             expected_object_cost
         );
     }
+
+    #[test]
+    fn test_cost_overflow() {
+        let object_id_0 = ObjectID::random();
+        let object_id_1 = ObjectID::random();
+        let object_id_2 = ObjectID::random();
+        // edge case: max value is saturated
+        let max_accumulated_txn_cost_per_object_in_commit = u64::MAX;
+
+        // case 1: large initial cost, small tx cost
+        let mut shared_object_congestion_tracker =
+            SharedObjectCongestionTracker::new_with_initial_value_for_test(
+                &[(object_id_0, u64::MAX - 1), (object_id_1, u64::MAX - 1)],
+                PerObjectCongestionControlMode::TotalGasBudget,
+            );
+
+        let tx = build_transaction(&[(object_id_0, true)], 1);
+        assert!(
+            shared_object_congestion_tracker
+                .should_defer_due_to_object_congestion(
+                    &tx,
+                    max_accumulated_txn_cost_per_object_in_commit,
+                    &HashMap::new(),
+                    0,
+                )
+                .is_none(),
+            "objects are not yet congested"
+        );
+        shared_object_congestion_tracker.bump_object_execution_cost(&tx);
+        assert_eq!(
+            shared_object_congestion_tracker,
+            SharedObjectCongestionTracker::new_with_initial_value_for_test(
+                &[(object_id_0, u64::MAX), (object_id_1, u64::MAX - 1),],
+                PerObjectCongestionControlMode::TotalGasBudget
+            )
+        );
+
+        let tx = build_transaction(&[(object_id_0, true), (object_id_1, true)], 1);
+        if let Some((_, congested_objects)) = shared_object_congestion_tracker
+            .should_defer_due_to_object_congestion(
+                &tx,
+                max_accumulated_txn_cost_per_object_in_commit,
+                &HashMap::new(),
+                0,
+            )
+        {
+            assert_eq!(congested_objects.len(), 1);
+            assert_eq!(congested_objects[0], object_id_0);
+        } else {
+            panic!("object 0 is congesting, should defer");
+        }
+        shared_object_congestion_tracker.bump_object_execution_cost(&tx);
+        assert_eq!(
+            shared_object_congestion_tracker,
+            SharedObjectCongestionTracker::new_with_initial_value_for_test(
+                &[(object_id_0, u64::MAX), (object_id_1, u64::MAX),],
+                PerObjectCongestionControlMode::TotalGasBudget
+            )
+        );
+
+        if let Some((_, congested_objects)) = shared_object_congestion_tracker
+            .should_defer_due_to_object_congestion(
+                &tx,
+                max_accumulated_txn_cost_per_object_in_commit,
+                &HashMap::new(),
+                0,
+            )
+        {
+            assert_eq!(congested_objects.len(), 2);
+            assert_eq!(congested_objects[0], object_id_0);
+            assert_eq!(congested_objects[1], object_id_1);
+        } else {
+            panic!("objects 0 and 1 are congesting, should defer");
+        }
+        shared_object_congestion_tracker.bump_object_execution_cost(&tx);
+        assert_eq!(
+            shared_object_congestion_tracker,
+            SharedObjectCongestionTracker::new_with_initial_value_for_test(
+                &[(object_id_0, u64::MAX), (object_id_1, u64::MAX),],
+                PerObjectCongestionControlMode::TotalGasBudget
+            )
+        );
+
+        // case 2: small initial cost, large tx cost
+        let mut shared_object_congestion_tracker =
+            SharedObjectCongestionTracker::new_with_initial_value_for_test(
+                &[(object_id_0, 0), (object_id_1, 1), (object_id_2, 2)],
+                PerObjectCongestionControlMode::TotalGasBudget,
+            );
+
+        let tx = build_transaction(
+            &[
+                (object_id_0, true),
+                (object_id_1, true),
+                (object_id_2, true),
+            ],
+            u64::MAX - 1,
+        );
+        if let Some((_, congested_objects)) = shared_object_congestion_tracker
+            .should_defer_due_to_object_congestion(
+                &tx,
+                max_accumulated_txn_cost_per_object_in_commit,
+                &HashMap::new(),
+                0,
+            )
+        {
+            assert_eq!(congested_objects.len(), 1);
+            assert_eq!(congested_objects[0], object_id_2);
+        } else {
+            panic!("case 2: object 2 is congested, should defer");
+        }
+        shared_object_congestion_tracker.bump_object_execution_cost(&tx);
+        assert_eq!(
+            shared_object_congestion_tracker,
+            SharedObjectCongestionTracker::new_with_initial_value_for_test(
+                &[
+                    (object_id_0, u64::MAX),
+                    (object_id_1, u64::MAX),
+                    (object_id_2, u64::MAX),
+                ],
+                PerObjectCongestionControlMode::TotalGasBudget
+            )
+        );
+
+        // case 3: max initial cost, max tx cost
+        let mut shared_object_congestion_tracker =
+            SharedObjectCongestionTracker::new_with_initial_value_for_test(
+                &[(object_id_0, u64::MAX)],
+                PerObjectCongestionControlMode::TotalGasBudget,
+            );
+
+        let tx = build_transaction(&[(object_id_0, true)], u64::MAX);
+        if let Some((_, congested_objects)) = shared_object_congestion_tracker
+            .should_defer_due_to_object_congestion(
+                &tx,
+                max_accumulated_txn_cost_per_object_in_commit,
+                &HashMap::new(),
+                0,
+            )
+        {
+            assert_eq!(congested_objects.len(), 1);
+            assert_eq!(congested_objects[0], object_id_0);
+        } else {
+            panic!("case 3: object 0 is congested, should defer");
+        }
+        shared_object_congestion_tracker.bump_object_execution_cost(&tx);
+        assert_eq!(
+            shared_object_congestion_tracker,
+            SharedObjectCongestionTracker::new_with_initial_value_for_test(
+                &[(object_id_0, u64::MAX),],
+                PerObjectCongestionControlMode::TotalGasBudget
+            )
+        );
+    }
 }
```
