# [?] [Storage] Fix HotState crash on stale merged_state

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-02-20
Source: https://github.com/aptos-labs/aptos-core/commit/eb4770408398ee63af674ff51e935a30a3880c7a
Type: security-commit

## Details
[Storage] Fix HotState crash on stale merged_state

The `Committer` thread could panic at `layer.rs:123` (`base_layer.inner.layer >= self.inner.base_layer`)
when building a delta between `merged_state` and an incoming `to_commit` state.

**Root cause**: `State::update()` spawns new `MapLayer` shards with
`base_layer = persisted_snapshot.shard.layer()`. When old
`LayeredHotStateView` readers prevent `try_merge()` from advancing
`merged_state`, the committer's `merged_state` falls behind
`persisted_snapshot`. Subsequent `to_commit.make_delta(&merged_state)` then
violates the layer compatibility invariant.

**Fix**: Before building the delta, spin-wait for old views to drain so
`try_merge()` can advance `merged_state` to a compatible layer. One successful
merge is always sufficient since `persisted.layer <= previous_committed.layer`.

- Add `MapLayer::can_view_after()` — non-panicking compatibility check
- Add `State::can_be_delta_base_of()` — checks all 16 shards
- `Committer::try_merge()` now returns `bool` (`false` = blocked by old views)
- `Committer::run()` waits for merge before `make_delta` when incompatible

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

## Patch
### experimental/storage/layered-map/src/layer.rs
```diff
@@ -118,18 +118,24 @@ impl<K: ArcAsyncDrop, V: ArcAsyncDrop> MapLayer<K, V> {
         self.inner.parent.upgrade().map(Self::new)
     }
 
-    pub fn into_layers_view_after(self, base_layer: MapLayer<K, V>) -> LayeredMap<K, V> {
-        assert!(base_layer.is_family(&self));
-        assert!(base_layer.inner.layer >= self.inner.base_layer);
-        assert!(base_layer.inner.layer <= self.inner.layer);
+    pub fn into_layers_view_after(self, base_layer: Self) -> LayeredMap<K, V> {
+        assert!(
+            self.can_view_after(&base_layer),
+            "incompatible layers: base(family={}, layer={}) top(family={}, layer={}, base_layer={})",
+            base_layer.inner.family,
+            base_layer.inner.layer,
+            self.inner.family,
+            self.inner.layer,
+            self.inner.base_layer,
+        );
 
         self.log_layer("view");
         base_layer.log_layer("as_view_base");
 
         LayeredMap::new(base_layer, self)
     }
 
-    pub fn view_layers_after(&self, base_layer: &MapLayer<K, V>) -> LayeredMap<K, V> {
+    pub fn view_layers_after(&self, base_layer: &Self) -> LayeredMap<K, V> {
         self.clone().into_layers_view_after(base_layer.clone())
     }
 
@@ -145,6 +151,13 @@ impl<K: ArcAsyncDrop, V: ArcAsyncDrop> MapLayer<K, V> {
         Arc::ptr_eq(&self.inner, &other.inner)
     }
 
+    /// Returns true if `base` can be used as the base layer for viewing layers up to `self`.
+    pub fn can_view_after(&self, base: &Self) -> bool {
+        self.is_family(base)
+            && base.inner.layer >= self.inner.base_layer
+            && base.inner.layer <= self.inner.layer
+    }
+
     pub fn is_descendant_of(&self, other: &Self) -> bool {
         if !self.is_family(other) {
             return false;
```

