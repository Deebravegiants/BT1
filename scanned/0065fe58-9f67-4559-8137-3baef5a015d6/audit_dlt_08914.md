# [?] Merge pull request #1405 from eqlabs/fix-pending-crash

## Summary
Severity: Unknown
Chain: Starknet
Component: software-mansion/pathfinder
Published: 2023-10-05
Source: https://github.com/software-mansion/pathfinder/commit/58a26d452107d2a6e6f5e9d6da0c2d244e48f39c
Type: security-commit

## Details
Merge pull request #1405 from eqlabs/fix-pending-crash

fix: sync crash due to duplicate blocks submitted by producer

## Patch
### CHANGELOG.md
```diff
@@ -11,6 +11,8 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 
 ### Fixed
 
+- Rare edge case where duplicate blocks caused the sync process to halt due to a `A PRIMARY KEY constraint failed` error.
+- Querying a descync'd feeder gateway causes sync process to end due to missing classes.
 - pathfinder now exits with a non-zero exit status if any of the service tasks (sync/RPC/monitoring) terminates.
 
 ### Changed
```

### crates/pathfinder/src/state/sync.rs
```diff
@@ -339,14 +339,14 @@ async fn consumer(mut events: Receiver<SyncEvent>, context: ConsumerContext) ->
         .connection()
         .context("Creating database connection")?;
 
-    let mut latest_timestamp = tokio::task::block_in_place(|| {
+    let (mut latest_timestamp, mut next_number) = tokio::task::block_in_place(|| {
         let tx = db_conn
             .transaction()
             .context("Creating database transaction")?;
         let latest = tx
             .block_header(pathfinder_storage::BlockId::Latest)
             .context("Fetching latest block header")?
-            .map(|b| b.timestamp)
+            .map(|b| (b.timestamp, b.number + 1))
             .unwrap_or_default();
 
         anyhow::Ok(latest)
@@ -361,6 +361,11 @@ async fn consumer(mut events: Receiver<SyncEvent>, context: ConsumerContext) ->
                 tracing::info!("L1 sync updated to block {}", update.block_number);
             }
             Block((block, (tx_comm, ev_comm)), state_update, timings) => {
+                if block.block_number < next_number {
+                    tracing::debug!("Ignoring duplicate block {}", block.block_number);
+                    continue;
+                }
+
                 let block_number = block.block_number;
                 let block_hash = block.block_hash;
                 let block_timestamp = block.timestamp;
@@ -422,6 +427,7 @@ async fn consumer(mut events: Receiver<SyncEvent>, context: ConsumerContext) ->
                     (block_timestamp.get() - latest_timestamp.get()) as f64
                 );
                 latest_timestamp = block_timestamp;
+                next_number += 1;
 
                 // Give a simple log under INFO level, and a more verbose log
                 // with timing information under DEBUG+ level.
@@ -1169,4 +1175,33 @@ mod tests {
 
         assert_eq!(definition, expected_definition);
     }
+
+    #[tokio::test(flavor = "multi_thread")]
+    async fn consumer_should_ignore_duplicate_blocks() {
+        let storage = Storage::in_memory().unwrap();
+
+        let (event_tx, event_rx) = tokio::sync::mpsc::channel(5);
+
+        let blocks = generate_block_data();
+        let (a, b, c) = blocks[0].clone();
+
+        event_tx
+            .send(SyncEvent::Block(a.clone(), b.clone(), c))
+            .await
+            .unwrap();
+        event_tx
+            .send(SyncEvent::Block(a.clone(), b.clone(), c))
+            .await
+            .unwrap();
+        drop(event_tx);
+
+        let context = ConsumerContext {
+            storage,
+            state: Arc::new(SyncState::default()),
+            pending_data: PendingData::default(),
+            verify_tree_hashes: false,
+        };
+
+        consumer(event_rx, context).await.unwrap();
+    }
 }
```

