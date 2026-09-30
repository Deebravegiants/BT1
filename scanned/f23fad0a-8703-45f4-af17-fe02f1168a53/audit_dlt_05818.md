# [?] fix(indexer): surface shard-tracking errors instead of panicking on restart (#15872)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-06-29
Source: https://github.com/near/nearcore/commit/fec195197c76dca36853cfb62664d28b13b4cf4b
Type: security-commit

## Details
fix(indexer): surface shard-tracking errors instead of panicking on restart (#15872)

`build_streamer_message` used to panic with "`receipt` must be present
at this moment" on restart (issue
https://github.com/near/nearcore/issues/15867, Mode A).
The chain was: on restart `ShardTracker::cares_about_shard` runs an
epoch lookup that can fail transiently and masks the error as `false`,
so `fetch_block_new_chunks` spuriously drops a chunk for a shard the
node actually tracks.
That shard's execution outcomes are then never classified by the
per-chunk loop and fall into the leftover loop, which unwrapped a `None`
receipt on the shard's transaction outcomes and panicked.

Fixes the root cause for the indexer:

- shard_tracker: add `ShardTracker::cares_about_shard_result`, which
returns the `EpochError` instead of masking it. `cares_about_shard` and
friends keep their bool signatures via a thin `unwrap_or(false)`, so
consensus call sites are unchanged; only the indexer opts into the
fallible variant.
- `fetch_block_new_chunks` now propagates that error, so
`build_streamer_message` returns `Err` and the streamer retries the
block instead of producing a message with orphaned outcomes.

Caveat:
Re-indexing historical blocks produced before a node adopted
https://github.com/near/nearcore/pull/14981 would have `receipt: None`
with no store entry, and now errors (streamer retries) instead of
reconstructing.

Partially fixed #15867 (Mode A).

## Patch
### Cargo.lock
```diff
@@ -4563,7 +4563,6 @@ dependencies = [
  "near-store",
  "nearcore",
  "node-runtime",
- "parking_lot 0.12.1",
  "rocksdb",
  "tokio",
  "tracing",
```

### chain/epoch-manager/src/shard_tracker.rs
```diff
@@ -173,33 +173,32 @@ impl ShardTracker {
         shard_id: ShardId,
         is_me: bool,
         epoch_selection: EpochSelection,
-    ) -> bool {
-        // TODO: fix these unwrap_or here and handle error correctly. The current behavior masks potential errors and bugs
-        // https://github.com/near/nearcore/issues/4936
+    ) -> Result<bool, EpochError> {
         if let Some(account_id) = account_id {
             let account_cares_about_shard = match epoch_selection {
-                EpochSelection::Previous => self
-                    .epoch_manager
-                    .cared_about_shard_prev_epoch_from_prev_block(prev_hash, account_id, shard_id)
-                    .unwrap_or(false),
+                EpochSelection::Previous => {
+                    self.epoch_manager.cared_about_shard_prev_epoch_from_prev_block(
+                        prev_hash, account_id, shard_id,
+                    )?
+                }
                 EpochSelection::Current => self
                     .epoch_manager
-                    .cares_about_shard_from_prev_block(prev_hash, account_id, shard_id)
-                    .unwrap_or(false),
-                EpochSelection::Next => self
-                    .epoch_manager
-                    .cares_about_shard_next_epoch_from_prev_block(prev_hash, account_id, shard_id)
-                    .unwrap_or(false),
+                    .cares_about_shard_from_prev_block(prev_hash, account_id, shard_id)?,
+                EpochSelection::Next => {
+                    self.epoch_manager.cares_about_shard_next_epoch_from_prev_block(
+                        prev_hash, account_id, shard_id,
+                    )?
+                }
             };
 
             if account_cares_about_shard {
                 // An account has to track this shard because of its validation duties.
-                return true;
+                return Ok(true);
             }
             if !is_me {
                 // We don't know how another node is configured.
                 // It may track all shards, it may track no additional shards.
-                return false;
+                return Ok(false);
             } else {
                 // We have access to the node config. Use the config to find a definite answer.
             }
@@ -208,20 +207,20 @@ impl ShardTracker {
         match self.tracked_shards_config {
             TrackedShardsConfig::NoShards => {
                 // Avoid looking up EpochId as a performance optimization.
-                false
+                Ok(false)
             }
             TrackedShardsConfig::AllShards => {
                 // Avoid looking up EpochId as a performance optimization.
-                true
+                Ok(true)
             }
             _ => match epoch_selection {
-                EpochSelection::Previous => self
-                    .tracks_shard_prev_epoch_from_prev_block(shard_id, prev_hash)
-                    .unwrap_or(false),
-                EpochSelection::Current => self.tracks_shard(shard_id, prev_hash).unwrap_or(false),
-                EpochSelection::Next => self
-                    .tracks_shard_next_epoch_from_prev_block(shard_id, prev_hash)
-                    .unwrap_or(false),
+                EpochSelection::Previous => {
+                    self.tracks_shard_prev_epoch_from_prev_block(shard_id, prev_hash)
+                }
+                EpochSelection::Current => self.tracks_shard(shard_id, prev_hash),
+                EpochSelection::Next => {
+                    self.tracks_shard_next_epoch_from_prev_block(shard_id, prev_hash)
+                }
             },
         }
     }
@@ -238,13 +237,15 @@ impl ShardTracker {
         shard_id: ShardId,
     ) -> bool {
         let account_id = self.validator_signer.get().map(|v| v.validator_id().clone());
+        // Masks `EpochError` as `false`, see [`Self::cares_about_shard`] and #4936.
         self.cares_about_shard_in_epoch_from_prev_hash(
             account_id.as_ref(),
             prev_hash,
             shard_id,
             true,
             EpochSelection::Previous,
         )
+        .unwrap_or(false)
     }
 
     /// All `ShardUId`s this client tracks in the current epoch at `parent_hash`.
@@ -278,7 +279,22 @@ impl ShardTracker {
     }
 
     /// Whether the client cares about some shard right now.
+    ///
+    /// Masks any `EpochError` from the underlying epoch lookup as `false` (#4936),
+    /// which can spuriously report "not tracked" on restart before epoch data is
+    /// available. Callers that need to distinguish a real lookup error from
+    /// "definitely not tracked" should use [`Self::cares_about_shard_checked`].
     pub fn cares_about_shard(&self, parent_hash: &CryptoHash, shard_id: ShardId) -> bool {
+        self.cares_about_shard_checked(parent_hash, shard_id).unwrap_or(false)
+    }
+
+    /// Like [`Self::cares_about_shard`] but surfaces the epoch-lookup error
+    /// instead of masking it as `false`.
+    pub fn cares_about_shard_checked(
+        &self,
+        parent_hash: &CryptoHash,
+        shard_id: ShardId,
+    ) -> Result<bool, EpochError> {
         let account_id = self.validator_signer.get().map(|v| v.validator_id().clone());
         self.cares_about_shard_in_epoch_from_prev_hash(
             account_id.as_ref(),
@@ -295,13 +311,15 @@ impl ShardTracker {
     /// change next epoch, return true if it cares about any shard that `shard_id` will split to
     pub fn will_care_about_shard(&self, parent_hash: &CryptoHash, shard_id: ShardId) -> bool {
         let account_id = self.validator_signer.get().map(|v| v.validator_id().clone());
+        // Masks `EpochError` as `false`, see [`Self::cares_about_shard`] and #4936.
         self.cares_about_shard_in_epoch_from_prev_hash(
             account_id.as_ref(),
             parent_hash,
             shard_id,
             true,
             EpochSelection::Next,
         )
+        .unwrap_or(false)
     }
 
     /// Whether the client cares about some shard in this or next epoch.
@@ -327,20 +345,25 @@ impl ShardTracker {
         parent_hash: &CryptoHash,
         shard_id: ShardId,
     ) -> bool {
-        let cares_about_shard = self.cares_about_shard_in_epoch_from_prev_hash(
-            Some(account_id),
-            parent_hash,
-            shard_id,
-            false,
-            EpochSelection::Current,
-        );
-        let will_care_about_shard = self.cares_about_shard_in_epoch_from_prev_hash(
-            Some(account_id),
-            parent_hash,
-            shard_id,
-            false,
-            EpochSelection::Next,
-        );
+        // Masks `EpochError` as `false`, see [`Self::cares_about_shard`] and #4936.
+        let cares_about_shard = self
+            .cares_about_shard_in_epoch_from_prev_hash(
+                Some(account_id),
+                parent_hash,
+                shard_id,
+                false,
+                EpochSelection::Current,
+            )
+            .unwrap_or(false);
+        let will_care_about_shard = self
+            .cares_about_shard_in_epoch_from_prev_hash(
+                Some(account_id),
+                parent_hash,
+                shard_id,
+                false,
+                EpochSelection::Next,
+            )
+            .unwrap_or(false);
         cares_about_shard || will_care_about_shard
     }
 
```

### chain/indexer/Cargo.toml
```diff
@@ -14,7 +14,6 @@ workspace = true
 [dependencies]
 anyhow.workspace = true
 futures.workspace = true
-parking_lot.workspace = true
 rocksdb.workspace = true
 tokio.workspace = true
 tracing.workspace = true
```

### chain/indexer/src/streamer/fetchers.rs
```diff
@@ -101,15 +101,24 @@ impl IndexerViewClientFetcher {
         shard_tracker: &ShardTracker,
     ) -> Result<Vec<ChunkView>, FailedToFetchData> {
         tracing::debug!(target: INDEXER, height = block.header.height,  "fetch chunks for block");
-        let mut futures: futures::stream::FuturesUnordered<_> = block
-            .chunks
-            .iter()
-            .filter(|chunk| {
-                shard_tracker.cares_about_shard(&block.header.prev_hash, chunk.shard_id)
-                    && chunk.is_new_chunk(block.header.height)
-            })
-            .map(|chunk| self.fetch_single_chunk(chunk.chunk_hash))
-            .collect();
+        let mut futures = futures::stream::FuturesUnordered::new();
+        for chunk in &block.chunks {
+            if !chunk.is_new_chunk(block.header.height) {
+                continue;
+            }
+            let cares_about_shard = shard_tracker
+                .cares_about_shard_checked(&block.header.prev_hash, chunk.shard_id)
+                .map_err(|err| {
+                    FailedToFetchData::String(format!(
+                        "failed to determine shard tracking for shard {} at block {}: {err}",
+                        chunk.shard_id, block.header.hash,
+                    ))
+                })?;
+            if !cares_about_shard {
+                continue;
+            }
+            futures.push(self.fetch_single_chunk(chunk.chunk_hash));
+        }
         let mut chunks = Vec::<ChunkView>::with_capacity(futures.len());
         while let Some(chunk) = futures.next().await {
             chunks.push(chunk?);
```

### chain/indexer/src/streamer/metrics.rs
```diff
@@ -43,12 +43,3 @@ pub(crate) static BUILD_STREAMER_MESSAGE_TIME: LazyLock<Histogram> = LazyLock::n
     )
     .unwrap()
 });
-
-pub(crate) static LOCAL_RECEIPT_LOOKUP_IN_HISTORY_BLOCKS_BACK: LazyLock<IntGauge> =
-    LazyLock::new(|| {
-        try_create_int_gauge(
-            "near_indexer_local_receipt_lookup_in_history_blocks_back",
-            "Time taken to lookup a receipt in history blocks back",
-        )
-        .unwrap()
-    });
```

### chain/indexer/src/streamer/mod.rs
```diff
@@ -10,29 +10,30 @@ use near_indexer_primitives::{
     IndexerExecutionOutcomeWithReceipt, IndexerShard, IndexerTransactionWithOutcome,
     StreamerMessage,
 };
-use near_parameters::RuntimeConfig;
 use near_primitives::hash::CryptoHash;
 use near_primitives::receipt::ReceiptSource;
-use near_primitives::types::{Balance, BlockHeight, EpochId, ShardId};
+use near_primitives::types::{BlockHeight, EpochId, ShardId};
 use near_primitives::version::ProtocolFeature;
-use near_primitives::views::{BlockView, ChunkView, ExecutionStatusView, ReceiptView};
-use parking_lot::RwLock;
+use near_primitives::views::{BlockView, ChunkView, ReceiptView};
 use rocksdb::DB;
 use std::collections::HashMap;
-use std::sync::Arc;
 use tokio::sync::mpsc;
 
 mod errors;
 mod fetchers;
 mod metrics;
 mod utils;
 
-static DELAYED_LOCAL_RECEIPTS_CACHE: std::sync::LazyLock<
-    Arc<RwLock<HashMap<CryptoHash, ReceiptView>>>,
-> = std::sync::LazyLock::new(|| Arc::new(RwLock::new(HashMap::new())));
-
 const INTERVAL: Duration = Duration::milliseconds(250);
 
+/// How many consecutive times we retry building a streamer message for the same
+/// height before terminating. In `WaitForFullSync` mode, failures while the node
+/// is still syncing are expected (e.g. epoch data not yet available after a
+/// restart, see #15867) and do not count against this budget. In
+/// `StreamWhileSyncing` mode the node is ~always syncing, so every failure is
+/// counted - otherwise the budget would never be enforced.
+const MAX_BUILD_STREAMER_MESSAGE_ATTEMPTS: u32 = 10;
+
 /// This function supposed to return the entire `StreamerMessage`.
 /// It fetches the block and all related parts (chunks, outcomes, state changes etc.)
 /// and returns everything together in one struct
@@ -105,6 +106,7 @@ pub async fn build_streamer_message(
         // All transaction outcomes have been removed.
         let mut receipt_outcomes = outcomes;
 
+        // Local receipts recovered from shard-outcomes would miss the delayed ones.
         let chunk_local_receipts = convert_transactions_sir_into_local_receipts(
             indexer_transactions
                 .iter()
@@ -113,17 +115,6 @@ pub async fn build_streamer_message(
             gas_price,
         );
 
-        // Add local receipts to corresponding outcomes
-        for receipt in &chunk_local_receipts {
-            if let Some(outcome) = receipt_outcomes.get_mut(&receipt.receipt_id) {
-                if outcome.receipt.is_none() {
-                    outcome.receipt = Some(receipt.clone());
-                }
-            } else {
-                DELAYED_LOCAL_RECEIPTS_CACHE.write().insert(receipt.receipt_id, receipt.clone());
-            }
-        }
-
         let mut receipt_execution_outcomes: Vec<IndexerExecutionOutcomeWithReceipt> = vec![];
         for outcome_id in outcome_order {
             let Some(outcome) = receipt_outcomes.remove(&outcome_id) else {
@@ -132,34 +123,13 @@ pub async fn build_streamer_message(
             };
 
             let IndexerExecutionOutcomeWithOptionalReceipt { execution_outcome, receipt } = outcome;
-            let receipt = if let Some(receipt) = receipt {
-                receipt
-            } else {
-                // Attempt to extract the receipt or decide to fetch it based on cache access success
-                let maybe_receipt =
-                    DELAYED_LOCAL_RECEIPTS_CACHE.write().remove(&execution_outcome.id);
-
-                // Depending on whether you got the receipt from the cache, proceed
-                if let Some(receipt) = maybe_receipt {
-                    // Receipt was found in cache
-                    receipt
-                } else {
-                    // Receipt not found in cache or failed to acquire lock, proceed to look it up
-                    // in the history of blocks (up to 1000 blocks back)
-                    tracing::warn!(
-                        target: INDEXER,
-                        receipt_id = ?execution_outcome.id,
-                        "receipt is missing in block and in DELAYED_LOCAL_RECEIPTS_CACHE, looking for it in up to 1000 blocks back in time",
-                    );
-                    lookup_delayed_local_receipt_in_previous_blocks(
-                        &client,
-                        &runtime_config,
-                        block.clone(),
-                        execution_outcome.id,
-                        shard_tracker,
-                    )
-                    .await?
-                }
+            let Some(receipt) = receipt else {
+                // A receipt-execution outcome must have its receipt. A `None` here is
+                // unexpected; return an error so the streamer handles the error.
+                return Err(FailedToFetchData::String(format!(
+                    "missing receipt for execution outcome {} in block {}",
+                    execution_outcome.id, block.header.hash,
+                )));
             };
             receipt_execution_outcomes
                 .push(IndexerExecutionOutcomeWithReceipt { execution_outcome, receipt });
@@ -187,24 +157,32 @@ pub async fn build_streamer_message(
         });
     }
 
-    // Ideally we expect `shards_outcomes` to be empty by this time, but if something went wrong with
-    // chunks and we end up with non-empty `shards_outcomes` we want to be sure we put them into IndexerShard
-    // That might happen before the fix https://github.com/near/nearcore/pull/4228
-    for (shard_id, outcomes) in shards_outcomes {
-        // The chunk may be missing and if that happens in the first block after
-        // resharding the shard id would no longer be valid in the new shard
-        // layout. In this case we can skip the chunk.
-        let shard_index = protocol_config_view.shard_layout.get_shard_index(shard_id);
-        let Ok(shard_index) = shard_index else {
-            continue;
-        };
-
-        indexer_shards[shard_index].receipt_execution_outcomes.extend(outcomes.into_iter().map(
-            |outcome| IndexerExecutionOutcomeWithReceipt {
-                execution_outcome: outcome.execution_outcome,
-                receipt: outcome.receipt.expect("`receipt` must be present at this moment"),
-            },
-        ))
+    // By this point every shard the indexer streams has had its outcomes
+    // consumed by the per-chunk loop above. Any leftover in `shards_outcomes` is
+    // an outcome for a shard whose chunk was not streamed, which we can only
+    // observe in two situations:
+    //   (a) the indexer's `ShardTracker` excludes a shard the node itself
+    //       tracked (the node has the outcomes but the chunk was not streamed);
+    //   (b) the post-resharding edge case where a stale shard id is no longer
+    //       part of the new layout.
+    //
+    // Both are unexpected and would require a proper fix to surface correctly
+    // (reliably classifying transaction vs receipt outcomes, aligning the
+    // indexer's `ShardTracker` with the shards the node tracked, and handling
+    // the stale-shard-id case in the per-chunk loop). For now we log
+    // a warning so the indexer operator knows something is off.
+    //
+    // TODO: eliminate leftovers entirely by addressing (a) and (b) above
+    // and emitting these outcomes through the per-chunk loop.
+    if !shards_outcomes.is_empty() {
+        let leftover_outcomes: usize = shards_outcomes.values().map(Vec::len).sum();
+        tracing::warn!(
+            target: INDEXER,
+            block_hash = %block.header.hash,
+            leftover_shards = ?shards_outcomes.keys().collect::<Vec<_>>(),
+            leftover_outcomes,
+            "execution outcomes left after streaming all chunks; they are not included in the streamer message",
+        );
     }
 
     Ok(StreamerMessage { block, shards: indexer_shards })
@@ -263,110 +241,17 @@ async fn fetch_instant_receipts(
     instant_receipts
 }
 
-// Receipt might be missing only in case of delayed local receipt
-// that appeared in some of the previous blocks
-// we will be iterating over previous blocks until we found the receipt
-// or panic if we didn't find it in 1000 blocks
-async fn lookup_delayed_local_receipt_in_previous_blocks(
-    client: &IndexerViewClientFetcher,
-    runtime_config: &RuntimeConfig,
-    source_block: BlockView,
-    receipt_id: CryptoHash,
-    shard_tracker: &ShardTracker,
-) -> Result<ReceiptView, FailedToFetchData> {
-    let mut block = client.fetch_block(source_block.header.prev_hash).await?;
-    for prev_block_tried in 0..1000 {
-        if prev_block_tried % 100 == 99 {
-            tracing::warn!(
-                target: INDEXER,
-                block_hash = %source_block.header.hash,
-                %receipt_id,
-                prev_block_tried,
-                "still looking for receipt in previous blocks",
-            );
+/// Whether the node reports it is fully synced and in a steady state. A failed
+/// status fetch is treated as "not ready" so we don't prematurely give up while
+/// the node is not in a steady state.
+async fn node_is_ready(client: &IndexerClientFetcher) -> bool {
+    match client.fetch_status().await {
+        Ok(status) => !status.sync_info.syncing,
+        Err(err) => {
+            tracing::warn!(target: INDEXER, ?err, "failed to fetch node status, assuming the node is not ready");
+            false
         }
-        let (prev_block, gas_price) = if block.header.prev_hash == CryptoHash::default() {
-            (None, block.header.gas_price)
-        } else {
-            let prev_block = client.fetch_block(block.header.prev_hash).await?;
-            let gas_price = prev_block.header.gas_price;
-            (Some(prev_block), gas_price)
-        };
-
-        if let Some(receipt) = find_local_receipt_by_id_in_block(
-            receipt_id,
-            &block,
-            client,
-            &runtime_config,
-            shard_tracker,
-            gas_price,
-        )
-        .await?
-        {
-            tracing::debug!(
-                target: INDEXER,
-                %receipt_id,
-                prev_block_tried,
-                "found receipt in previous block",
-            );
-            metrics::LOCAL_RECEIPT_LOOKUP_IN_HISTORY_BLOCKS_BACK.set(prev_block_tried as i64);
-            return Ok(receipt);
-        }
-        block = prev_block.unwrap_or_else(|| {
-            panic!("reached genesis and failed to find local receipt {receipt_id}")
-        });
     }
-    panic!("failed to find local receipt {receipt_id} in 1000 prev blocks");
-}
-
-async fn find_local_receipt_by_id_in_block(
-    receipt_id: CryptoHash,
-    block: &BlockView,
-    client: &IndexerViewClientFetcher,
-    runtime_config: &RuntimeConfig,
-    shard_tracker: &ShardTracker,
-    gas_price: Balance,
-) -> Result<Option<ReceiptView>, FailedToFetchData> {
-    let new_chunks = client.fetch_block_new_chunks(&block, shard_tracker).await?;
-    let mut outcomes = client.fetch_outcomes(block.header.hash).await?;
-
-    for chunk in new_chunks {
-        let ChunkView { header, transactions, .. } = chunk;
-        let shard_outcomes = outcomes
-            .remove(&header.shard_id)
-            .expect("execution outcomes for given shard should be present");
-
-        let Some(tx_outcome) = shard_outcomes.into_iter().find(|outcome| {
-            if let ExecutionStatusView::SuccessReceiptId(outcome_receipt_id) =
-                outcome.outcome.status
-            {
-                outcome_receipt_id == receipt_id
-            } else {
-                false
-            }
-        }) else {
-            continue;
-        };
-        let tx_hash = tx_outcome.id;
-        let tx = transactions.into_iter().find(|tx| tx.hash == tx_hash)
-            .unwrap_or_else(|| panic!(
-                "failed to find transaction {} that generated local receipt {} in block {} shard {}",
-                tx_hash, receipt_id, block.header.hash, header.shard_id
-            ));
-        let indexer_tx = IndexerTransactionWithOutcome {
-            transaction: tx,
-            outcome: IndexerExecutionOutcomeWithOptionalReceipt {
-                execution_outcome: tx_outcome,
-                receipt: None,
-            },
-        };
-
-        let local_receipts =
-            convert_transactions_sir_into_local_receipts([&indexer_tx], &runtime_config, gas_price);
-        assert_eq!(local_receipts.len(), 1);
-        return Ok(local_receipts.into_iter().next());
-    }
-    Ok(None)
 }
 
 /// Function that starts Streamer's busy loop. Every half a seconds it fetches the status
@@ -392,6 +277,10 @@ pub async fn start(
     };
 
     let mut last_synced_block_height: Option<BlockHeight> = None;
+    // Consecutive failed attempts to build a streamer message; reset on success.
+    // In `WaitForFullSync` mode it is also reset while the node is syncing (see
+    // `MAX_BUILD_STREAMER_MESSAGE_ATTEMPTS`).
+    let mut build_streamer_message_attempts: u32 = 0;
 
     'main: loop {
         clock.sleep(INTERVAL).await;
@@ -450,9 +339,38 @@ pub async fn start(
 
             let streamer_message =
                 Box::pin(build_streamer_message(&view_client, block, &shard_tracker)).await;
-            let Ok(streamer_message) = streamer_message else {
-                tracing::error!(target: INDEXER, ?block_height, ?streamer_message, "failed to build streamer message, skipping");
-                continue;
+            let streamer_message = match streamer_message {
+                Ok(streamer_message) => {
+                    build_streamer_message_attempts = 0;
+                    streamer_message
+                }
+                Err(err) => {
+                    // When waiting for full sync, a build failure while the node
+                    // is not yet ready is expected (e.g. epoch data not available
+                    // after a restart, see #15867): retry the same height forever
+                    // without counting it against the budget. When streaming while
+                    // syncing the node is ~always "syncing", so that gate would
+                    // make the budget unreachable; there we count every failure so
+                    // a genuinely stuck height eventually surfaces.
+                    let transient_while_syncing = matches!(
+                        indexer_config.await_for_node_synced,
+                        AwaitForNodeSyncedEnum::WaitForFullSync
+                    ) && !node_is_ready(&client).await;
+                    if transient_while_syncing {
+                        build_streamer_message_attempts = 0;
+                        tracing::warn!(target: INDEXER, ?block_height, ?err, "failed to build streamer message while the node is syncing, retrying the same height");
+                    } else {
+                        build_streamer_message_attempts += 1;
+                        tracing::error!(target: INDEXER, ?block_height, ?err, attempts = build_streamer_message_attempts, "failed to build streamer message, retrying the same height");
+                        assert!(
+                            build_streamer_message_attempts < MAX_BUILD_STREAMER_MESSAGE_ATTEMPTS,
+                            "failed to build streamer message at height {block_height} after {MAX_BUILD_STREAMER_MESSAGE_ATTEMPTS} attempts: {err:?}"
+                        );
+                    }
+                    // Retry the same height on the next outer iteration instead of
+                    // advancing `last_synced_block_height`.
+                    break;
+                }
             };
 
             tracing::debug!(target: INDEXER, ?block_height, "sending streamer message to the listener");
```

### test-loop-tests/src/tests/indexer.rs
```diff
@@ -8,6 +8,7 @@ use near_async::futures::FutureSpawnerExt;
 use near_async::time::Duration;
 use near_client::NetworkAdversarialMessage;
 use near_client::client_actor::AdvProduceChunksMode;
+use near_epoch_manager::shard_tracker::ShardTracker;
 use near_indexer::{
     AwaitForNodeSyncedEnum, IndexerConfig, IndexerExecutionOutcomeWithReceipt, StreamerMessage,
     SyncModeEnum, start,
@@ -454,6 +455,17 @@ fn setup() -> TestLoopEnv {
 }
 
 fn start_indexer(env: &TestLoopEnv, sync_mode: SyncModeEnum) -> mpsc::Receiver<StreamerMessage> {
+    let node_data = &env.node_datas[0];
+    let client = &env.test_loop.data.get(&node_data.client_sender.actor_handle()).client;
+    let shard_tracker = client.shard_tracker.clone();
+    start_indexer_with_shard_tracker(env, sync_mode, shard_tracker)
+}
+
+fn start_indexer_with_shard_tracker(
+    env: &TestLoopEnv,
+    sync_mode: SyncModeEnum,
+    shard_tracker: ShardTracker,
+) -> mpsc::Receiver<StreamerMessage> {
     let node_data = &env.node_datas[0];
     let indexer_config = IndexerConfig {
         home_dir: NodeExecutionData::homedir(&env.shared_state.tempdir, &node_data.identifier),
@@ -463,8 +475,6 @@ fn start_indexer(env: &TestLoopEnv, sync_mode: SyncModeEnum) -> mpsc::Receiver<S
         validate_genesis: false,
     };
 
-    let client = &env.test_loop.data.get(&node_data.client_sender.actor_handle()).client;
-    let shard_tracker = client.shard_tracker.clone();
     let store_config =
         StoreConfig { path: Some(indexer_config.home_dir.clone()), ..Default::default() };
     let (sender, receiver) = tokio::sync::mpsc::channel(100);
```