### experimental/storage/layered-map/src/tests.rs
```diff
@@ -132,6 +132,56 @@ fn test_is_descendant_of() {
     assert!(!other_root.is_descendant_of(&child1));
 }
 
+#[test]
+fn test_can_view_after() {
+    //  Build a chain with an advancing base:
+    //
+    //       root (layer 0)
+    //        |
+    //      child1 (layer 1, base_layer=0)  -- spawned from LayeredMap(root, root)
+    //        |
+    //      child2 (layer 2, base_layer=0)  -- spawned from LayeredMap(root, child1)
+    //        |
+    //      child3 (layer 3, base_layer=1)  -- spawned from LayeredMap(child1, child2)
+    //        |
+    //      child4 (layer 4, base_layer=2)  -- spawned from LayeredMap(child2, child3)
+    //
+    let root = MapLayer::<u8, u8>::new_family("test");
+    let child1 = root.view_layers_after(&root).new_layer(&[(1, 10)]);
+    let child2 = child1.view_layers_after(&root).new_layer(&[(2, 20)]);
+    let child3 = child2.view_layers_after(&child1).new_layer(&[(3, 30)]);
+    let child4 = child3.view_layers_after(&child2).new_layer(&[(4, 40)]);
+
+    // A layer can always be viewed after itself.
+    assert!(root.can_view_after(&root));
+    assert!(child3.can_view_after(&child3));
+
+    // child1 and child2 have base_layer=0, so root (layer 0) is a valid base.
+    assert!(child1.can_view_after(&root));
+    assert!(child2.can_view_after(&root));
+
+    // child3 has base_layer=1, so child1 (layer 1) is the earliest valid base.
+    assert!(child3.can_view_after(&child1));
+    assert!(child3.can_view_after(&child2));
+    // root (layer 0) is too old for child3.
+    assert!(!child3.can_view_after(&root));
+
+    // child4 has base_layer=2, so child2 (layer 2) is the earliest valid base.
+    assert!(child4.can_view_after(&child2));
+    assert!(child4.can_view_after(&child3));
+    assert!(!child4.can_view_after(&root));
+    assert!(!child4.can_view_after(&child1));
+
+    // A base cannot be newer than the top layer.
+    assert!(!root.can_view_after(&child1));
+    assert!(!child1.can_view_after(&child2));
+
+    // Different family is always invalid.
+    let other = MapLayer::<u8, u8>::new_family("other");
+    assert!(!child1.can_view_after(&other));
+    assert!(!other.can_view_after(&child1));
+}
+
 proptest! {
     #[test]
     fn test_layered_map_get(
```