### crates/pathfinder/src/state/sync/pending.rs
```diff
@@ -3,8 +3,8 @@ use pathfinder_common::BlockId;
 use pathfinder_common::StateUpdate;
 use pathfinder_storage::Storage;
 use starknet_gateway_client::GatewayApi;
+use starknet_gateway_types::reply::Block;
 use starknet_gateway_types::reply::MaybePendingBlock;
-use starknet_gateway_types::reply::{Block, PendingBlock};
 use std::sync::Arc;
 use tokio::time::Instant;
 
@@ -29,7 +29,11 @@ pub async fn poll_pending<S: GatewayApi + Clone + Send + 'static>(
     poll_interval: std::time::Duration,
     storage: Storage,
 ) -> anyhow::Result<(Option<Block>, Option<StateUpdate>)> {
-    let mut prev_block: Option<Arc<PendingBlock>> = None;
+    // The transaction count of the last emitted pending block. This is used
+    // as a proxy for freshness of the pending data. Feeder gateways are not 100%
+    // in sync wrt pending data, and as a result it is possible for us to receive
+    // pending data which is older than the one we received previously.
+    let mut prev_tx_count = 0;
 
     loop {
         let t_fetch = Instant::now();
@@ -67,62 +71,42 @@ pub async fn poll_pending<S: GatewayApi + Clone + Send + 'static>(
                 );
                 return Ok((None, None));
             }
-            MaybePendingBlock::Pending(pending) => {
-                let replace = prev_block
-                    .as_ref()
-                    .map(|prev| pending.transactions.len() > prev.transactions.len())
-                    .unwrap_or(true);
-
-                if replace {
-                    let block = Arc::new(pending);
-                    prev_block = Some(block.clone());
-                    tracing::trace!("Pending block data changed");
-
-                    download_classes_and_emit_event(
-                        &tx_event,
-                        sequencer,
-                        &storage,
-                        block,
-                        Arc::new(state_update),
-                    )
-                    .await?;
+            MaybePendingBlock::Pending(pending) if pending.transactions.len() > prev_tx_count => {
+                // Download, process and emit all missing classes. This can occasionally
+                // fail when querying a desync'd feeder gateway which isn't aware of the
+                // new pending classes. In this case, ignore the new pending data as it
+                // is incomplete.
+                if let Err(e) = super::l2::download_new_classes(
+                    &state_update,
+                    sequencer,
+                    &tx_event,
+                    &pending.starknet_version,
+                    storage.clone(),
+                )
+                .await
+                {
+                    tracing::debug!(reason=?e, "Failed to download pending classes");
                 } else {
-                    tracing::trace!("No change in pending block data");
+                    prev_tx_count = pending.transactions.len();
+                    tracing::trace!("Emitting a pending update");
+                    let block = Arc::new(pending);
+                    let state_update = Arc::new(state_update);
+                    tx_event
+                        .send(SyncEvent::Pending(block, state_update))
+                        .await
+                        .context("Event channel closed")?;
                 }
             }
+            MaybePendingBlock::Pending(_) => {
+                // Pending data was not newer than the previous iteration.
+                tracing::trace!("No change in pending block data");
+            }
         }
 
         tokio::time::sleep_until(t_fetch + poll_interval).await;
     }
 }
 
-async fn download_classes_and_emit_event<S: GatewayApi + Clone + Send + 'static>(
-    tx_event: &tokio::sync::mpsc::Sender<SyncEvent>,
-    sequencer: &S,
-    storage: &Storage,
-    block: Arc<PendingBlock>,
-    state_update: Arc<StateUpdate>,
-) -> anyhow::Result<()> {
-    tracing::trace!("Downloading classes for pending state update");
-
-    // Download, process and emit all missing classes.
-    super::l2::download_new_classes(
-        &state_update,
-        sequencer,
-        tx_event,
-        &block.starknet_version,
-        storage.clone(),
-    )
-    .await
-    .context("Handling newly declared classes for pending block")?;
-
-    tracing::trace!("Emitting a pending update");
-    tx_event
-        .send(SyncEvent::Pending(block, state_update))
-        .await
-        .context("Event channel closed")
-}
-
 #[cfg(test)]
 mod tests {
     use std::sync::Arc;
```
