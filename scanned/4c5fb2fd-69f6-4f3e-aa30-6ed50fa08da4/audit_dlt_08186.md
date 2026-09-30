# [?] Fix shutdown panics (#1637)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2021-02-03
Source: https://github.com/ZcashFoundation/zebra/commit/d7c40af2a82370d24d920c4380a1bf87cc839ea5
Type: security-commit

## Details
Fix shutdown panics (#1637)

* add a shutdown flag in zebra_chain::shutdown
* fix network panic on shutdown
* fix checkpoint panic on shutdown

## Patch
### zebra-chain/src/lib.rs
```diff
@@ -28,6 +28,7 @@ pub mod parameters;
 pub mod primitives;
 pub mod sapling;
 pub mod serialization;
+pub mod shutdown;
 pub mod sprout;
 pub mod transaction;
 pub mod transparent;
```

### zebra-chain/src/shutdown.rs
```diff
@@ -0,0 +1,29 @@
+//! Shutdown related code.
+//!
+//! A global flag indicates when the application is shutting down so actions can be taken
+//! at different parts of the codebase.
+
+use std::sync::atomic::{AtomicBool, Ordering};
+
+/// A flag to indicate if Zebra is shutting down.
+///
+/// Initialized to `false` at startup.
+pub static IS_SHUTTING_DOWN: AtomicBool = AtomicBool::new(false);
+
+/// Returns true if the application is shutting down.
+///
+/// Returns false otherwise.
+pub fn is_shutting_down() -> bool {
+    // ## Correctness:
+    //
+    // Since we're shutting down, and this is a one-time operation,
+    // performance is not important. So we use the strongest memory
+    // ordering.
+    // https://doc.rust-lang.org/nomicon/atomics.html#sequentially-consistent
+    IS_SHUTTING_DOWN.load(Ordering::SeqCst)
+}
+
+/// Sets the Zebra shutdown flag to `true`.
+pub fn set_shutting_down() {
+    IS_SHUTTING_DOWN.store(true, Ordering::SeqCst);
+}
```

### zebra-consensus/src/checkpoint.rs
```diff
@@ -793,7 +793,7 @@ where
 
 #[derive(Debug, Error)]
 pub enum VerifyCheckpointError {
-    #[error("checkpoint request after checkpointing finished")]
+    #[error("checkpoint request after the final checkpoint has been verified")]
     Finished,
     #[error("block at {height:?} is higher than the maximum checkpoint {max_height:?}")]
     TooHigh {
@@ -832,6 +832,8 @@ pub enum VerifyCheckpointError {
         expected: block::Hash,
         found: block::Hash,
     },
+    #[error("zebra is shutting down")]
+    ShuttingDown,
 }
 
 /// The CheckpointVerifier service implementation.
@@ -905,9 +907,19 @@ where
         });
 
         async move {
-            commit_finalized_block
-                .await
-                .expect("commit_finalized_block should not panic")
+            let result = commit_finalized_block.await;
+            // Avoid a panic on shutdown
+            //
+            // When `zebrad` is terminated using Ctrl-C, the `commit_finalized_block` task
+            // can return a `JoinError::Cancelled`. We expect task cancellation on shutdown,
+            // so we don't need to panic here. The persistent state is correct even when the
+            // task is cancelled, because block data is committed inside transactions, in
+            // height order.
+            if zebra_chain::shutdown::is_shutting_down() {
+                Err(VerifyCheckpointError::ShuttingDown)
+            } else {
+                result.expect("commit_finalized_block should not panic")
+            }
         }
         .boxed()
     }
```

### zebra-network/src/peer/client.rs
```diff
@@ -179,12 +179,15 @@ impl<T: std::fmt::Debug> From<oneshot::Sender<T>> for MustUseOneshotSender<T> {
 impl<T: std::fmt::Debug> Drop for MustUseOneshotSender<T> {
     #[instrument(skip(self))]
     fn drop(&mut self) {
-        // is_canceled() will not panic, because we check is_none() first
-        assert!(
-            self.tx.is_none() || self.is_canceled(),
-            "unused oneshot sender: oneshot must be used or canceled: {:?}",
-            self
-        );
+        // we don't panic if we are shutting down anyway
+        if !zebra_chain::shutdown::is_shutting_down() {
+            // is_canceled() will not panic, because we check is_none() first
+            assert!(
+                self.tx.is_none() || self.is_canceled(),
+                "unused oneshot sender: oneshot must be used or canceled: {:?}",
+                self
+            );
+        }
     }
 }
 
```

### zebrad/src/components/tokio.rs
```diff
@@ -84,6 +84,7 @@ mod imp {
             .expect("Failed to register signal handler")
             .recv()
             .await;
+        zebra_chain::shutdown::set_shutting_down();
 
         info!(
             // use target to remove 'imp' from output
@@ -104,6 +105,7 @@ mod imp {
         tokio::signal::ctrl_c()
             .await
             .expect("listening for ctrl-c signal should never fail");
+        zebra_chain::shutdown::set_shutting_down();
 
         info!(
             // use target to remove 'imp' from output
```
