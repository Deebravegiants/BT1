# [?] Hotfix/fix mempool race condition (#852)

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2024-02-27
Source: https://github.com/radixdlt/babylon-node/commit/72eade6867075d6b1c7b665d88c7810c2dec9429
Type: security-commit

## Details
Hotfix/fix mempool race condition (#852)

Same as https://github.com/radixdlt/babylon-node/pull/846 but to
`release/anemone`

## Patch
### core-rust/state-manager/src/mempool/mempool_manager.rs
```diff
@@ -315,7 +315,7 @@ impl MempoolManager {
                     validated,
                     raw: raw_transaction,
                 });
-                match self.mempool.write().add_transaction(
+                match self.mempool.write().add_transaction_if_not_present(
                     mempool_transaction.clone(),
                     source,
                     Instant::now(),
```

### core-rust/state-manager/src/mempool/priority_mempool.rs
```diff
@@ -250,17 +250,22 @@ impl PriorityMempool {
 }
 
 impl PriorityMempool {
-    /// ASSUMPTION: Mempool does not already contain the transaction (panics otherwise).
     /// Tries to add a new transaction into the mempool.
     /// Will return either a [`Vec`] of [`MempoolData`] that was evicted in order to fit the new transaction or an error
     /// if the mempool is full and the new transaction proposal priority is not better than what already exists.
-    pub fn add_transaction(
+    /// Returns an empty [`Vec`] if the transaction was already present in the mempool.
+    pub fn add_transaction_if_not_present(
         &mut self,
         transaction: Arc<MempoolTransaction>,
         source: MempoolAddSource,
         added_at: Instant,
     ) -> Result<Vec<Arc<MempoolData>>, MempoolAddError> {
         let payload_hash = transaction.notarized_transaction_hash();
+
+        if self.contains_transaction(&payload_hash) {
+            return Ok(vec![]);
+        }
+
         let intent_hash = transaction.intent_hash();
         let transaction_size = transaction.raw.0.len() as u64;
 
@@ -335,7 +340,8 @@ impl PriorityMempool {
             .insert(payload_hash, transaction_data.clone())
             .is_some()
         {
-            panic!("Broken precondition: Transaction already inside mempool");
+            // This should have been checked at the beginning of this method
+            panic!("Broken precondition: Transaction already inside mempool.");
         }
 
         // Add proposal priority index
@@ -636,14 +642,18 @@ mod tests {
         assert_eq!(mp.remaining_transaction_count, 5);
         assert_eq!(mp.get_count(), 0);
 
-        mp.add_transaction(mt1.clone(), MempoolAddSource::CoreApi, Instant::now())
+        mp.add_transaction_if_not_present(mt1.clone(), MempoolAddSource::CoreApi, Instant::now())
             .unwrap();
         assert_eq!(mp.remaining_transaction_count, 4);
         assert_eq!(mp.get_count(), 1);
         assert!(mp.contains_transaction(&mt1.notarized_transaction_hash()));
 
-        mp.add_transaction(mt2.clone(), MempoolAddSource::MempoolSync, Instant::now())
-            .unwrap();
+        mp.add_transaction_if_not_present(
+            mt2.clone(),
+            MempoolAddSource::MempoolSync,
+            Instant::now(),
+        )
+        .unwrap();
         assert_eq!(mp.remaining_transaction_count, 3);
         assert_eq!(mp.get_count(), 2);
         assert!(mp.contains_transaction(&mt1.notarized_transaction_hash()));
@@ -687,31 +697,31 @@ mod tests {
             &registry,
         );
         assert!(mp
-            .add_transaction(
+            .add_transaction_if_not_present(
                 intent_1_payload_1.clone(),
                 MempoolAddSource::CoreApi,
                 Instant::now()
             )
             .unwrap()
             .is_empty());
         assert!(mp
-            .add_transaction(
+            .add_transaction_if_not_present(
                 intent_1_payload_2.clone(),
                 MempoolAddSource::CoreApi,
                 Instant::now()
             )
             .unwrap()
             .is_empty());
         assert!(mp
-            .add_transaction(
+            .add_transaction_if_not_present(
                 intent_1_payload_3,
                 MempoolAddSource::MempoolSync,
                 Instant::now()
             )
             .unwrap()
             .is_empty());
         assert!(mp
-            .add_transaction(
+            .add_transaction_if_not_present(
                 intent_2_payload_1.clone(),
                 MempoolAddSource::CoreApi,
                 Instant::now()
@@ -753,7 +763,7 @@ mod tests {
             0
         );
         assert!(mp
-            .add_transaction(
+            .add_transaction_if_not_present(
                 intent_2_payload_1,
                 MempoolAddSource::MempoolSync,
                 Instant::now()
@@ -769,7 +779,7 @@ mod tests {
         );
 
         assert!(mp
-            .add_transaction(
+            .add_transaction_if_not_present(
                 intent_2_payload_2.clone(),
                 MempoolAddSource::CoreApi,
                 Instant::now()
@@ -857,49 +867,84 @@ mod tests {
         );
 
         assert!(mp
-            .add_transaction(mt4.clone(), MempoolAddSource::CoreApi, time_point[0])
+            .add_transaction_if_not_present(mt4.clone(), MempoolAddSource::CoreApi, time_point[0])
             .unwrap()
             .is_empty());
         assert!(mp
-            .add_transaction(mt2.clone(), MempoolAddSource::CoreApi, time_point[1])
+            .add_transaction_if_not_present(mt2.clone(), MempoolAddSource::CoreApi, time_point[1])
             .unwrap()
             .is_empty());
         assert!(mp
-            .add_transaction(mt3.clone(), MempoolAddSource::MempoolSync, time_point[0])
+            .add_transaction_if_not_present(
+                mt3.clone(),
+                MempoolAddSource::MempoolSync,
+                time_point[0]
+            )
             .unwrap()
             .is_empty());
         assert!(mp
-            .add_transaction(mt1.clone(), MempoolAddSource::CoreApi, time_point[0])
+            .add_transaction_if_not_present(mt1.clone(), MempoolAddSource::CoreApi, time_point[0])
             .unwrap()
             .is_empty());
 
         let evicted = mp
-            .add_transaction(mt5, MempoolAddSource::CoreApi, time_point[1])
+            .add_transaction_if_not_present(mt5, MempoolAddSource::CoreApi, time_point[1])
             .unwrap();
         assert_eq!(evicted.len(), 1);
         assert_eq!(evicted[0].transaction, mt1);
 
         // mt2 should be evicted before mt3 because of lower time spent in the mempool
         let evicted = mp
-            .add_transaction(mt6, MempoolAddSource::CoreApi, time_point[1])
+            .add_transaction_if_not_present(mt6, MempoolAddSource::CoreApi, time_point[1])
             .unwrap();
         assert_eq!(evicted.len(), 1);
         assert_eq!(evicted[0].transaction, mt2);
 
         let evicted = mp
-            .add_transaction(mt7, MempoolAddSource::CoreApi, time_point[1])
+            .add_transaction_if_not_present(mt7, MempoolAddSource::CoreApi, time_point[1])
             .unwrap();
         assert_eq!(evicted.len(), 1);
         assert_eq!(evicted[0].transaction, mt3);
 
         let evicted = mp
-            .add_transaction(mt8, MempoolAddSource::CoreApi, time_point[1])
+            .add_transaction_if_not_present(mt8, MempoolAddSource::CoreApi, time_point[1])
             .unwrap();
         assert_eq!(evicted.len(), 1);
         assert_eq!(evicted[0].transaction, mt4);
 
         assert!(mp
-            .add_transaction(mt9, MempoolAddSource::CoreApi, time_point[2])
+            .add_transaction_if_not_present(mt9, MempoolAddSource::CoreApi, time_point[2])
             .is_err());
     }
+
+    #[test]
+    fn test_duplicate_txn_not_inserted() {
+        let mempool_txn = create_fake_pending_transaction(1, 0, 10);
+
+        let now = Instant::now();
+
+        let registry = Registry::new();
+
+        let mut mempool = PriorityMempool::new(
+            MempoolConfig {
+                max_transaction_count: 1,
+                max_total_transactions_size: 1024 * 1024,
+            },
+            &registry,
+        );
+
+        // Inserting the same transaction twice should be a non-panicking no-op
+        assert!(mempool
+            .add_transaction_if_not_present(mempool_txn.clone(), MempoolAddSource::CoreApi, now)
+            .unwrap()
+            .is_empty());
+        assert!(mempool
+            .add_transaction_if_not_present(
+                mempool_txn.clone(),
+                MempoolAddSource::MempoolSync,
+                now + Duration::from_secs(1)
+            )
+            .unwrap()
+            .is_empty());
+    }
 }
```
