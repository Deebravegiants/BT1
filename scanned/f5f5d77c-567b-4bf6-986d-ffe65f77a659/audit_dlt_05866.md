# [?] fix(en): Do not crash node in sync state updater task (#4247)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2026-07-15
Source: https://github.com/matter-labs/zksync-era/commit/7bc1f12998a5444f6be1988a670944da8bab5b38
Type: security-commit

## Details
fix(en): Do not crash node in sync state updater task (#4247)

## What ❔

Fixes node crashing if the main node is inaccessible when updating the
node sync state.

## Why ❔

Crashing the node in this case looks disproportionate.

## Is this a breaking change?

- [ ] Yes
- [x] No

## Operational changes

No operational changes.

## Checklist

- [x] PR title corresponds to the body of PR (we generate changelog
entries from PRs).
- [x] Tests for the changes have been added / updated.
- [x] Code has been formatted via `zkstack dev fmt` and `zkstack dev
lint`.

---------

Co-authored-by: Danil Lugovskoi <dl@matterlabs.dev>
Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### core/lib/shared_resources/src/api/sync_state.rs
```diff
@@ -51,7 +51,7 @@ impl SyncState {
     }
 }
 
-#[derive(Clone, Debug, Default)]
+#[derive(Debug, Clone, Copy, Default)]
 pub struct SyncStateData {
     main_node_block: Option<L2BlockNumber>,
     local_block: Option<L2BlockNumber>,
```

### core/node/node_sync/src/node/sync_state_updater.rs
```diff
@@ -1,5 +1,6 @@
 use std::{sync::Arc, time::Duration};
 
+use anyhow::Context as _;
 use async_trait::async_trait;
 use tokio::sync::watch;
 use zksync_dal::{
@@ -17,6 +18,7 @@ use zksync_shared_metrics::EN_METRICS;
 use zksync_shared_resources::api::{SyncState, SyncStateData};
 use zksync_web3_decl::{
     client::{DynClient, L2},
+    error::ClientRpcContext,
     namespaces::EthNamespaceClient,
 };
 
@@ -81,6 +83,7 @@ impl WiringLayer for SyncStateUpdaterLayer {
                 sync_state,
                 connection_pool,
                 main_node_client: input.main_node_client,
+                update_interval: SyncStateUpdater::DEFAULT_UPDATE_INTERVAL,
             }),
         })
     }
@@ -91,6 +94,46 @@ pub struct SyncStateUpdater {
     sync_state: SyncState,
     connection_pool: ConnectionPool<Core>,
     main_node_client: Box<DynClient<L2>>,
+    update_interval: Duration,
+}
+
+impl SyncStateUpdater {
+    const DEFAULT_UPDATE_INTERVAL: Duration = Duration::from_secs(10);
+
+    async fn step(&self) -> anyhow::Result<()> {
+        let local_block = self
+            .connection_pool
+            .connection_tagged("sync_layer")
+            .await?
+            .blocks_dal()
+            .get_sealed_l2_block_number()
+            .await?;
+        let Some(local_block) = local_block else {
+            // No local blocks yet, no need to query the main node.
+            return Ok(());
+        };
+
+        let fetch_result = self
+            .main_node_client
+            .get_block_number()
+            .rpc_context("get_block_number")
+            .await;
+        let main_node_block = match fetch_result {
+            Ok(block) => block,
+            Err(err) if err.is_retryable() => {
+                tracing::warn!(%err, "Failed fetching latest block number from main node, will retry after {:?}", self.update_interval);
+                return Ok(());
+            }
+            Err(err) => {
+                return Err(err).context("Fatal error fetching latest block number from main node");
+            }
+        };
+
+        self.sync_state.set_local_block(local_block);
+        self.sync_state
+            .set_main_node_block(main_node_block.as_u32().into());
+        Ok(())
+    }
 }
 
 #[async_trait::async_trait]
@@ -100,32 +143,9 @@ impl Task for SyncStateUpdater {
     }
 
     async fn run(self: Box<Self>, mut stop_receiver: StopReceiver) -> anyhow::Result<()> {
-        const UPDATE_INTERVAL: Duration = Duration::from_secs(10);
-
         while !*stop_receiver.0.borrow_and_update() {
-            let local_block = self
-                .connection_pool
-                .connection()
-                .await?
-                .blocks_dal()
-                .get_sealed_l2_block_number()
-                .await?;
-
-            let main_node_block = match self.main_node_client.get_block_number().await {
-                Ok(block_number) => block_number,
-                Err(e) => {
-                    tracing::warn!("Failed to fetch main node block number: {e}");
-                    continue;
-                }
-            };
-
-            if let Some(local_block) = local_block {
-                self.sync_state.set_local_block(local_block);
-                self.sync_state
-                    .set_main_node_block(main_node_block.as_u32().into());
-            }
-
-            tokio::time::timeout(UPDATE_INTERVAL, stop_receiver.0.changed())
+            self.step().await?;
+            tokio::time::timeout(self.update_interval, stop_receiver.0.changed())
                 .await
                 .ok();
         }
@@ -147,7 +167,7 @@ impl Task for SyncStateMetricsTask {
         while !*stop_receiver.0.borrow() {
             tokio::select! {
                 _ = self.0.changed() => {
-                    let data = self.0.borrow_and_update().clone();
+                    let data = *self.0.borrow_and_update();
                     let (is_synced, lag) = data.lag();
                     EN_METRICS.synced.set(is_synced.into());
                     if let Some(lag) = lag {
@@ -161,3 +181,92 @@ impl Task for SyncStateMetricsTask {
         Ok(())
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use std::sync::atomic::{AtomicUsize, Ordering};
+
+    use zksync_node_genesis::{insert_genesis_batch, GenesisParamsInitials};
+    use zksync_types::{L2BlockNumber, U64};
+    use zksync_web3_decl::{client::MockClient, jsonrpsee::core::ClientError};
+
+    use super::*;
+
+    #[tokio::test]
+    async fn sync_state_updater_basics() {
+        let pool = ConnectionPool::test_pool().await;
+        let mut storage = pool.connection().await.unwrap();
+        insert_genesis_batch(&mut storage, &GenesisParamsInitials::mock())
+            .await
+            .unwrap();
+
+        let sync_state = SyncState::default();
+        let main_node_client = MockClient::builder(L2::default())
+            .method("eth_blockNumber", move || Ok(U64::from(42)))
+            .build();
+        let (stop_sender, stop_receiver) = watch::channel(false);
+
+        let updater = Box::new(SyncStateUpdater {
+            sync_state: sync_state.clone(),
+            connection_pool: pool.clone(),
+            main_node_client: Box::new(main_node_client),
+            update_interval: Duration::from_millis(10),
+        });
+        let task_handle = tokio::spawn(updater.run(StopReceiver(stop_receiver)));
+
+        let sync_state = *sync_state
+            .subscribe()
+            .wait_for(|state| state.main_node_block().is_some() && state.local_block().is_some())
+            .await
+            .unwrap();
+
+        assert!(!task_handle.is_finished());
+        assert_eq!(sync_state.local_block(), Some(L2BlockNumber(0)));
+        assert_eq!(sync_state.main_node_block(), Some(L2BlockNumber(42)));
+
+        // Check graceful shutdown.
+        stop_sender.send_replace(true);
+        task_handle.await.unwrap().unwrap();
+    }
+
+    #[tokio::test]
+    async fn sync_state_updater_handles_transient_errors() {
+        let pool = ConnectionPool::test_pool().await;
+        let mut storage = pool.connection().await.unwrap();
+        insert_genesis_batch(&mut storage, &GenesisParamsInitials::mock())
+            .await
+            .unwrap();
+
+        let sync_state = SyncState::default();
+        let request_count = AtomicUsize::new(0);
+        let main_node_client = MockClient::builder(L2::default())
+            .method("eth_blockNumber", move || {
+                // Emulate transient connectivity issues
+                if request_count.fetch_add(1, Ordering::Relaxed) < 10 {
+                    Err(ClientError::RequestTimeout)
+                } else {
+                    Ok(U64::from(1))
+                }
+            })
+            .build();
+        let (_stop_sender, stop_receiver) = watch::channel(false);
+
+        let updater = Box::new(SyncStateUpdater {
+            sync_state: sync_state.clone(),
+            connection_pool: pool.clone(),
+            main_node_client: Box::new(main_node_client),
+            update_interval: Duration::from_millis(10),
+        });
+        let task_handle = tokio::spawn(updater.run(StopReceiver(stop_receiver)));
+
+        let sync_state = *sync_state
+            .subscribe()
+            .wait_for(|state| state.main_node_block().is_some() && state.local_block().is_some())
+            .await
+            .unwrap();
+
+        assert!(!task_handle.is_finished());
+        assert_eq!(sync_state.local_block(), Some(L2BlockNumber(0)));
+        assert_eq!(sync_state.main_node_block(), Some(L2BlockNumber(1)));
+    }
+}
```
