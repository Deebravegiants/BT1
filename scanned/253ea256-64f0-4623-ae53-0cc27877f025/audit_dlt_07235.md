# [?] Fix race condition for transaction cache (#20875)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2025-01-14
Source: https://github.com/MystenLabs/sui/commit/11e5ec9bbed9c9baed97511b5b87aa16f5702e6e
Type: security-commit

## Details
Fix race condition for transaction cache (#20875)

Bug was (likely) as follows:

      Reader thread               | Writer thread (state sync)

                                    invalidate tickets
      get ticket
      miss cache
      read database
      insert to cache               insert to cache (racing)
      ticket is valid
      panic
                                    write to database

The writer thread must insert to db first so that the db read
cannot find an old value while holding a valid ticket

## Patch
### crates/sui-core/src/execution_cache/cache_types.rs
```diff
@@ -8,6 +8,7 @@ use std::sync::Arc;
 use std::{cmp::Ordering, hash::DefaultHasher};
 
 use moka::sync::Cache as MokaCache;
+use mysten_common::debug_fatal;
 use parking_lot::Mutex;
 use sui_types::base_types::SequenceNumber;
 
@@ -292,10 +293,12 @@ where
             let mut entry = entry.value().lock();
             check_ticket()?;
 
-            // Ticket expiry makes this assert impossible.
-            // TODO: relax to debug_assert?
-            assert!(!entry.is_newer_than(&value), "entry is newer than value");
-            *entry = value;
+            // Ticket expiry should make this assert impossible.
+            if entry.is_newer_than(&value) {
+                debug_fatal!("entry is newer than value");
+            } else {
+                *entry = value;
+            }
         }
 
         Ok(())
```

### crates/sui-core/src/execution_cache/unit_tests/writeback_cache_tests.rs
```diff
@@ -1346,3 +1346,60 @@ async fn latest_object_cache_race_test() {
     checker.join().unwrap();
     invalidator.join().unwrap();
 }
+
+#[tokio::test]
+async fn test_transaction_cache_race() {
+    telemetry_subscribers::init_for_testing();
+
+    let mut s = Scenario::new(None, Arc::new(AtomicU32::new(0))).await;
+    let cache = s.cache.clone();
+    let mut txns = Vec::new();
+
+    for i in 0..1000 {
+        let a = i * 4;
+        s.with_created(&[a]);
+        s.do_tx().await;
+
+        let outputs = s.take_outputs();
+        let tx = (*outputs.transaction).clone();
+        let effects = outputs.effects.clone();
+
+        txns.push((tx, effects));
+    }
+
+    let barrier = Arc::new(std::sync::Barrier::new(2));
+
+    let t1 = {
+        let txns = txns.clone();
+        let cache = cache.clone();
+        let barrier = barrier.clone();
+        std::thread::spawn(move || {
+            for (i, (tx, effects)) in txns.into_iter().enumerate() {
+                barrier.wait();
+                // test both single and multi insert
+                if i % 2 == 0 {
+                    cache.insert_transaction_and_effects(&tx, &effects);
+                } else {
+                    cache.multi_insert_transaction_and_effects(&[VerifiedExecutionData::new(
+                        tx, effects,
+                    )]);
+                }
+            }
+        })
+    };
+
+    let t2 = {
+        let txns = txns.clone();
+        let cache = cache.clone();
+        let barrier = barrier.clone();
+        std::thread::spawn(move || {
+            for (tx, _) in txns {
+                barrier.wait();
+                cache.get_transaction_block(tx.digest());
+            }
+        })
+    };
+
+    t1.join().unwrap();
+    t2.join().unwrap();
+}
```

### crates/sui-core/src/execution_cache/writeback_cache.rs
```diff
@@ -2268,6 +2268,9 @@ impl StateSyncAPI for WritebackCache {
         transaction: &VerifiedTransaction,
         transaction_effects: &TransactionEffects,
     ) {
+        self.store
+            .insert_transaction_and_effects(transaction, transaction_effects)
+            .expect("db error");
         self.cached
             .transactions
             .insert(
@@ -2284,15 +2287,15 @@ impl StateSyncAPI for WritebackCache {
                 Ticket::Write,
             )
             .ok();
-        self.store
-            .insert_transaction_and_effects(transaction, transaction_effects)
-            .expect("db error");
     }
 
     fn multi_insert_transaction_and_effects(
         &self,
         transactions_and_effects: &[VerifiedExecutionData],
     ) {
+        self.store
+            .multi_insert_transaction_and_effects(transactions_and_effects.iter())
+            .expect("db error");
         for VerifiedExecutionData {
             transaction,
             effects,
@@ -2315,8 +2318,5 @@ impl StateSyncAPI for WritebackCache {
                 )
                 .ok();
         }
-        self.store
-            .multi_insert_transaction_and_effects(transactions_and_effects.iter())
-            .expect("db error");
     }
 }
```
