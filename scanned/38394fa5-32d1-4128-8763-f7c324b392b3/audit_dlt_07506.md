# [?] upstream(node): Fix race condition for transaction cache (#8018)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2025-07-29
Source: https://github.com/iotaledger/iota/commit/9d448fefd611bf011885bfc722a6fa9ade810b70
Type: security-commit

## Details
upstream(node): Fix race condition for transaction cache (#8018)

# Description of change

- Upstream range: [v1.40.3, v1.41.2)
- Port commit: 
-
https://github.com/MystenLabs/sui/commit/11e5ec9bbed9c9baed97511b5b87aa16f5702e6e
- Description:
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


## Links to any relevant issues

Part of #6149   

## How the change has been tested

- [x] Basic tests (linting, compilation, formatting, unit/integration
tests)
- [ ] Patch-specific tests (correctness, functionality coverage)
- [ ] I have added tests that prove my fix is effective or that my
feature works
- [ ] I have checked that new and existing unit tests pass locally with
my changes

## Patch
### crates/iota-core/src/execution_cache/cache_types.rs
```diff
@@ -9,6 +9,7 @@ use std::{
     sync::{Arc, atomic::AtomicU64},
 };
 
+use iota_common::debug_fatal;
 use iota_types::base_types::SequenceNumber;
 use moka::sync::Cache as MokaCache;
 use parking_lot::Mutex;
@@ -293,10 +294,14 @@ where
             let mut entry = entry.value().lock();
             check_ticket()?;
 
-            // Ticket expiry makes this assert impossible.
-            // TODO: relax to debug_assert?
-            assert!(!entry.is_newer_than(&value), "entry is newer than value");
-            *entry = value;
+            // Ticket expiry should make this assert impossible.
+            // Note: value and entry versions can be equal, which is allowed for genesis
+            // initialization
+            if entry.is_newer_than(&value) {
+                debug_fatal!("entry is newer than value");
+            } else {
+                *entry = value;
+            }
         }
 
         Ok(())
```

### crates/iota-core/src/execution_cache/unit_tests/writeback_cache_tests.rs
```diff
@@ -1328,6 +1328,65 @@ async fn latest_object_cache_race_test() {
     invalidator.join().unwrap();
 }
 
+#[tokio::test]
+// This test verifies that concurrent transaction insertions and reads work
+// correctly without race conditions. It specifically tests the fix that ensures
+// store operations happen before cache operations. It ensures atomicity by
+// writing to the persistent store first, then updating the cache, so readers
+// never see stale or inconsistent data.
+async fn test_transaction_cache_race() {
+    telemetry_subscribers::init_for_testing();
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
+
 #[tokio::test]
 async fn concurrent_latest_object_cache_race_test() {
     // This test is a thread-less variant of latest_object_cache_race_test.
```

### crates/iota-core/src/execution_cache/writeback_cache.rs
```diff
@@ -2232,6 +2232,11 @@ impl StateSyncAPI for WritebackCache {
         transaction: &VerifiedTransaction,
         transaction_effects: &TransactionEffects,
     ) -> IotaResult {
+        self.store
+            .insert_transaction_and_effects(transaction, transaction_effects)?;
+
+        // Cache operations should not fail the entire operation after DB write succeeds
+        // Use .ok() to ignore cache failures and avoid data inconsistency
         self.cached
             .transactions
             .insert(
@@ -2248,15 +2253,16 @@ impl StateSyncAPI for WritebackCache {
                 Ticket::Write,
             )
             .ok();
-        self.store
-            .insert_transaction_and_effects(transaction, transaction_effects)
-            .map_err(IotaError::from)
+
+        Ok(())
     }
 
     fn try_multi_insert_transaction_and_effects(
         &self,
         transactions_and_effects: &[VerifiedExecutionData],
     ) -> IotaResult {
+        self.store
+            .multi_insert_transaction_and_effects(transactions_and_effects.iter())?;
         for VerifiedExecutionData {
             transaction,
             effects,
@@ -2279,8 +2285,7 @@ impl StateSyncAPI for WritebackCache {
                 )
                 .ok();
         }
-        self.store
-            .multi_insert_transaction_and_effects(transactions_and_effects.iter())
-            .map_err(IotaError::from)
+
+        Ok(())
     }
 }
```
