# [?] fix(consensus): Avoid panicking when validation result channel is closed (#10099)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2025-11-17
Source: https://github.com/ZcashFoundation/zebra/commit/d3131af402cf2dd8629aa1f93b6aeae52c7347ec
Type: security-commit

## Details
fix(consensus): Avoid panicking when validation result channel is closed (#10099)

* Avoids finishing batch worker task when batch result channel has been closed when attempting to broadcast validation results.

Avoids panicking when batch worker task has finished by returning an error early without polling the completed JoinHandle.

* Corrects `tower_batch_control::Worker::failed()` method docs.

* Removes logic from `Batch::poll_ready` for returning an error early when the worker task is finished and replaces it with a correctness comment.

## Patch
### tower-batch-control/src/service.rs
```diff
@@ -245,8 +245,21 @@ where
             .expect("previous task panicked while holding the worker handle mutex")
             .as_mut()
         {
+            // # Correctness
+            //
+            // The inner service used with `Batch` MUST NOT return recoverable errors from its:
+            // - `poll_ready` method, or
+            // - `call` method when called with a `BatchControl::Flush` request.
+            //
+            // If the inner service returns an error in those cases, this `poll_ready` method will
+            // return an error the first time its called, and will panic the second time its called
+            // as it attempts to call `poll` on a `JoinHandle` that has already completed.
             match Pin::new(worker_handle).poll(cx) {
-                Poll::Ready(Ok(())) => return Poll::Ready(Err(self.get_worker_error())),
+                Poll::Ready(Ok(())) => {
+                    let worker_error = self.get_worker_error();
+                    tracing::warn!(?worker_error, "batch worker finished unexpectedly");
+                    return Poll::Ready(Err(worker_error));
+                }
                 Poll::Ready(Err(task_cancelled)) if task_cancelled.is_cancelled() => {
                     tracing::warn!(
                         "batch task cancelled: {task_cancelled}\n\
```

### tower-batch-control/src/worker.rs
```diff
@@ -291,7 +291,7 @@ where
 
     /// Register an inner service failure.
     ///
-    /// The underlying service failed when we called `poll_ready` on it with the given `error`. We
+    /// The underlying service failed with the given `error` when we called `poll_ready` or `call` on it. We
     /// need to communicate this to all the `Batch` handles. To do so, we wrap up the error in
     /// an `Arc`, send that `Arc<E>` to all pending requests, and store it so that subsequent
     /// requests will also fail with the same error.
```

### zebra-consensus/src/primitives/sapling.rs
```diff
@@ -136,9 +136,9 @@ impl Service<BatchControl<Item>> for Verifier {
                         let (spend_vk, output_vk) = SAPLING.verifying_keys();
 
                         let res = batch.validate(&spend_vk, &output_vk, thread_rng());
-                        tx.send(Some(res))
+                        let _ = tx.send(Some(res));
                     })
-                    .await?
+                    .await
                     .map_err(Self::Error::from)
                 }
                 .boxed()
```
