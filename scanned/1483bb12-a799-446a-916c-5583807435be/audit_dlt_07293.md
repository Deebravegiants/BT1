# [?] fix(state-sync): Remove `state_fetch_horizon` because it causes nodes to crash (#9380)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2023-08-07
Source: https://github.com/near/nearcore/commit/7a25e7d9af195c36430515fdb4c8432837922400
Type: security-commit

## Details
fix(state-sync): Remove `state_fetch_horizon` because it causes nodes to crash (#9380)

The main issue is that `find_sync_hash()` is not consistent with `check_state_needed()`.
`check_state_needed` compares epoch_id of header_head and head.
`find_sync_hash()` moves back a number of blocks before determining which epoch to sync.
It can lead to a node deciding to state sync, and downloading the same state again.

I've observed that it leads to a crash in this complicated scenario:
* State sync to epoch X
* Finalize the state sync and execute block at height H
* Check orphans and unblock a block at height H+1
* At the same time check if a node needs a state sync - determine that yes, and reset Flat Storage to prepare it to execute a block at height H.
* The orhpaned block gets executed, but flat storage doesn't support height H+1, leading to a panic.

## Patch
### Cargo.lock
```diff
@@ -3749,6 +3749,7 @@ dependencies = [
  "nearcore",
  "rayon",
  "tqdm",
+ "tracing",
 ]
 
 [[package]]
```

### chain/client-primitives/src/types.rs
```diff
@@ -1,5 +1,5 @@
 use actix::Message;
-use ansi_term::Color::{Purple, Yellow};
+use ansi_term::Color::Purple;
 use ansi_term::Style;
 use chrono::DateTime;
 use chrono::Utc;
@@ -231,31 +231,16 @@ pub fn format_shard_sync_phase(
         ShardSyncStatus::StateDownloadParts => {
             let mut num_parts_done = 0;
             let mut num_parts_not_done = 0;
-            let mut text = "".to_string();
-            for (i, download) in shard_sync_download.downloads.iter().enumerate() {
+            for download in shard_sync_download.downloads.iter() {
                 if download.done {
                     num_parts_done += 1;
-                    continue;
+                } else {
+                    num_parts_not_done += 1;
                 }
-                num_parts_not_done += 1;
-                text.push_str(&format!(
-                    "[{}: {}, {}, {:?}] ",
-                    paint(&i.to_string(), Yellow.bold(), use_colour),
-                    download.done,
-                    download.state_requests_count,
-                    download.last_target
-                ));
             }
-            format!(
-                "{} [{}: is_done, requests sent, last target] {} num_parts_done={} num_parts_not_done={}",
-                paint("PARTS", Purple.bold(), use_colour),
-                paint("part_id", Yellow.bold(), use_colour),
-                text,
-                num_parts_done,
-                num_parts_not_done
-            )
+            format!("num_parts_done={num_parts_done} num_parts_not_done={num_parts_not_done}")
         }
-        status => format!("{:?}", status),
+        status => format!("{status:?}"),
     }
 }
 
```

### chain/client/src/client_actor.rs
```diff
@@ -1491,30 +1491,21 @@ impl ClientActor {
     ///
     /// The selected block will always be the first block on a new epoch:
     /// <https://github.com/nearprotocol/nearcore/issues/2021#issuecomment-583039862>.
-    ///
-    /// To prevent syncing from a fork, we move `state_fetch_horizon` steps backwards and use that epoch.
-    /// Usually `state_fetch_horizon` is much less than the expected number of produced blocks on an epoch,
-    /// so this is only relevant on epoch boundaries.
     fn find_sync_hash(&mut self) -> Result<CryptoHash, near_chain::Error> {
         let header_head = self.client.chain.header_head()?;
-        let mut sync_hash = header_head.prev_block_hash;
-        for _ in 0..self.client.config.state_fetch_horizon {
-            sync_hash = *self.client.chain.get_block_header(&sync_hash)?.prev_hash();
-        }
-        let mut epoch_start_sync_hash =
+        let sync_hash = header_head.last_block_hash;
+        let epoch_start_sync_hash =
             StateSync::get_epoch_start_sync_hash(&mut self.client.chain, &sync_hash)?;
 
-        if &epoch_start_sync_hash == self.client.chain.genesis().hash() {
-            // If we are within `state_fetch_horizon` blocks of the second epoch, the sync hash will
-            // be the first block of the first epoch (or, the genesis block). Due to implementation
-            // details of the state sync, we can't state sync to the genesis block, so redo the
-            // search without going back `state_fetch_horizon` blocks.
-            epoch_start_sync_hash = StateSync::get_epoch_start_sync_hash(
-                &mut self.client.chain,
-                &header_head.last_block_hash,
-            )?;
-            assert_ne!(&epoch_start_sync_hash, self.client.chain.genesis().hash());
-        }
+        let genesis_hash = self.client.chain.genesis().hash();
+        tracing::debug!(
+            target: "sync",
+            ?header_head,
+            ?sync_hash,
+            ?epoch_start_sync_hash,
+            ?genesis_hash,
+            "find_sync_hash");
+        assert_ne!(&epoch_start_sync_hash, genesis_hash);
         Ok(epoch_start_sync_hash)
     }
 
```

### chain/client/src/sync/block.rs
```diff
@@ -96,6 +96,18 @@ impl BlockSync {
                 && !self.archive
                 && self.state_sync_enabled
             {
+                tracing::debug!(
+                    target: "sync",
+                    head_epoch_id = ?head.epoch_id,
+                    header_head_epoch_id = ?header_head.epoch_id,
+                    head_next_epoch_id = ?head.next_epoch_id,
+                    head_height = head.height,
+                    header_head_height = header_head.height,
+                    header_head_height_sub = header_head.height.saturating_sub(self.block_fetch_horizon),
+                    archive = self.archive,
+                    state_sync_enabled = self.state_sync_enabled,
+                    block_fetch_horizon = self.block_fetch_horizon,
+                    "Switched from block sync to state sync");
                 // Epochs are different and we are too far from horizon, State Sync is needed
                 return Ok(true);
             }
```

### chain/client/src/sync/state.rs
```diff
@@ -33,6 +33,7 @@ use near_chain::near_chain_primitives;
 use near_chain::resharding::StateSplitRequest;
 use near_chain::Chain;
 use near_chain_configs::{ExternalStorageConfig, ExternalStorageLocation, SyncConfig};
+use near_client_primitives::types::format_shard_sync_phase_per_shard;
 use near_client_primitives::types::{
     format_shard_sync_phase, DownloadStatus, ShardSyncDownload, ShardSyncStatus,
 };
@@ -297,9 +298,6 @@ impl StateSync {
 
             let old_status = shard_sync_download.status.clone();
             let mut shard_sync_done = false;
-            metrics::STATE_SYNC_STAGE
-                .with_label_values(&[&shard_id.to_string()])
-                .set(shard_sync_download.status.repr() as i64);
             match &shard_sync_download.status {
                 ShardSyncStatus::StateDownloadHeader => {
                     (download_timeout, run_shard_state_download) = self
@@ -312,12 +310,8 @@ impl StateSync {
                         )?;
                 }
                 ShardSyncStatus::StateDownloadParts => {
-                    let res = self.sync_shards_download_parts_status(
-                        shard_id,
-                        shard_sync_download,
-                        sync_hash,
-                        now,
-                    );
+                    let res =
+                        self.sync_shards_download_parts_status(shard_id, shard_sync_download, now);
                     download_timeout = res.0;
                     run_shard_state_download = res.1;
                     update_sync_status |= res.2;
@@ -342,13 +336,8 @@ impl StateSync {
                     )?;
                 }
                 ShardSyncStatus::StateDownloadComplete => {
-                    shard_sync_done = self.sync_shards_download_complete_status(
-                        split_states,
-                        shard_id,
-                        shard_sync_download,
-                        sync_hash,
-                        chain,
-                    )?;
+                    shard_sync_done = self
+                        .sync_shards_download_complete_status(split_states, shard_sync_download);
                 }
                 ShardSyncStatus::StateSplitScheduling => {
                     debug_assert!(split_states);
@@ -374,6 +363,14 @@ impl StateSync {
                     shard_sync_done = true;
                 }
             }
+            let stage = if shard_sync_done {
+                // Update the state sync stage metric, because maybe we'll not
+                // enter this function again.
+                ShardSyncStatus::StateSyncDone.repr()
+            } else {
+                shard_sync_download.status.repr()
+            };
+            metrics::STATE_SYNC_STAGE.with_label_values(&[&shard_id.to_string()]).set(stage as i64);
             all_done &= shard_sync_done;
 
             if download_timeout {
@@ -407,6 +404,13 @@ impl StateSync {
             }
             update_sync_status |= shard_sync_download.status != old_status;
         }
+        if update_sync_status {
+            // Print debug messages only if something changed.
+            // Otherwise it spams the debug logs.
+            tracing::debug!(
+                target: "sync",
+                progress_per_shard = ?format_shard_sync_phase_per_shard(new_shard_sync, false));
+        }
 
         Ok((update_sync_status, all_done))
     }
@@ -951,7 +955,6 @@ impl StateSync {
         &mut self,
         shard_id: ShardId,
         shard_sync_download: &mut ShardSyncDownload,
-        sync_hash: CryptoHash,
         now: DateTime<Utc>,
     ) -> (bool, bool, bool) {
         // Step 2 - download all the parts (each part is usually around 1MB).
@@ -991,7 +994,6 @@ impl StateSync {
                 num_parts_done += 1;
             }
         }
-        tracing::debug!(target: "sync", %shard_id, %sync_hash, num_parts_done, parts_done);
         metrics::STATE_SYNC_PARTS_DONE
             .with_label_values(&[&shard_id.to_string()])
             .set(num_parts_done);
@@ -1058,8 +1060,7 @@ impl StateSync {
     ) -> Result<(), near_chain::Error> {
         // Keep waiting until our shard is on the list of results
         // (these are set via callback from ClientActor - both for sync and catchup).
-        let result = self.state_parts_apply_results.remove(&shard_id);
-        if let Some(result) = result {
+        if let Some(result) = self.state_parts_apply_results.remove(&shard_id) {
             match chain.set_state_finalize(shard_id, sync_hash, result) {
                 Ok(()) => {
                     *shard_sync_download = ShardSyncDownload {
@@ -1088,30 +1089,21 @@ impl StateSync {
     fn sync_shards_download_complete_status(
         &mut self,
         split_states: bool,
-        shard_id: ShardId,
         shard_sync_download: &mut ShardSyncDownload,
-        sync_hash: CryptoHash,
-        chain: &mut Chain,
-    ) -> Result<bool, near_chain::Error> {
-        let shard_state_header = chain.get_state_header(shard_id, sync_hash)?;
-        let state_num_parts =
-            get_num_state_parts(shard_state_header.state_root_node().memory_usage);
-        chain.clear_downloaded_parts(shard_id, sync_hash, state_num_parts)?;
-
-        let mut shard_sync_done = false;
+    ) -> bool {
         // If the shard layout is changing in this epoch - we have to apply it right now.
         if split_states {
             *shard_sync_download = ShardSyncDownload {
                 downloads: vec![],
                 status: ShardSyncStatus::StateSplitScheduling,
-            }
+            };
+            false
         } else {
             // If there is no layout change - we're done.
             *shard_sync_download =
                 ShardSyncDownload { downloads: vec![], status: ShardSyncStatus::StateSyncDone };
-            shard_sync_done = true;
+            true
         }
-        Ok(shard_sync_done)
     }
 
     fn sync_shards_state_split_scheduling_status(
```

### core/chain-configs/src/client_config.rs
```diff
@@ -212,8 +212,6 @@ pub struct ClientConfig {
     pub ttl_account_id_router: Duration,
     /// Horizon at which instead of fetching block, fetch full state.
     pub block_fetch_horizon: BlockHeightDelta,
-    /// Horizon to step from the latest block when fetching state.
-    pub state_fetch_horizon: NumBlocks,
     /// Time between check to perform catchup.
     pub catchup_step_period: Duration,
     /// Time between checking to re-request chunks.
@@ -318,7 +316,6 @@ impl ClientConfig {
             num_block_producer_seats,
             ttl_account_id_router: Duration::from_secs(60 * 60),
             block_fetch_horizon: 50,
-            state_fetch_horizon: 5,
             catchup_step_period: Duration::from_millis(1),
             chunk_request_retry_period: min(
                 Duration::from_millis(100),
```

### core/o11y/src/lib.rs
```diff
@@ -188,13 +188,18 @@ fn add_simple_log_layer<S, W>(
     filter: EnvFilter,
     writer: W,
     ansi: bool,
+    with_span_events: bool,
     subscriber: S,
 ) -> SimpleLogLayer<S, W>
 where
     S: tracing::Subscriber + for<'span> LookupSpan<'span> + Send + Sync,
     W: for<'writer> fmt::MakeWriter<'writer> + 'static,
 {
-    let layer = fmt::layer().with_ansi(ansi).with_writer(writer).with_filter(filter);
+    let layer = fmt::layer()
+        .with_ansi(ansi)
+        .with_span_events(get_fmt_span(with_span_events))
+        .with_writer(writer)
+        .with_filter(filter);
 
     subscriber.with(layer)
 }
@@ -337,7 +342,13 @@ pub fn default_subscriber(
     };
 
     let subscriber = tracing_subscriber::registry();
-    let subscriber = add_simple_log_layer(env_filter, make_writer, color_output, subscriber);
+    let subscriber = add_simple_log_layer(
+        env_filter,
+        make_writer,
+        color_output,
+        options.log_span_events,
+        subscriber,
+    );
 
     #[allow(unused_mut)]
     let mut io_trace_guard = None;
```

### integration-tests/src/tests/nearcore/sync_state_nodes.rs
```diff
@@ -349,8 +349,6 @@ fn sync_empty_state() {
                                             Duration::from_millis(200);
                                         near2.client_config.max_block_production_delay =
                                             Duration::from_millis(400);
-                                        near2.client_config.state_fetch_horizon =
-                                            state_sync_horizon;
                                         near2.client_config.block_header_fetch_horizon =
                                             block_header_fetch_horizon;
                                         near2.client_config.block_fetch_horizon =
@@ -482,7 +480,6 @@ fn sync_state_dump() {
                                     Duration::from_millis(300);
                                 near2.client_config.max_block_production_delay =
                                     Duration::from_millis(600);
-                                near2.client_config.state_fetch_horizon = state_sync_horizon;
                                 near2.client_config.block_header_fetch_horizon =
                                     block_header_fetch_horizon;
                                 near2.client_config.block_fetch_horizon = block_fetch_horizon;
```

### nearcore/res/example-config-gc.json
```diff
@@ -78,7 +78,6 @@
         },
         "produce_empty_blocks": true,
         "block_fetch_horizon": 50,
-        "state_fetch_horizon": 5,
         "block_header_fetch_horizon": 50,
         "catchup_step_period": {
             "secs": 0,
```

### nearcore/res/example-config-no-gc.json
```diff
@@ -78,7 +78,6 @@
         },
         "produce_empty_blocks": true,
         "block_fetch_horizon": 50,
-        "state_fetch_horizon": 5,
         "block_header_fetch_horizon": 50,
         "catchup_step_period": {
             "secs": 0,
```

### nearcore/src/config.rs
```diff
@@ -69,9 +69,6 @@ pub const MAX_BLOCK_WAIT_DELAY: u64 = 6_000;
 /// Horizon at which instead of fetching block, fetch full state.
 const BLOCK_FETCH_HORIZON: BlockHeightDelta = 50;
 
-/// Horizon to step from the latest block when fetching state.
-const STATE_FETCH_HORIZON: NumBlocks = 5;
-
 /// Behind this horizon header fetch kicks in.
 const BLOCK_HEADER_FETCH_HORIZON: BlockHeightDelta = 50;
 
@@ -181,6 +178,10 @@ fn default_view_client_threads() -> usize {
     4
 }
 
+fn default_log_summary_period() -> Duration {
+    Duration::from_secs(10)
+}
+
 fn default_doomslug_step_period() -> Duration {
     Duration::from_millis(100)
 }
@@ -213,8 +214,6 @@ pub struct Consensus {
     pub produce_empty_blocks: bool,
     /// Horizon at which instead of fetching block, fetch full state.
     pub block_fetch_horizon: BlockHeightDelta,
-    /// Horizon to step from the latest block when fetching state.
-    pub state_fetch_horizon: NumBlocks,
     /// Behind this horizon header fetch kicks in.
     pub block_header_fetch_horizon: BlockHeightDelta,
     /// Time between check to perform catchup.
@@ -259,7 +258,6 @@ impl Default for Consensus {
             max_block_wait_delay: Duration::from_millis(MAX_BLOCK_WAIT_DELAY),
             produce_empty_blocks: true,
             block_fetch_horizon: BLOCK_FETCH_HORIZON,
-            state_fetch_horizon: STATE_FETCH_HORIZON,
             block_header_fetch_horizon: BLOCK_HEADER_FETCH_HORIZON,
             catchup_step_period: Duration::from_millis(CATCHUP_STEP_PERIOD),
             chunk_request_retry_period: Duration::from_millis(CHUNK_REQUEST_RETRY_PERIOD),
@@ -308,6 +306,8 @@ pub struct Config {
     #[serde(skip_serializing_if = "Option::is_none")]
     pub save_trie_changes: Option<bool>,
     pub log_summary_style: LogSummaryStyle,
+    #[serde(default = "default_log_summary_period")]
+    pub log_summary_period: Duration,
     // Allows more detailed logging, for example a list of orphaned blocks.
     pub enable_multiline_logging: Option<bool>,
     /// Garbage collection configuration.
@@ -377,6 +377,7 @@ impl Default for Config {
             archive: false,
             save_trie_changes: None,
             log_summary_style: LogSummaryStyle::Colored,
+            log_summary_period: default_log_summary_period(),
             gc: GCConfig::default(),
             epoch_sync_enabled: true,
             view_client_threads: default_view_client_threads(),
@@ -658,14 +659,13 @@ impl NearConfig {
                     .header_sync_expected_height_per_second,
                 state_sync_timeout: config.consensus.state_sync_timeout,
                 min_num_peers: config.consensus.min_num_peers,
-                log_summary_period: Duration::from_secs(10),
+                log_summary_period: config.log_summary_period,
                 produce_empty_blocks: config.consensus.produce_empty_blocks,
                 epoch_length: genesis.config.epoch_length,
                 num_block_producer_seats: genesis.config.num_block_producer_seats,
                 ttl_account_id_router: config.network.ttl_account_id_router,
                 // TODO(1047): this should be adjusted depending on the speed of sync of state.
                 block_fetch_horizon: config.consensus.block_fetch_horizon,
-                state_fetch_horizon: config.consensus.state_fetch_horizon,
                 block_header_fetch_horizon: config.consensus.block_header_fetch_horizon,
                 catchup_step_period: config.consensus.catchup_step_period,
                 chunk_request_retry_period: config.consensus.chunk_request_retry_period,
```
