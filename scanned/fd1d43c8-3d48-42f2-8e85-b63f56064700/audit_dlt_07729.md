# [?] fix(chain-state): avoid state overlay cache deadlock (#24875)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-06-09
Source: https://github.com/paradigmxyz/reth/commit/84d8e471ea51896eb4c83e4f0b2ec95cefb1f30d
Type: security-commit

## Details
fix(chain-state): avoid state overlay cache deadlock (#24875)

Co-authored-by: Brian <brian@Brians-MacBook-Pro.local>
Co-authored-by: Brian <brian@Host-007.homenet.telecomitalia.it>

## Patch
### crates/chain-state/src/state_trie_overlay.rs
```diff
@@ -17,7 +17,11 @@ use reth_primitives_traits::{
 #[cfg(feature = "rayon")]
 use reth_tasks::WorkerPool;
 use reth_trie::{updates::TrieUpdatesSorted, HashedPostStateSorted, TrieInputSorted};
-use std::{fmt, sync::Arc, time::Instant};
+use std::{
+    fmt,
+    sync::{Arc, OnceLock},
+    time::Instant,
+};
 use tracing::{debug, trace};
 
 /// Manages flattened state trie overlays for in-memory blocks.
@@ -27,7 +31,7 @@ use tracing::{debug, trace};
 #[derive(Clone)]
 pub struct StateTrieOverlayManager<N: NodePrimitives = EthPrimitives> {
     blocks: Arc<DashMap<B256, ExecutedBlock<N>>>,
-    overlays: Arc<DashMap<OverlayCacheKey, Arc<TrieInputSorted>>>,
+    overlays: Arc<DashMap<OverlayCacheKey, OverlayCacheEntry>>,
     #[cfg(feature = "rayon")]
     worker_pool: Option<Arc<WorkerPool>>,
     metrics: StateTrieOverlayMetrics,
@@ -118,7 +122,7 @@ impl<N: NodePrimitives> StateTrieOverlayManager<N> {
             .iter()
             .filter_map(|entry| {
                 let key = *entry.key();
-                (key.tip_hash == parent_hash).then_some(key.anchor_hash)
+                (key.tip_hash == parent_hash && entry.value().is_ready()).then_some(key.anchor_hash)
             })
             .collect::<Vec<_>>();
 
@@ -155,7 +159,7 @@ impl<N: NodePrimitives> StateTrieOverlayManager<N> {
                         anchor_hash = %anchor_hash,
                     )
                     .entered();
-                    let _ = manager.get_overlay(hash, anchor_hash);
+                    let _ = manager.precompute_overlay(hash, anchor_hash);
                 });
             }
         }
@@ -229,6 +233,16 @@ impl<N: NodePrimitives> StateTrieOverlayManager<N> {
         Ok((Arc::clone(&input.nodes), Arc::clone(&input.state)))
     }
 
+    #[cfg(feature = "rayon")]
+    fn precompute_overlay(
+        &self,
+        tip_hash: B256,
+        anchor_hash: B256,
+    ) -> Result<(), StateTrieOverlayError> {
+        let _ = self.get_overlay_inner(tip_hash, anchor_hash, OverlayLookupMode::Precompute)?;
+        Ok(())
+    }
+
     #[tracing::instrument(
         level = "trace",
         target = "chain_state::state_trie_overlay",
@@ -246,13 +260,36 @@ impl<N: NodePrimitives> StateTrieOverlayManager<N> {
         tip_hash: B256,
         anchor_hash: B256,
     ) -> Result<Arc<TrieInputSorted>, StateTrieOverlayError> {
+        self.get_overlay_inner(tip_hash, anchor_hash, OverlayLookupMode::Required)
+            .map(|input| input.expect("required overlay lookups always return an overlay"))
+    }
+
+    fn get_overlay_inner(
+        &self,
+        tip_hash: B256,
+        anchor_hash: B256,
+        mode: OverlayLookupMode,
+    ) -> Result<Option<Arc<TrieInputSorted>>, StateTrieOverlayError> {
         let key = OverlayCacheKey { anchor_hash, tip_hash };
         let span = tracing::Span::current();
 
-        if let Some(input) = self.overlays.get(&key).map(|entry| Arc::clone(entry.value())) {
-            self.metrics.overlay_cache_reuses.increment(1);
-            span.record("cache_reused", true);
-            return Ok(input)
+        if let Some(entry) = self.overlays.get(&key).map(|entry| entry.value().clone()) {
+            return Ok(match entry {
+                OverlayCacheEntry::Ready(input) => {
+                    self.metrics.overlay_cache_reuses.increment(1);
+                    span.record("cache_reused", true);
+                    Some(input)
+                }
+                OverlayCacheEntry::Computing(waiter) => {
+                    span.record("cache_reused", true);
+                    if mode == OverlayLookupMode::Precompute {
+                        None
+                    } else {
+                        self.metrics.overlay_cache_reuses.increment(1);
+                        Some(waiter.wait())
+                    }
+                }
+            })
         }
         span.record("cache_reused", false);
 
@@ -277,7 +314,7 @@ impl<N: NodePrimitives> StateTrieOverlayManager<N> {
                 .then(|| {
                     self.overlays
                         .get(&OverlayCacheKey { anchor_hash, tip_hash: parent_hash })
-                        .map(|entry| Arc::clone(entry.value()))
+                        .and_then(|entry| entry.value().ready())
                 })
                 .flatten()
         });
@@ -289,42 +326,61 @@ impl<N: NodePrimitives> StateTrieOverlayManager<N> {
             None => ComputeOverlayInput::MergeBlocks(blocks),
         };
 
-        // The vacant entry is the cache-fill gate: racing callers block instead of recomputing.
-        let input = match self.overlays.entry(key) {
-            Entry::Occupied(entry) => {
-                self.metrics.overlay_cache_reuses.increment(1);
-                span.record("cache_reused", true);
-                return Ok(Arc::clone(entry.get()))
-            }
+        enum CacheAction {
+            Ready(Arc<TrieInputSorted>),
+            Wait(Arc<OverlayWaiter>),
+            Compute(Arc<OverlayWaiter>),
+            Skip,
+        }
+
+        let action = match self.overlays.entry(key) {
+            Entry::Occupied(entry) => match entry.get().clone() {
+                OverlayCacheEntry::Ready(input) => {
+                    self.metrics.overlay_cache_reuses.increment(1);
+                    span.record("cache_reused", true);
+                    CacheAction::Ready(input)
+                }
+                OverlayCacheEntry::Computing(waiter) => {
+                    span.record("cache_reused", true);
+                    if mode == OverlayLookupMode::Precompute {
+                        CacheAction::Skip
+                    } else {
+                        self.metrics.overlay_cache_reuses.increment(1);
+                        CacheAction::Wait(waiter)
+                    }
+                }
+            },
             Entry::Vacant(entry) => {
                 self.metrics.overlay_cache_fills.increment(1);
-                let input = {
-                    #[cfg(feature = "rayon")]
-                    {
-                        if let Some(worker_pool) = &self.worker_pool {
-                            let compute_span = span;
-                            let metrics = self.metrics.clone();
-                            Arc::new(worker_pool.install_fn(move || {
-                                let _guard = compute_span.enter();
-                                compute_overlay(compute_input, anchor_hash, &metrics)
-                            }))
-                        } else {
-                            Arc::new(compute_overlay(compute_input, anchor_hash, &self.metrics))
-                        }
-                    }
+                let waiter = Arc::new(OverlayWaiter::new());
+                entry.insert(OverlayCacheEntry::Computing(Arc::clone(&waiter)));
+                CacheAction::Compute(waiter)
+            }
+        };
 
-                    #[cfg(not(feature = "rayon"))]
-                    {
-                        Arc::new(compute_overlay(compute_input, anchor_hash, &self.metrics))
+        match action {
+            CacheAction::Ready(input) => Ok(Some(input)),
+            CacheAction::Wait(waiter) => Ok(Some(waiter.wait())),
+            CacheAction::Skip => Ok(None),
+            CacheAction::Compute(waiter) => {
+                let input = self.compute_overlay(compute_input, anchor_hash, span);
+                waiter.finish(Arc::clone(&input));
+
+                if let Entry::Occupied(mut entry) = self.overlays.entry(key) {
+                    // The entry may have been pruned while the overlay was computing. Only cache
+                    // the result if the map still points at the waiter installed by this task.
+                    let should_publish = match entry.get() {
+                        OverlayCacheEntry::Computing(existing) => Arc::ptr_eq(existing, &waiter),
+                        OverlayCacheEntry::Ready(_) => false,
+                    };
+                    if should_publish {
+                        entry.insert(OverlayCacheEntry::Ready(Arc::clone(&input)));
                     }
-                };
+                }
 
-                entry.insert(Arc::clone(&input));
-                input
+                Ok(Some(input))
             }
-        };
-
-        Ok(input)
+        }
     }
 
     /// Returns `preferred_anchor` if it is on the parent chain, otherwise the first missing parent.
@@ -357,6 +413,27 @@ impl<N: NodePrimitives> StateTrieOverlayManager<N> {
             hash = block_parent_hash;
         }
     }
+
+    fn compute_overlay(
+        &self,
+        compute_input: ComputeOverlayInput<N>,
+        anchor_hash: B256,
+        _span: tracing::Span,
+    ) -> Arc<TrieInputSorted> {
+        #[cfg(feature = "rayon")]
+        {
+            if let Some(worker_pool) = &self.worker_pool {
+                let compute_span = _span;
+                let metrics = self.metrics.clone();
+                return Arc::new(worker_pool.install_fn(move || {
+                    let _guard = compute_span.enter();
+                    compute_overlay(compute_input, anchor_hash, &metrics)
+                }))
+            }
+        }
+
+        Arc::new(compute_overlay(compute_input, anchor_hash, &self.metrics))
+    }
 }
 
 /// Error returned when a state trie overlay cannot be built from the manager's current block set.
@@ -386,6 +463,49 @@ struct OverlayCacheKey {
     tip_hash: B256,
 }
 
+#[derive(Clone)]
+enum OverlayCacheEntry {
+    Ready(Arc<TrieInputSorted>),
+    Computing(Arc<OverlayWaiter>),
+}
+
+impl OverlayCacheEntry {
+    const fn is_ready(&self) -> bool {
+        matches!(self, Self::Ready(_))
+    }
+
+    fn ready(&self) -> Option<Arc<TrieInputSorted>> {
+        match self {
+            Self::Ready(input) => Some(Arc::clone(input)),
+            Self::Computing(_) => None,
+        }
+    }
+}
+
+#[derive(Clone, Copy, Debug, Eq, PartialEq)]
+enum OverlayLookupMode {
+    Required,
+    Precompute,
+}
+
+struct OverlayWaiter {
+    input: OnceLock<Arc<TrieInputSorted>>,
+}
+
+impl OverlayWaiter {
+    const fn new() -> Self {
+        Self { input: OnceLock::new() }
+    }
+
+    fn wait(&self) -> Arc<TrieInputSorted> {
+        Arc::clone(self.input.wait())
+    }
+
+    fn finish(&self, computed: Arc<TrieInputSorted>) {
+        let _ = self.input.set(computed);
+    }
+}
+
 enum ComputeOverlayInput<N: NodePrimitives> {
     ExtendCached { block: ExecutedBlock<N>, parent_input: Arc<TrieInputSorted> },
     MergeBlocks(Vec<ExecutedBlock<N>>),
@@ -516,11 +636,12 @@ mod tests {
     use alloy_primitives::U256;
     use reth_primitives_traits::Account;
     use reth_trie::{updates::TrieUpdatesSorted, HashedPostState, HashedStorage};
-    use std::sync::Arc;
     #[cfg(feature = "rayon")]
+    use std::time::Instant;
     use std::{
+        sync::{mpsc, Arc},
         thread,
-        time::{Duration, Instant},
+        time::Duration,
     };
 
     fn with_unique_state(
@@ -625,6 +746,55 @@ mod tests {
         );
     }
 
+    #[test]
+    fn required_lookup_waits_for_in_progress_overlay() {
+        let manager = StateTrieOverlayManager::<EthPrimitives>::default();
+        let key = OverlayCacheKey {
+            anchor_hash: B256::with_last_byte(1),
+            tip_hash: B256::with_last_byte(2),
+        };
+        let waiter = Arc::new(OverlayWaiter::new());
+        manager.overlays.insert(key, OverlayCacheEntry::Computing(Arc::clone(&waiter)));
+
+        let (tx, rx) = mpsc::channel();
+        thread::spawn(move || {
+            let res =
+                manager.overlay_for_parent(key.tip_hash, key.anchor_hash).map(|(_, state)| state);
+            tx.send(res).unwrap();
+        });
+
+        assert!(matches!(
+            rx.recv_timeout(Duration::from_millis(50)),
+            Err(mpsc::RecvTimeoutError::Timeout)
+        ));
+
+        waiter.finish(Arc::new(TrieInputSorted::default()));
+
+        let state = rx.recv_timeout(Duration::from_secs(1)).unwrap().unwrap();
+        assert!(state.is_empty());
+    }
+
+    #[cfg(feature = "rayon")]
+    #[test]
+    fn precompute_skips_in_progress_overlay() {
+        let manager = StateTrieOverlayManager::<EthPrimitives>::new(Arc::new(WorkerPool::new(
+            1,
+            "test-ovly",
+        )));
+        let key = OverlayCacheKey {
+            anchor_hash: B256::with_last_byte(1),
+            tip_hash: B256::with_last_byte(2),
+        };
+        manager.overlays.insert(key, OverlayCacheEntry::Computing(Arc::new(OverlayWaiter::new())));
+
+        let (tx, rx) = mpsc::channel();
+        thread::spawn(move || {
+            tx.send(manager.precompute_overlay(key.tip_hash, key.anchor_hash)).unwrap();
+        });
+
+        rx.recv_timeout(Duration::from_secs(1)).unwrap().unwrap();
+    }
+
     #[cfg(feature = "rayon")]
     #[test]
     fn insert_block_prepares_child_overlay_from_cached_parent() {
```
