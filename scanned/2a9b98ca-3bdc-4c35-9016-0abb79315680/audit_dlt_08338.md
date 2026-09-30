# [?] fix deadlock between the mempool and the db (#15421)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2024-11-27
Source: https://github.com/aptos-labs/aptos-core/commit/de9040dab6d41af91520fa90e43200949d9490f7
Type: security-commit

## Details
fix deadlock between the mempool and the db (#15421)

## Patch
### mempool/src/shared_mempool/tasks.rs
```diff
@@ -16,7 +16,7 @@ use crate::{
         },
         use_case_history::UseCaseHistory,
     },
-    thread_pool::IO_POOL,
+    thread_pool::{IO_POOL, VALIDATION_POOL},
     QuorumStoreRequest, QuorumStoreResponse, SubmissionStatus,
 };
 use anyhow::Result;
@@ -45,7 +45,6 @@ use std::{
     time::{Duration, Instant},
 };
 use tokio::runtime::Handle;
-
 // ============================== //
 //  broadcast_coordinator tasks  //
 // ============================== //
@@ -393,18 +392,20 @@ fn validate_and_add_transactions<NetworkClient, TransactionValidator>(
     let vm_validation_timer = counters::PROCESS_TXN_BREAKDOWN_LATENCY
         .with_label_values(&[counters::VM_VALIDATION_LABEL])
         .start_timer();
-    let validation_results = transactions
-        .par_iter()
-        .map(|t| {
-            let result = smp.validator.read().validate_transaction(t.0.clone());
-            // Pre-compute the hash and length if the transaction is valid, before locking mempool
-            if result.is_ok() {
-                t.0.committed_hash();
-                t.0.txn_bytes_len();
-            }
-            result
-        })
-        .collect::<Vec<_>>();
+    let validation_results = VALIDATION_POOL.install(|| {
+        transactions
+            .par_iter()
+            .map(|t| {
+                let result = smp.validator.read().validate_transaction(t.0.clone());
+                // Pre-compute the hash and length if the transaction is valid, before locking mempool
+                if result.is_ok() {
+                    t.0.committed_hash();
+                    t.0.txn_bytes_len();
+                }
+                result
+            })
+            .collect::<Vec<_>>()
+    });
     vm_validation_timer.stop_and_record();
     {
         let mut mempool = smp.mempool.lock();
```

### mempool/src/thread_pool.rs
```diff
@@ -11,3 +11,10 @@ pub(crate) static IO_POOL: Lazy<rayon::ThreadPool> = Lazy::new(|| {
         .build()
         .unwrap()
 });
+
+pub(crate) static VALIDATION_POOL: Lazy<rayon::ThreadPool> = Lazy::new(|| {
+    rayon::ThreadPoolBuilder::new()
+        .thread_name(|index| format!("mempool_vali_{}", index))
+        .build()
+        .unwrap()
+});
```

### storage/storage-interface/src/state_store/sharded_state_updates.rs
```diff
@@ -31,12 +31,14 @@ impl ShardedStateUpdates {
     }
 
     pub fn merge(&mut self, other: Self) {
-        self.shards
-            .par_iter_mut()
-            .zip_eq(other.shards.into_par_iter())
-            .for_each(|(l, r)| {
-                l.extend(r);
-            })
+        THREAD_MANAGER.get_exe_cpu_pool().install(|| {
+            self.shards
+                .par_iter_mut()
+                .zip_eq(other.shards.into_par_iter())
+                .for_each(|(l, r)| {
+                    l.extend(r);
+                })
+        })
     }
 
     pub fn clone_merge(&mut self, other: &Self) {
```
