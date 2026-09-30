# [?] apollo_l1_events: bound catch-up commit-block backlog, abandoning it to L2 sync on overflow (#14590)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/sequencer
Published: 2026-07-09
Source: https://github.com/starkware-libs/sequencer/commit/405aae582ff4f9da0bd59acf6e36817cb7e65ef5
Type: security-commit

## Details
apollo_l1_events: bound catch-up commit-block backlog, abandoning it to L2 sync on overflow (#14590)

The catchupper's `commit_block_backlog` was an unbounded `Vec` populated by every
commit-block arriving above the provider's height during startup catch-up, and
drained only once L2 sync reached the target. A persistently slow or stalled sync
while the batcher keeps committing could grow it without limit (security finding
L-16).

Add a configurable `max_commit_block_backlog_len` (default 1,000,000) and a
`l1_message_provider_commit_block_backlog_len` gauge. On overflow (or a
non-sequential height that would tear the gapless run), `add_commit_block_to_backlog`
abandons the in-memory backlog and defers to L2 sync to re-drive the whole range up
to the tip: it clears the buffer, latches `backlog_overflowed`, and extends the sync
target. Buffered tip commits are redundant with what L2 sync re-delivers, so dropping
them costs latency (until sync unstalls), not correctness -- bounded memory, no gap,
no panic.

An earlier version returned a `CatchUpBacklogOverflow` error instead, but the batcher
swallows commit_block errors and advances (pinned by
`decision_reached_return_success_when_l1_commit_block_fails`), so the rejected height
was dropped downstream and the next tip commit tripped the sequentiality assert,
panicking the provider into a crash loop -- the opposite of the intended
degraded-but-recoverable behavior. Abandoning to sync closes that loop entirely.

The gauge is updated on each push, reset to 0 on abandon, and reset again when the
backlog drains at catch-up completion.

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### Cargo.lock
```diff
@@ -1827,6 +1827,8 @@ dependencies = [
  "futures",
  "indexmap 2.14.0",
  "itertools 0.12.1",
+ "metrics",
+ "metrics-exporter-prometheus",
  "mockall",
  "papyrus_base_layer",
  "pretty_assertions",
```

### crates/apollo_deployments/resources/app_configs/l1_events_provider_config.json
```diff
@@ -3,5 +3,6 @@
   "l1_events_provider_config.l1_handler_cancellation_timelock_seconds": 300,
   "l1_events_provider_config.l1_handler_consumption_timelock_seconds": 300.0,
   "l1_events_provider_config.l1_handler_proposal_cooldown_seconds": 70,
-  "l1_events_provider_config.dummy_mode": false
+  "l1_events_provider_config.dummy_mode": false,
+  "l1_events_provider_config.max_commit_block_backlog_len": 1000000
 }
```

### crates/apollo_deployments/resources/app_configs/replacer_l1_events_provider_config.json
```diff
@@ -3,5 +3,6 @@
   "l1_events_provider_config.l1_handler_cancellation_timelock_seconds": 300,
   "l1_events_provider_config.l1_handler_consumption_timelock_seconds": 300.0,
   "l1_events_provider_config.l1_handler_proposal_cooldown_seconds": 70,
+  "l1_events_provider_config.max_commit_block_backlog_len": 1000000,
   "l1_events_provider_config.startup_sync_sleep_retry_interval_seconds": 2
 }
```

### crates/apollo_l1_events/Cargo.toml
```diff
@@ -42,10 +42,13 @@ alloy.workspace = true
 apollo_base_layer_tests.workspace = true
 apollo_infra_utils = { workspace = true, features = ["testing"] }
 apollo_l1_events_types = { workspace = true, features = ["testing"] }
+apollo_metrics = { workspace = true, features = ["testing"] }
 apollo_state_sync_types = { workspace = true, features = ["testing"] }
 apollo_time = { workspace = true, features = ["testing"] }
 assert_matches.workspace = true
 itertools.workspace = true
+metrics.workspace = true
+metrics-exporter-prometheus.workspace = true
 mockall.workspace = true
 papyrus_base_layer = { workspace = true, features = ["testing"] }
 pretty_assertions.workspace = true
```

### crates/apollo_l1_events/src/catchupper.rs
```diff
@@ -2,13 +2,15 @@ use std::sync::atomic::{AtomicU64, AtomicU8, Ordering};
 use std::sync::Arc;
 use std::time::Duration;
 
-use apollo_l1_events_types::SharedL1EventsProviderClient;
+use apollo_l1_events_types::{L1EventsProviderResult, SharedL1EventsProviderClient};
 use apollo_state_sync_types::communication::SharedStateSyncClient;
 use indexmap::IndexSet;
 use starknet_api::block::BlockNumber;
 use starknet_api::transaction::TransactionHash;
 use tracing::{debug, warn};
 
+use crate::metrics::L1_MESSAGE_PROVIDER_COMMIT_BLOCK_BACKLOG_LEN;
+
 // When the Provider gets a commit_block that is too high, it starts catching up.
 // The commit is rejected by the provider, so it must use sync to catch up to the height of the
 // commit, including that height. The sync task continues until reaching the target height,
@@ -30,6 +32,14 @@ pub struct Catchupper {
     // Keep track of sync task for health checks and logging status.
     pub sync_task_handle: SyncTaskHandle,
     pub n_sync_health_check_failures: Arc<AtomicU8>,
+    /// Cap on `commit_block_backlog` length. Exceeding it abandons the in-memory backlog (rather
+    /// than dropping a single entry, which would tear a gap) and defers to L2 sync; see
+    /// `add_commit_block_to_backlog`.
+    pub max_commit_block_backlog_len: usize,
+    /// Set once the backlog is abandoned during a catch-up (cap hit, or a non-sequential height
+    /// that would tear the gapless run). While set, tip commits are no longer buffered: L2 sync
+    /// owns the whole range and only its target is extended. Cleared when catch-up completes.
+    pub backlog_overflowed: bool,
 }
 
 impl Catchupper {
@@ -41,6 +51,7 @@ impl Catchupper {
         l1_events_provider_client: SharedL1EventsProviderClient,
         sync_client: SharedStateSyncClient,
         sync_retry_interval: Duration,
+        max_commit_block_backlog_len: usize,
     ) -> Self {
         Self {
             sync_retry_interval,
@@ -49,6 +60,8 @@ impl Catchupper {
             sync_client,
             sync_task_handle: SyncTaskHandle::NotStartedYet,
             n_sync_health_check_failures: Default::default(),
+            max_commit_block_backlog_len,
+            backlog_overflowed: false,
             // This is overriden when starting the sync task (e.g., when provider starts
             // catching up).
             target_height: Default::default(),
@@ -68,17 +81,47 @@ impl Catchupper {
         &mut self,
         committed_txs: IndexSet<TransactionHash>,
         height: BlockNumber,
-    ) {
-        assert!(
-            self.commit_block_backlog
-                .last()
-                .is_none_or(|commit_block| commit_block.height.unchecked_next() == height),
-            "Heights should be sequential."
-        );
+    ) -> L1EventsProviderResult<()> {
+        // Already abandoned this catch-up's backlog: L2 sync owns the whole range now. Don't
+        // rebuild the buffer; just keep extending the sync target so the task drives the provider
+        // up to the latest tip height.
+        if self.backlog_overflowed {
+            self.update_target_height(height);
+            return Ok(());
+        }
+
+        let is_sequential = self
+            .commit_block_backlog
+            .last()
+            .is_none_or(|commit_block| commit_block.height.unchecked_next() == height);
+        let is_full = self.commit_block_backlog.len() >= self.max_commit_block_backlog_len;
+
+        // Two runtime-reachable conditions force us off the in-memory fast path: the backlog hit
+        // its cap (a stalled/lagging L2 sync let the tip race ahead), or a non-sequential height
+        // would tear a hole in the gapless run. Dropping any single entry would leave a permanent
+        // gap that corrupts the drain-time sequential invariant (and previously panicked the
+        // provider, since the batcher swallows the error and keeps advancing). Instead, abandon the
+        // backlog entirely and let the authoritative L2 sync re-drive every height up to the tip --
+        // bounded memory, no gap, no panic. The buffered commits are redundant: sync re-delivers
+        // the same heights, just with more latency while it is stalled.
+        if is_full || !is_sequential {
+            warn!(
+                "Catch-up commit-block backlog abandoned at height {height} (cap {}, sequential: \
+                 {is_sequential}); deferring to L2 sync to re-drive the range. L2 sync is likely \
+                 stalled or lagging.",
+                self.max_commit_block_backlog_len
+            );
+            self.backlog_overflowed = true;
+            self.commit_block_backlog.clear();
+            L1_MESSAGE_PROVIDER_COMMIT_BLOCK_BACKLOG_LEN.set_lossy(0_usize);
+            self.update_target_height(height);
+            return Ok(());
+        }
 
         debug!("Adding future commit-block to backlog at height: {height}");
-        self.commit_block_backlog
-            .push(CommitBlockBacklog { height, committed_txs: committed_txs.clone() });
+        self.commit_block_backlog.push(CommitBlockBacklog { height, committed_txs });
+        L1_MESSAGE_PROVIDER_COMMIT_BLOCK_BACKLOG_LEN.set_lossy(self.commit_block_backlog.len());
+        Ok(())
     }
 
     /// Spawns async task that produces and sends commit block messages to the provider, according
```

### crates/apollo_l1_events/src/l1_events_provider.rs
```diff
@@ -22,7 +22,7 @@ use starknet_api::transaction::TransactionHash;
 use tracing::{debug, error, info, instrument, trace, warn};
 
 use crate::catchupper::Catchupper;
-use crate::metrics::register_provider_metrics;
+use crate::metrics::{register_provider_metrics, L1_MESSAGE_PROVIDER_COMMIT_BLOCK_BACKLOG_LEN};
 use crate::transaction_manager::TransactionManager;
 use crate::L1EventsProviderConfig;
 
@@ -71,6 +71,7 @@ impl L1EventsProvider {
             l1_events_provider_client,
             state_sync_client,
             config.startup_sync_sleep_retry_interval_seconds,
+            config.max_commit_block_backlog_len,
         );
         Self {
             config,
@@ -87,6 +88,7 @@ impl L1EventsProvider {
             self.catchupper.l1_events_provider_client.clone(),
             self.catchupper.sync_client.clone(),
             self.config.startup_sync_sleep_retry_interval_seconds,
+            self.config.max_commit_block_backlog_len,
         );
     }
     // Functions Called by the scraper.
@@ -432,7 +434,7 @@ impl L1EventsProvider {
             Equal => self.apply_commit_block(committed_txs, Default::default()),
             // We're still syncing, backlog it, it'll get applied later.
             Greater => {
-                self.catchupper.add_commit_block_to_backlog(committed_txs, new_height);
+                self.catchupper.add_commit_block_to_backlog(committed_txs, new_height)?;
                 // No need to check the backlog or catchup completion, since those are only
                 // applicable if we just increased the provider's height, like in the `Equal` case.
                 return Ok(());
@@ -448,6 +450,12 @@ impl L1EventsProvider {
                 self.current_height
             );
             let backlog = std::mem::take(&mut self.catchupper.commit_block_backlog);
+            // The backlog is fully consumed below; reset its gauge to 0.
+            L1_MESSAGE_PROVIDER_COMMIT_BLOCK_BACKLOG_LEN.set_lossy(0_usize);
+            // Catch-up is finished; clear the overflow latch so a future catch-up starts buffering
+            // on the fast path again (a fresh catch-up also rebuilds the catchupper, but resetting
+            // here keeps the state coherent if the same catchupper is reused).
+            self.catchupper.backlog_overflowed = false;
             assert!(
                 backlog.is_empty()
                     || self.current_height == backlog.first().unwrap().height
```

### crates/apollo_l1_events/src/l1_events_provider_tests.rs
```diff
@@ -1,4 +1,5 @@
 use std::collections::HashMap;
+use std::sync::atomic::AtomicU64;
 use std::sync::{Arc, Mutex};
 use std::time::Duration;
 
@@ -24,6 +25,7 @@ use apollo_time::time::Clock;
 use assert_matches::assert_matches;
 use indexmap::IndexSet;
 use itertools::Itertools;
+use metrics_exporter_prometheus::PrometheusBuilder;
 use pretty_assertions::assert_eq;
 use rstest::rstest;
 use starknet_api::block::{BlockNumber, BlockTimestamp};
@@ -33,6 +35,7 @@ use starknet_api::tx_hash;
 
 use crate::catchupper::{Catchupper, CommitBlockBacklog, SyncTaskHandle};
 use crate::l1_events_provider::L1EventsProvider;
+use crate::metrics::{register_provider_metrics, L1_MESSAGE_PROVIDER_COMMIT_BLOCK_BACKLOG_LEN};
 use crate::test_utils::{
     l1_handler,
     make_catchupper,
@@ -415,6 +418,185 @@ async fn commit_block_backlog() {
     expected_l1_events_provider.assert_eq(&l1_events_provider);
 }
 
+/// Drives `commit_block` with strictly-increasing (`Greater`) heights while catching up, so each
+/// one is appended to the backlog. Returns the provider so callers can inspect/continue.
+fn provider_catching_up_with_backlog_cap(max_commit_block_backlog_len: usize) -> L1EventsProvider {
+    const STARTUP_HEIGHT: BlockNumber = BlockNumber(0);
+    let catchupper = make_catchupper!(backlog: [], max: max_commit_block_backlog_len);
+    L1EventsProviderContentBuilder::new()
+        .with_catchupper(catchupper)
+        .with_height(STARTUP_HEIGHT)
+        .with_state(ProviderState::CatchingUp)
+        .build_into_l1_provider()
+}
+
+#[test]
+fn backlog_below_cap_accepts_all_commits() {
+    const CAP: usize = 3;
+    let mut l1_events_provider = provider_catching_up_with_backlog_cap(CAP);
+
+    // Two commits, both above current height (0) -> backlogged, staying below the cap of 3.
+    for height in [BlockNumber(1), BlockNumber(2)] {
+        commit_block_no_rejected(&mut l1_events_provider, &[], height);
+    }
+
+    assert_eq!(l1_events_provider.catchupper.commit_block_backlog.len(), 2);
+}
+
+#[test]
+fn backlog_fills_exactly_to_cap_without_error() {
+    const CAP: usize = 3;
+    let mut l1_events_provider = provider_catching_up_with_backlog_cap(CAP);
+
+    // Exactly CAP commits fit (heights 1..=3, all above current height 0).
+    for height in [BlockNumber(1), BlockNumber(2), BlockNumber(3)] {
+        commit_block_no_rejected(&mut l1_events_provider, &[], height);
+    }
+
+    let backlog = &l1_events_provider.catchupper.commit_block_backlog;
+    assert_eq!(backlog.len(), CAP);
+    // The backlog must remain a gapless, strictly-sequential run.
+    assert_eq!(
+        backlog.iter().map(|commit_block| commit_block.height).collect::<Vec<_>>(),
+        vec![BlockNumber(1), BlockNumber(2), BlockNumber(3)]
+    );
+}
+
+// Regression test for the cap's recovery path (L-16 review).
+//
+// The batcher swallows `commit_block` errors and advances anyway (batcher.rs commit-block
+// handling is pinned by `decision_reached_return_success_when_l1_commit_block_fails`), so an
+// overflow height rejected by the provider is dropped downstream. Before the fix, the *next* tip
+// commit then tripped the "Heights should be sequential." assert and panicked the provider,
+// turning bounded memory into a crash loop -- the opposite of the intended degraded-but-recoverable
+// behavior. After the fix, overflow abandons the in-memory backlog and lets L2 sync re-drive the
+// range, so the follow-up commit is handled gracefully.
+#[test]
+fn commit_after_overflow_does_not_panic() {
+    const CAP: usize = 3;
+    let mut l1_events_provider = provider_catching_up_with_backlog_cap(CAP);
+
+    // Fill the backlog exactly to the cap (heights 1..=3, all above current height 0).
+    for height in [BlockNumber(1), BlockNumber(2), BlockNumber(3)] {
+        commit_block_no_rejected(&mut l1_events_provider, &[], height);
+    }
+
+    // Overflow commit. Mimic the batcher, which swallows the result and advances regardless.
+    let _overflow_result = l1_events_provider.commit_block([].into(), [].into(), BlockNumber(4));
+
+    // The next tip commit must be handled gracefully; pre-fix this panicked on the sequentiality
+    // assert in `add_commit_block_to_backlog`.
+    let result = l1_events_provider.commit_block([].into(), [].into(), BlockNumber(5));
+    assert_matches!(result, Ok(()));
+
+    // Overflow abandoned the backlog (memory bounded) and extended the sync target to the latest
+    // tip so L2 sync re-drives the whole range authoritatively.
+    assert!(l1_events_provider.catchupper.commit_block_backlog.is_empty());
+    assert_eq!(l1_events_provider.catchupper.target_height(), BlockNumber(5));
+}
+
+// Once overflowed, no further tip commit is buffered: memory stays bounded at zero however far the
+// tip races ahead, and the sync target keeps following the latest committed height.
+#[test]
+fn commits_after_overflow_stay_bounded_and_track_tip() {
+    const CAP: usize = 3;
+    let mut l1_events_provider = provider_catching_up_with_backlog_cap(CAP);
+
+    // Heights 1..=3 fill the backlog to the cap; 4..=8 all overflow it.
+    for height in (1..=8).map(BlockNumber) {
+        commit_block_no_rejected(&mut l1_events_provider, &[], height);
+    }
+
+    assert!(l1_events_provider.catchupper.commit_block_backlog.is_empty());
+    assert_eq!(l1_events_provider.catchupper.target_height(), BlockNumber(8));
+}
+
+// The recovery is genuinely recoverable: after an overflow abandons the backlog, L2 sync re-driving
+// the range (each height arrives at `current_height`, the `Equal` path) completes catch-up and
+// transitions the provider to `Pending`, with the backlog drained empty.
+#[test]
+fn catch_up_completes_after_overflow_via_sync() {
+    const CAP: usize = 3;
+    let mut l1_events_provider = provider_catching_up_with_backlog_cap(CAP);
+
+    // Fill to the cap and overflow, abandoning the backlog. The sync target is now 4.
+    for height in (1..=4).map(BlockNumber) {
+        commit_block_no_rejected(&mut l1_events_provider, &[], height);
+    }
+    assert!(l1_events_provider.catchupper.commit_block_backlog.is_empty());
+
+    // L2 sync re-drives the range: heights 0..=4 arrive as `Equal` commits and are applied, taking
+    // the current height to 5 (> target 4) and completing catch-up.
+    for height in (0..=4).map(BlockNumber) {
+        commit_block_no_rejected(&mut l1_events_provider, &[], height);
+    }
+
+    assert_eq!(l1_events_provider.state, ProviderState::Pending);
+    assert!(l1_events_provider.catchupper.commit_block_backlog.is_empty());
+}
+
+// A non-sequential `Greater` commit (a gap, not a cap overflow) hits the same recovery path: it
+// would previously trip the "Heights should be sequential." assert, and must instead abandon the
+// backlog and defer to sync rather than panic.
+#[test]
+fn non_sequential_backlog_commit_abandons_instead_of_panicking() {
+    // Cap well above what we push, so the cap is not the trigger -- the gap is.
+    const CAP: usize = 100;
+    let mut l1_events_provider = provider_catching_up_with_backlog_cap(CAP);
+
+    // Two sequential `Greater` commits build a gapless backlog [1, 2].
+    for height in [BlockNumber(1), BlockNumber(2)] {
+        commit_block_no_rejected(&mut l1_events_provider, &[], height);
+    }
+    assert_eq!(l1_events_provider.catchupper.commit_block_backlog.len(), 2);
+
+    // A non-sequential commit (expected 3, got 5) must be absorbed gracefully, not panic.
+    let result = l1_events_provider.commit_block([].into(), [].into(), BlockNumber(5));
+    assert_matches!(result, Ok(()));
+    assert!(l1_events_provider.catchupper.commit_block_backlog.is_empty());
+    assert_eq!(l1_events_provider.catchupper.target_height(), BlockNumber(5));
+}
+
+#[tokio::test]
+async fn backlog_len_metric_tracks_push_and_drain() {
+    let recorder = PrometheusBuilder::new().build_recorder();
+    let _recorder_guard = metrics::set_default_local_recorder(&recorder);
+
+    // Start catching up with current height 0 and a target one above it, so a single `Equal`
+    // commit (height 1) completes catch-up and drains the backlog.
+    const TARGET_HEIGHT: BlockNumber = BlockNumber(0);
+    let mut catchupper = make_catchupper!(backlog: []);
+    catchupper.target_height = Arc::new(AtomicU64::new(TARGET_HEIGHT.0));
+    let mut l1_events_provider = L1EventsProviderContentBuilder::new()
+        .with_catchupper(catchupper)
+        .with_height(BlockNumber(0))
+        .with_state(ProviderState::CatchingUp)
+        .build_into_l1_provider();
+    // Registers the gauge so it is rendered even before its first `set`.
+    register_provider_metrics();
+
+    // Two `Greater` commits (heights 1, 2) are backlogged; the gauge tracks the backlog length.
+    // They start sequentially one above the current height (0), as the drain-time invariant
+    // requires.
+    commit_block_no_rejected(&mut l1_events_provider, &[], BlockNumber(1));
+    commit_block_no_rejected(&mut l1_events_provider, &[], BlockNumber(2));
+    let metrics = recorder.handle().render();
+    assert_eq!(
+        L1_MESSAGE_PROVIDER_COMMIT_BLOCK_BACKLOG_LEN.parse_numeric_metric::<usize>(&metrics),
+        Some(2)
+    );
+
+    // The `Equal` commit at height 0 completes catch-up (current height becomes 1 > target 0),
+    // drains the backlog [1, 2], and resets the gauge to 0.
+    commit_block_no_rejected(&mut l1_events_provider, &[], BlockNumber(0));
+    assert_eq!(l1_events_provider.state, ProviderState::Pending);
+    let metrics = recorder.handle().render();
+    assert_eq!(
+        L1_MESSAGE_PROVIDER_COMMIT_BLOCK_BACKLOG_LEN.parse_numeric_metric::<usize>(&metrics),
+        Some(0)
+    );
+}
+
 #[test]
 fn commit_block_before_add_tx_stores_tx_in_committed() {
     // Setup
```

### crates/apollo_l1_events/src/metrics.rs
```diff
@@ -20,6 +20,7 @@ define_metrics!(
         MetricGauge { L1_MESSAGE_SCRAPER_LAST_SUCCESS_TIMESTAMP_SECONDS, "l1_message_scraper_last_success_timestamp_seconds", "Unix timestamp (seconds) of the last successful L1 message scrape" },
         MetricGauge { L1_MESSAGE_PROVIDER_NUM_PENDING_TXS, "l1_message_provider_num_pending_txs", "The number of pending L1 handler transactions in the transaction manager" },
         MetricGauge { L1_MESSAGE_PROVIDER_OLDEST_PENDING_TX_L1_TIMESTAMP_SECONDS, "l1_message_provider_oldest_pending_tx_l1_timestamp_seconds", "The L1 block timestamp (unix seconds) of the oldest pending (uncommitted) L1 handler transaction; 0 when none are pending" },
+        MetricGauge { L1_MESSAGE_PROVIDER_COMMIT_BLOCK_BACKLOG_LEN, "l1_message_provider_commit_block_backlog_len", "The number of commit-blocks buffered in the catch-up backlog while the provider syncs to the target height; abnormal sustained growth indicates a stalled or lagging L2 sync" },
     },
 );
 
@@ -35,4 +36,5 @@ pub(crate) fn register_scraper_metrics() {
 pub(crate) fn register_provider_metrics() {
     L1_MESSAGE_PROVIDER_NUM_PENDING_TXS.register();
     L1_MESSAGE_PROVIDER_OLDEST_PENDING_TX_L1_TIMESTAMP_SECONDS.register();
+    L1_MESSAGE_PROVIDER_COMMIT_BLOCK_BACKLOG_LEN.register();
 }
```

### crates/apollo_l1_events/src/test_utils.rs
```diff
@@ -36,7 +36,10 @@ use crate::transaction_record::{TransactionPayload, TransactionRecord};
 use crate::L1EventsProviderConfig;
 
 macro_rules! make_catchupper {
-    (backlog: [$($height:literal => [$($tx:literal),* $(,)*]),* $(,)*]) => {{
+    (backlog: [$($height:literal => [$($tx:literal),* $(,)*]),* $(,)*]) => {
+        make_catchupper!(backlog: [$($height => [$($tx),*]),*], max: usize::MAX)
+    };
+    (backlog: [$($height:literal => [$($tx:literal),* $(,)*]),* $(,)*], max: $max:expr) => {{
         Catchupper {
             commit_block_backlog: vec![
                 $(CommitBlockBacklog {
@@ -49,7 +52,9 @@ macro_rules! make_catchupper {
             sync_client: Arc::new(MockStateSyncClient::default()),
             sync_task_handle: SyncTaskHandle::default(),
             n_sync_health_check_failures: Default::default(),
-            sync_retry_interval: Duration::from_millis(10)
+            sync_retry_interval: Duration::from_millis(10),
+            max_commit_block_backlog_len: $max,
+            backlog_overflowed: false
         }
     }};
 }
```

### crates/apollo_l1_events_config/src/config.rs
```diff
@@ -21,6 +21,11 @@ pub struct L1EventsProviderConfig {
     pub l1_handler_proposal_cooldown_seconds: Duration,
     /// When true, the L1 provider operates in dummy mode.
     pub dummy_mode: bool,
+    /// Maximum number of commit-blocks buffered in the catch-up backlog while the provider syncs
+    /// to the target height. Bounds memory growth when L2 sync stalls or lags during startup
+    /// catch-up. Hitting it is a hard error rather than a silent drop, because the backlog
+    /// must remain a gapless, strictly-sequential run of heights.
+    pub max_commit_block_backlog_len: usize,
 }
 
 impl Default for L1EventsProviderConfig {
@@ -31,6 +36,9 @@ impl Default for L1EventsProviderConfig {
             l1_handler_consumption_timelock_seconds: Duration::from_secs(5 * 60),
             l1_handler_proposal_cooldown_seconds: Duration::from_secs(70),
             dummy_mode: false,
+            // ~1M entries is only ~tens of MB, comfortably covering any legitimate startup sync gap
+            // while still bounding worst-case memory.
+            max_commit_block_backlog_len: 1_000_000,
         }
     }
 }
@@ -72,6 +80,14 @@ impl SerializeConfig for L1EventsProviderConfig {
                  trivial truthy responses without connecting to actual L1.",
                 ParamPrivacyInput::Public,
             ),
+            ser_param(
+                "max_commit_block_backlog_len",
+                &self.max_commit_block_backlog_len,
+                "Maximum number of commit-blocks buffered in the catch-up backlog during startup \
+                 sync before commit_block fails; guards against unbounded memory growth on a \
+                 stalled or lagging L2 sync.",
+                ParamPrivacyInput::Public,
+            ),
         ])
     }
 }
```

### crates/apollo_node/resources/config_schema.json
```diff
@@ -3284,6 +3284,11 @@
     "privacy": "Public",
     "value": 70
   },
+  "l1_events_provider_config.max_commit_block_backlog_len": {
+    "description": "Maximum number of commit-blocks buffered in the catch-up backlog during startup sync before commit_block fails; guards against unbounded memory growth on a stalled or lagging L2 sync.",
+    "privacy": "Public",
+    "value": 1000000
+  },
   "l1_events_provider_config.startup_sync_sleep_retry_interval_seconds": {
     "description": "Interval in seconds between each retry of syncing with L2 during startup.",
     "privacy": "Public",
```
