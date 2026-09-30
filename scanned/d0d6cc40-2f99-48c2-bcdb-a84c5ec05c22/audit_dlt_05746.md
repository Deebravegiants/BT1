# [?] ledger: fix panic with async verify and dropping ConfirmationProgress (#11234)

## Summary
Severity: Unknown
Chain: Solana
Component: jito-foundation/jito-solana
Published: 2026-03-12
Source: https://github.com/jito-foundation/jito-solana/commit/1997085ea158eb1f9bc3ac2162d0a6bd3d8869ef
Type: security-commit

## Details
ledger: fix panic with async verify and dropping ConfirmationProgress (#11234)

If ConfirmationProgress gets dropped while async verifications are still
in flight, AsyncVerificationProgress::spawn panics trying to send back
resuts to a now disconnected channel.

The fix is to remove expect() and ignore results instead.

## Patch
### ledger/src/blockstore_processor.rs
```diff
@@ -1554,9 +1554,7 @@ impl AsyncVerificationProgress {
         self.pending_jobs = self.pending_jobs.saturating_add(1);
         let sender = self.sender.clone();
         replay_tx_thread_pool.spawn(move || {
-            sender
-                .send(work())
-                .expect("AsyncVerificationProgress work sender failed");
+            let _ = sender.send(work());
         });
         Ok(())
     }
@@ -2619,6 +2617,7 @@ pub mod tests {
         },
         assert_matches::assert_matches,
         rand::{Rng, rng},
+        rayon::ThreadPoolBuilder,
         solana_account::{AccountSharedData, WritableAccount},
         solana_cost_model::transaction_cost::TransactionCost,
         solana_entry::entry::{create_ticks, next_entry, next_entry_mut},
@@ -2650,7 +2649,11 @@ pub mod tests {
             self,
             vote_state::{MAX_LOCKOUT_HISTORY, TowerSync, VoteStateV4, VoteStateVersions},
         },
-        std::{collections::BTreeSet, slice, sync::RwLock},
+        std::{
+            collections::BTreeSet,
+            slice,
+            sync::{Arc, Barrier, RwLock},
+        },
         test_case::{test_case, test_matrix},
         trees::tr,
     };
@@ -5325,6 +5328,47 @@ pub mod tests {
         );
     }
 
+    #[test]
+    fn test_async_verification_progress_drop() {
+        let exit_barrier = Arc::new(Barrier::new(2));
+        let drop_barrier = Arc::new(Barrier::new(2));
+
+        let pool = ThreadPoolBuilder::new()
+            .num_threads(1)
+            .exit_handler({
+                let exit_barrier = exit_barrier.clone();
+                move |_| {
+                    exit_barrier.wait();
+                }
+            })
+            .build()
+            .unwrap();
+
+        let mut progress = AsyncVerificationProgress::new();
+        progress
+            .spawn(&pool, &mut 0, &mut 0, {
+                let drop_barrier = drop_barrier.clone();
+                move || {
+                    // wait for the test to drop `progress` so the channel spawn() sends results to
+                    // gets disconnected
+                    drop_barrier.wait();
+                    AsyncVerificationResult {
+                        poh_verify_elapsed: 0,
+                        transaction_verify_elapsed: 0,
+                        error: None,
+                    }
+                }
+            })
+            .unwrap();
+
+        // ensure that in flight or pending tasks don't panic if AsyncVerificationProgress gets
+        // dropped
+        drop(progress);
+        drop_barrier.wait();
+        drop(pool);
+        exit_barrier.wait();
+    }
+
     fn do_test_schedule_batches_for_execution(should_succeed: bool) {
         agave_logger::setup();
         let dummy_leader_pubkey = solana_pubkey::new_rand();
```
