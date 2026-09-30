# [?] [consensus] Clear module cache on pipeline teardown to prevent hot-state deadlock

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-03-16
Source: https://github.com/aptos-labs/aptos-core/commit/f064f03a4312cfae80d6e3647cd40714acb003d7
Type: security-commit

## Details
[consensus] Clear module cache on pipeline teardown to prevent hot-state deadlock

The `PipelineBuilder` holds a `module_cache` containing a
`CachedModuleView<CachedStateView>`, where the inner `CachedStateView`
keeps an `Arc<dyn HotStateView>` alive. When the consensus observer
aborts its pipeline (e.g. on epoch transition or fallback to state
sync), spawned tasks are correctly cancelled but the `PipelineBuilder`
itself — and its `module_cache` — remains alive until a new pipeline is
created (at the start of the next epoch).

This creates a circular deadlock:

- The stale `HotStateView` in `module_cache` keeps the `Weak` ref in
  `old_views` alive (`strong_count > 0`), blocking `try_merge`.
- `try_merge` being blocked stalls the hot-state commit thread, filling
  up the commit channel (backlog = 10).
- The full channel blocks `state_batch_committer`, which blocks
  `StateSnapshotCommitter`, which blocks `BufferedState::enqueue_commit`.
- State-sync threads can no longer commit checkpoints, so state sync
  stalls.
- The new `PipelineBuilder` (which would replace the old one and drop
  the stale cache) is only created **after** state sync completes and a
  new epoch starts — deadlock.

Fix: call `clear_module_cache()` in `clear_pending_block_state()`, the
common teardown path used by fallback entry, subscription failure, and
post-sync reset. This drops the stale `CachedStateView` and its
`HotStateView` reference immediately, allowing `try_merge` to proceed.

As an extra safety net, the hot-state committer now force-clears
`old_views` after 5 seconds of blocked merge, logging an error so
the root cause is still surfaced.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### consensus/src/consensus_observer/observer/consensus_observer.rs
```diff
@@ -229,6 +229,11 @@ impl ConsensusObserver {
             );
         }
 
+        // Clear the pipeline builder's module cache so that the stale CachedStateView is released.
+        if let Some(ref builder) = self.pipeline_builder {
+            builder.clear_module_cache();
+        }
+
         // Increment the cleared block state counter
         metrics::increment_counter_without_labels(&metrics::OBSERVER_CLEARED_BLOCK_STATE);
     }
```

### consensus/src/pipeline/pipeline_builder.rs
```diff
@@ -293,6 +293,12 @@ impl PipelineBuilder {
         self.pre_commit_status.clone()
     }
 
+    /// Drops the cached module view and releases the state view inside it. Must be called when the
+    /// pipeline is being torn down.
+    pub fn clear_module_cache(&self) {
+        *self.module_cache.lock() = None;
+    }
+
     fn channel(abort_handles: &mut Vec<AbortHandle>) -> (PipelineInputTx, PipelineInputRx) {
         let (qc_tx, qc_rx) = oneshot::channel();
         let (rand_tx, rand_rx) = oneshot::channel();
```

### storage/aptosdb/src/state_store/hot_state.rs
```diff
@@ -29,11 +29,12 @@ use std::{
         mpsc::{Receiver, RecvTimeoutError, Sender, SyncSender},
         Arc, Weak,
     },
-    time::Duration,
+    time::{Duration, Instant},
 };
 
 const MAX_HOT_STATE_COMMIT_BACKLOG: usize = 10;
 const DEFERRED_MERGE_RETRY_INTERVAL: Duration = Duration::from_millis(10);
+const FORCE_MERGE_TIMEOUT: Duration = Duration::from_secs(5);
 
 #[derive(Debug)]
 struct Shard<K, V>
@@ -342,9 +343,24 @@ impl Committer {
             // If merged_state is too old for to_commit (persisted snapshot advanced
             // while merge was deferred), wait for old views to drain so try_merge
             // can advance merged_state.
+            let wait_start = Instant::now();
             while !self.merged_state.can_be_delta_base_of(&to_commit) {
                 if !self.try_merge() {
                     std::thread::sleep(DEFERRED_MERGE_RETRY_INTERVAL);
+                    if wait_start.elapsed() >= FORCE_MERGE_TIMEOUT {
+                        error!(
+                            wait_secs = wait_start.elapsed().as_secs(),
+                            old_views = self.old_views.len(),
+                            merged_version = self.merged_state.next_version(),
+                            commit_version = to_commit.next_version(),
+                            "Hot-state merge blocked too long, force-clearing old views.",
+                        );
+                        // NOTE: this means that we force the base DashMaps to advance and the
+                        // lingering old readers might get inconsistent data from now on, but we
+                        // have to move on to prevent the backpressure from building up.
+                        self.old_views.clear();
+                        COUNTER.inc_with(&["hot_state_force_merge_clear"]);
+                    }
                 }
             }
 
```
