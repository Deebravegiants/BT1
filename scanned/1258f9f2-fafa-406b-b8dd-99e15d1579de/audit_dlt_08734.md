# [?] fix: fixed panic propagation (#2525)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-07-29
Source: https://github.com/matter-labs/zksync-era/commit/e0fc58b536debf804920887e3eb4bc050a9fe9d6
Type: security-commit

## Details
fix: fixed panic propagation (#2525)

consensus layer was incorrectly waiting for stop_receiver, while the
panic/error should be propagated immediately.

## Patch
### core/node/node_framework/src/implementations/layers/consensus/external_node.rs
```diff
@@ -1,5 +1,5 @@
 use anyhow::Context as _;
-use zksync_concurrency::{ctx, scope};
+use zksync_concurrency::{ctx, scope, sync};
 use zksync_config::configs::consensus::{ConsensusConfig, ConsensusSecrets};
 use zksync_dal::{ConnectionPool, Core};
 use zksync_node_consensus as consensus;
@@ -110,8 +110,7 @@ impl Task for ExternalNodeTask {
         // Note, however, that awaiting for the `stop_receiver` is related to the root context behavior,
         // not the consensus task itself. There may have been any number of tasks running in the root context,
         // but we only need to wait for stop signal once, and it will be propagated to all child contexts.
-        let root_ctx = ctx::root();
-        scope::run!(&root_ctx, |ctx, s| async {
+        scope::run!(&ctx::root(), |ctx, s| async {
             s.spawn_bg(consensus::era::run_external_node(
                 ctx,
                 self.config,
@@ -120,7 +119,10 @@ impl Task for ExternalNodeTask {
                 self.main_node_client,
                 self.action_queue_sender,
             ));
-            let _ = stop_receiver.0.wait_for(|stop| *stop).await?;
+            // `run_external_node` might return an error or panic,
+            // in which case we need to return immediately,
+            // rather than wait for the `stop_receiver`.
+            let _ = sync::wait_for(ctx, &mut stop_receiver.0, |stop| *stop).await;
             Ok(())
         })
         .await
```

### core/node/node_framework/src/implementations/layers/consensus/main_node.rs
```diff
@@ -1,4 +1,4 @@
-use zksync_concurrency::{ctx, scope};
+use zksync_concurrency::{ctx, scope, sync};
 use zksync_config::configs::consensus::{ConsensusConfig, ConsensusSecrets};
 use zksync_dal::{ConnectionPool, Core};
 use zksync_node_consensus as consensus;
@@ -74,15 +74,19 @@ impl Task for MainNodeConsensusTask {
         // Note, however, that awaiting for the `stop_receiver` is related to the root context behavior,
         // not the consensus task itself. There may have been any number of tasks running in the root context,
         // but we only need to wait for stop signal once, and it will be propagated to all child contexts.
-        let root_ctx = ctx::root();
-        scope::run!(&root_ctx, |ctx, s| async move {
+        scope::run!(&ctx::root(), |ctx, s| async move {
             s.spawn_bg(consensus::era::run_main_node(
                 ctx,
                 self.config,
                 self.secrets,
                 self.pool,
             ));
-            let _ = stop_receiver.0.wait_for(|stop| *stop).await?;
+            // `run_main_node` might return an error or panic,
+            // in which case we need to return immediately,
+            // rather than wait for the `stop_receiver`.
+            // We ignore the `Canceled` error and return `Ok()` instead,
+            // because cancellation is expected.
+            let _ = sync::wait_for(ctx, &mut stop_receiver.0, |stop| *stop).await;
             Ok(())
         })
         .await
```