### storage/aptosdb/src/state_store/hot_state.rs
```diff
@@ -334,6 +334,15 @@ impl Committer {
                 continue;
             }
 
+            // If merged_state is too old for to_commit (persisted snapshot advanced
+            // while merge was deferred), wait for old views to drain so try_merge
+            // can advance merged_state.
+            while !self.merged_state.can_be_delta_base_of(&to_commit) {
+                if !self.try_merge() {
+                    std::thread::sleep(DEFERRED_MERGE_RETRY_INTERVAL);
+                }
+            }
+
             let committed_version = to_commit.next_version();
 
             // Build a layered view: delta(merged_state -> to_commit) over base DashMaps.
@@ -398,7 +407,9 @@ impl Committer {
                     );
                     self.handle_reset(state, ack);
                 },
-                Err(RecvTimeoutError::Timeout) => self.try_merge(),
+                Err(RecvTimeoutError::Timeout) => {
+                    self.try_merge();
+                },
                 Err(RecvTimeoutError::Disconnected) => return None,
             }
         };
@@ -441,15 +452,16 @@ impl Committer {
     /// a clean (no-delta) view. Readers who already cloned the old delta-bearing view are
     /// unaffected: the delta shadows changed keys, and unchanged keys agree between the delta's
     /// target and the updated DashMaps.
-    fn try_merge(&mut self) {
+    /// Returns `false` if blocked by lingering old views, `true` otherwise.
+    fn try_merge(&mut self) -> bool {
         self.old_views.retain(|v| v.strong_count() > 0);
         if !self.old_views.is_empty() {
-            return;
+            return false;
         }
 
         let target = self.committed.lock().state.clone();
         if self.merged_state.is_the_same(&target) {
-            return;
+            return true;
         }
 
         self.apply_delta_to_base(&target);
@@ -468,6 +480,7 @@ impl Committer {
             base: Arc::clone(&self.base),
         });
         Self::swap_view(&mut self.old_views, &mut self.committed.lock(), clean_view);
+        true
     }
 
     /// Apply the delta between `merged_state` and `target` to the base DashMaps.
@@ -861,6 +874,55 @@ mod tests {
         assert_eq!(hot_state.merged_version.load(Ordering::Acquire), 2);
     }
 
+    /// Regression test: the committer must not crash when `merged_state` lags behind
+    /// the `base_layer` of an incoming `to_commit`.
+    ///
+    /// In production, `State::update()` spawns new `MapLayer` shards with
+    /// `base_layer = persisted_snapshot.layer()`. When old readers prevent
+    /// `try_merge()` from advancing `merged_state`, and `persisted_snapshot`
+    /// has advanced, the committer's `merged_state` can be at a lower layer than
+    /// `to_commit.base_layer`. The fix makes the committer wait for merge before
+    /// building the delta.
+    ///
+    /// Timeline:
+    /// ```text
+    ///   r0 holds V0_clean ──► blocks all merges (merged_state stuck at S0)
+    ///   S1 committed (base_layer=0) ──► delta(S0→S1) OK
+    ///   S2 committed (base_layer=1) ──► delta(S0→S2) would crash without fix
+    ///   drop(r0) ──► merge to S1 proceeds, then delta(S1→S2) OK
+    /// ```
+    #[test]
+    fn test_commit_with_advanced_base_layer() {
+        let state0 = State::new_empty(TEST_CONFIG);
+        let hot_state = HotState::new(state0.clone(), TEST_CONFIG);
+
+        // Hold a view to block all merges (merged_state stays at S0).
+        let (held_view, _) = hot_state.get_committed();
+
+        // S1: spawned with root=S0, so base_layer = S0.layer = 0.
+        // Compatible with merged_state at S0.
+        let state1 = build_empty_descendant(&state0, &state0, 0);
+        hot_state.enqueue_commit(state1.clone());
+        wait_for_committed_version(&hot_state, 1);
+
+        // S2: spawned with root=S1, simulating persisted_snapshot advancing to S1.
+        // This gives base_layer = S1.layer = 1, incompatible with merged_state
+        // still at S0 (layer 0). Without the fix this panics.
+        let state2 = build_empty_descendant(&state1, &state1, 1);
+        hot_state.enqueue_commit(state2);
+
+        // Give the committer time to pick up S2 and hit the incompatible
+        // merged_state. Without the fix, this would panic.
+        std::thread::sleep(Duration::from_millis(100));
+
+        // Drop the held view so the committer can merge S0→S1, then process S2.
+        drop(held_view);
+
+        hot_state.wait_for_merge(2);
+        let (_, committed) = hot_state.get_committed();
+        assert_eq!(committed.next_version(), 2);
+    }
+
     #[test]
     fn test_rapid_commits_with_lingering_reader() {
         let state0 = State::new_empty(TEST_CONFIG);
```

### storage/storage-interface/src/state_store/state.rs
```diff
@@ -142,6 +142,15 @@ impl State {
         self.shards[0].is_descendant_of(&rhs.shards[0])
     }
 
+    /// Returns true if `self` can serve as the base (older) side of a `StateDelta`
+    /// with `current` as the newer side.
+    pub fn can_be_delta_base_of(&self, current: &State) -> bool {
+        self.shards
+            .iter()
+            .zip(current.shards.iter())
+            .all(|(base_shard, top_shard)| top_shard.can_view_after(base_shard))
+    }
+
     pub fn latest_hot_key(&self, shard_id: usize) -> Option<StateKey> {
         self.hot_state_metadata[shard_id].latest.clone()
     }
```
