# [?] fix(state): handle invalidateblock/reconsiderblock edge cases without panicking (#10592)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-06-25
Source: https://github.com/ZcashFoundation/zebra/commit/d58097f8793aa6122e9b5c5becd11c26d397401b
Type: security-commit

## Details
fix(state): handle invalidateblock/reconsiderblock edge cases without panicking (#10592)

* fix(state): handle invalidateblock/reconsiderblock edge cases without panicking

Three authenticated state-control RPC sequences could panic the
non-finalized write task, which is process-fatal under `panic = "abort"`:

1. `invalidateblock` on the root of a tracked non-finalized chain called
   `BTreeSet::remove(&chain)`, which compared the stored chain against
   itself and reached `Chain::cmp`'s `unreachable!()` for matching tip
   hashes.
2. `invalidateblock` on two same-height sibling fork tips with the same
   parent: the second invalidation produced a shortened parent chain
   whose tip hash matched an existing entry, and `BTreeSet::insert`
   reached the same `unreachable!()` while comparing.
3. `reconsiderblock` repeated for the same successfully reconsidered
   hash: the first call removed the invalidation record from a clone of
   `invalidated_blocks` instead of from the live map, so the second
   call replayed the same chain suffix into a chain set that already
   contained the restored tip and hit the same `Chain::cmp` panic. The
   replay path also used `Chain::push(...).expect(...)` for unexpected
   failures.

Changes:

- `Chain::cmp` returns `Ordering::Equal` for chains with matching
  cumulative work and tip hash. The `BTreeSet<Arc<Chain>>` already
  treats equal items as duplicates, so this keeps the uniqueness
  invariant via no-op inserts instead of a panic.
- `NonFinalizedState::invalidate_block` root branch retains the chain
  set by tip hash instead of `BTreeSet::remove(&chain)`. The non-root
  branch is unchanged at the call site, but is now idempotent against
  same-tip-hash collisions because `Chain::cmp` no longer panics.
- `NonFinalizedState::reconsider_block` copies the height out of the
  invalidation lookup, then calls `shift_remove(&height)` on the live
  map (not a clone). The replay loop returns the typed
  `ReconsiderError::ReplayFailed(ValidateContextError)` instead of
  `expect()`.

Add three regression tests under
`zebra-state/src/service/non_finalized_state/tests/vectors.rs`:

- `invalidating_non_finalized_root_does_not_panic`
- `invalidating_same_height_fork_tips_is_idempotent`
- `reconsider_block_removes_live_entry_and_second_call_returns_missing`

Closes #10586

* fix(state): preserve invalidation record on reconsider failure

Address codex review feedback on #10592: the previous version removed
the invalidation record from the live `invalidated_blocks` map up front,
before parent-chain lookup and replay. If either fallible step failed,
the record was destroyed even though the chain set was never updated.

Concrete sequence: invalidate child `B` (with grandchild), then
invalidate parent/root `A`, then `reconsiderblock(B)` returns
`ParentChainNotFound` because `A` is no longer in the non-finalized
state. The previous fix would have deleted `B`'s record on that
failure, making it unrecoverable after `reconsiderblock(A)`.

Restructure `reconsider_block` to:

- Look up the invalidation entry without removing it, cloning the
  `Arc<Vec<...>>` for replay.
- Run parent-chain lookup and the replay loop against that clone.
- Only `shift_remove` the live entry after all fallible steps have
  succeeded, atomic with installing the restored chain.

Add a regression test for the failure-preservation path:
`reconsider_block_preserves_record_when_parent_chain_missing`.

* docs: move #10586 changelog entry into Unreleased Fixed section

Fixes the markdown-lint CI failure (MD032) caused by the entry landing
after the 4.5.0 Contributors list during the merge of main.

* refactor(state): address review feedback on #10592

- Correct Chain::cmp docs: equality requires matching cumulative work AND
  tip hash, not tip hash alone (per Copilot review).
- Trim the verbose reconsider_block deferral comment to two lines.
- Factor the repeated invalidate/reconsider test setup into a
  new_invalidate_test_state helper.
- Shorten the CHANGELOG entry to one sentence.

Per oxarbitrage and Copilot review on #10592.

* refactor(state): use BTreeSet::remove for root invalidation

Per jvff/oxarbitrage review on #10592: now that Chain::cmp returns Equal
instead of panicking, BTreeSet::remove(&chain) no longer aborts and is
more efficient than a tip-hash retain scan, so revert the root-invalidation
branch back to remove(&chain).

Also merges main and adds the now-required expect() for the Result-returning
FinalizedState::new in the invalidate/reconsider test helper.

* refactor(state): simplify reconsider_block lookup per review

- Clone the invalidated Vec directly in find_map instead of cloning the Arc
  and then Arc::unwrap_or_clone; the entry stays in the map until shift_remove,
  so the unwrap path never applied.
- Drop the unnecessary 'previously panicked' note on ReconsiderError::ReplayFailed.

Per jvff review on #10592.

* docs(changelog): move #10586 Fixed entry into Unreleased

The main merge reorganized CHANGELOG.md and left the invalidateblock/
reconsiderblock entry inside the already-released 5.1.0 section. Move it
under [Unreleased] > Fixed. Per Copilot review on #10592.

* Fix changelog formatting

Remove extra newline from merge commit.

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Conrado Gouvea <conrado@zfnd.org>
Co-authored-by: Janito Vaqueiro Ferreira Filho <janito.vff@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

### CHANGELOG.md
```diff
@@ -41,6 +41,9 @@ and this project adheres to [Semantic Versioning](https://semver.org).
 
 - Released `zebrad` binaries report their source commit in `zebrad version`
   ([#10798](https://github.com/ZcashFoundation/zebra/pull/10798))
+- Handle `invalidateblock` and `reconsiderblock` edge cases (chain-root and
+  same-height sibling-tip invalidation, repeated reconsideration) without panicking
+  ([#10586](https://github.com/ZcashFoundation/zebra/issues/10586))
 
 ### Security
 
```

### zebra-state/src/error.rs
```diff
@@ -218,6 +218,11 @@ pub enum ReconsiderError {
     /// The reconsider request was dropped before processing.
     #[error("reconsider block request was unexpectedly dropped")]
     ReconsiderResponseDropped,
+
+    /// Replaying an invalidated block into the restored chain failed contextual
+    /// validation.
+    #[error("replaying a previously invalidated block failed contextual validation: {0}")]
+    ReplayFailed(#[source] ValidateContextError),
 }
 
 /// An error describing why a block failed contextual validation.
```

### zebra-state/src/service/non_finalized_state.rs
```diff
@@ -427,26 +427,21 @@ impl NonFinalizedState {
         block_hash: block::Hash,
         finalized_state: &ZebraDb,
     ) -> Result<Vec<block::Hash>, ReconsiderError> {
-        // Get the invalidated blocks that were invalidated by the given block_hash
-        let height = self
+        // Locate the record but keep it live until replay succeeds, so a
+        // recoverable error can't lose it; it is `shift_remove`d atomically with
+        // the insert below.
+        let (height, invalidated_blocks) = self
             .invalidated_blocks
             .iter()
             .find_map(|(height, blocks)| {
                 if blocks.first()?.hash == block_hash {
-                    Some(height)
+                    Some((*height, (**blocks).clone()))
                 } else {
                     None
                 }
             })
             .ok_or(ReconsiderError::MissingInvalidatedBlock(block_hash))?;
 
-        let invalidated_blocks = Arc::unwrap_or_clone(
-            self.invalidated_blocks
-                .clone()
-                .shift_remove(height)
-                .ok_or(ReconsiderError::MissingInvalidatedBlock(block_hash))?,
-        );
-
         let invalidated_block_hashes = invalidated_blocks
             .iter()
             .map(|block| block.hash)
@@ -486,10 +481,15 @@ impl NonFinalizedState {
         for block in invalidated_blocks {
             modified_chain = modified_chain
                 .push(block)
-                .expect("previously invalidated block should be valid for chain");
+                .map_err(ReconsiderError::ReplayFailed)?;
         }
 
-        let (height, hash) = modified_chain.non_finalized_tip();
+        let (tip_height, tip_hash) = modified_chain.non_finalized_tip();
+
+        // All fallible steps have succeeded; remove the invalidation record
+        // atomically with installing the restored chain so a failed attempt
+        // does not destroy the record.
+        self.invalidated_blocks.shift_remove(&height);
 
         // Only track invalidated_blocks that are not yet finalized. Once blocks are finalized (below the best_chain_root_height)
         // we can discard the block.
@@ -502,7 +502,7 @@ impl NonFinalizedState {
             chain_set.retain(|chain| chain.non_finalized_tip_hash() != root_parent_hash)
         });
 
-        self.update_metrics_for_committed_block(height, hash);
+        self.update_metrics_for_committed_block(tip_height, tip_hash);
 
         Ok(invalidated_block_hashes)
     }
```

### zebra-state/src/service/non_finalized_state/chain.rs
```diff
@@ -2335,14 +2335,12 @@ impl Ord for Chain {
     /// `Chain::cmp` is used in a `BTreeSet`, so the fields accessed by `cmp` must not have
     /// interior mutability.
     ///
-    /// # Panics
-    ///
-    /// If two chains compare equal.
-    ///
-    /// This panic enforces the [`NonFinalizedState::chain_set`][2] unique chain invariant.
-    ///
-    /// If the chain set contains duplicate chains, the non-finalized state might
-    /// handle new blocks or block finalization incorrectly.
+    /// `cmp` returns [`Ordering::Equal`] only when both the cumulative work and
+    /// the tip hash match. The [`NonFinalizedState::chain_set`][2] is a
+    /// `BTreeSet<Arc<Chain>>`, so an attempt to insert a chain that compares
+    /// equal to an existing entry is a no-op rather than a process-fatal panic.
+    /// Callers that need to replace such a chain must remove the existing entry
+    /// first.
     ///
     /// [1]: super::NonFinalizedState
     /// [2]: super::NonFinalizedState::chain_set
@@ -2367,10 +2365,7 @@ impl Ord for Chain {
 
             // This comparison is a tie-breaker within the local node, so it does not need to
             // be consistent with the ordering on `ExpandedDifficulty` and `block::Hash`.
-            match self_hash.0.cmp(&other_hash.0) {
-                Ordering::Equal => unreachable!("Chain tip block hashes are always unique"),
-                ordering => ordering,
-            }
+            self_hash.0.cmp(&other_hash.0)
         }
     }
 }
@@ -2385,11 +2380,8 @@ impl PartialEq for Chain {
     /// Chain equality for [`NonFinalizedState::chain_set`][1], using proof of
     /// work, then the tip block hash as a tie-breaker.
     ///
-    /// # Panics
-    ///
-    /// If two chains compare equal.
-    ///
-    /// See [`Chain::cmp`] for details.
+    /// Two chains with the same cumulative work and tip hash are equal; the
+    /// `chain_set` uses this to keep tip hashes unique.
     ///
     /// [1]: super::NonFinalizedState::chain_set
     fn eq(&self, other: &Self) -> bool {
```

### zebra-state/src/service/non_finalized_state/tests/vectors.rs
```diff
@@ -22,6 +22,7 @@ use crate::{
     service::{
         finalized_state::{calculate_deferred_pool_balance_change, FinalizedState},
         non_finalized_state::{Chain, NonFinalizedState, MIN_DURATION_BETWEEN_BACKUP_UPDATES},
+        ReconsiderError,
     },
     tests::FakeChainHelper,
     Config, SemanticallyVerifiedBlock,
@@ -322,6 +323,211 @@ fn invalidate_block_removes_block_and_descendants_from_chain_for_network(
     Ok(())
 }
 
+/// Regression test for https://github.com/ZcashFoundation/zebra/issues/10586.
+///
+/// Build an empty `NonFinalizedState` and an ephemeral `FinalizedState` with a
+/// populated value pool — the shared setup for the invalidate/reconsider
+/// regression tests below.
+fn new_invalidate_test_state(network: &Network) -> (NonFinalizedState, FinalizedState) {
+    let state = NonFinalizedState::new(network);
+    let finalized_state = FinalizedState::new(
+        &Config::ephemeral(),
+        network,
+        #[cfg(feature = "elasticsearch")]
+        false,
+    )
+    .expect("opening an ephemeral database should succeed");
+    finalized_state.set_finalized_value_pool(ValueBalance::<NonNegative>::fake_populated_pool());
+    (state, finalized_state)
+}
+
+/// Invalidating the non-finalized root of a tracked chain previously called
+/// `BTreeSet::remove(&chain)`, which compared the stored chain against
+/// itself via `Chain::cmp` and reached an `unreachable!()` for matching tip
+/// hashes. The root branch now retains by tip hash and the call returns
+/// successfully without panicking.
+#[test]
+fn invalidating_non_finalized_root_does_not_panic() {
+    let _init_guard = zebra_test::init();
+
+    let network = Network::Mainnet;
+    let block1: Arc<Block> = Arc::new(network.test_block(653599, 583999).unwrap());
+    let block2 = block1.make_fake_child().set_work(10);
+
+    let (mut state, finalized_state) = new_invalidate_test_state(&network);
+
+    state
+        .commit_new_chain(block1.clone().prepare(), &finalized_state)
+        .expect("fake root block should commit to an empty non-finalized state");
+    state
+        .commit_block(block2.prepare(), &finalized_state)
+        .expect("fake child block should extend the fake root chain");
+
+    state
+        .invalidate_block(block1.hash())
+        .expect("invalidating the chain root should not panic");
+
+    assert!(
+        state.best_chain().is_none(),
+        "invalidating the root should leave no live non-finalized chain"
+    );
+}
+
+/// Regression test for https://github.com/ZcashFoundation/zebra/issues/10586.
+///
+/// Sequentially invalidating two same-height sibling fork tips with the same
+/// parent previously panicked. The second invalidation produced a shortened
+/// parent chain whose tip hash matched an existing entry, and `BTreeSet::insert`
+/// reached `Chain::cmp`'s `unreachable!()`. After the fix, `Chain::cmp` returns
+/// `Equal` for matching tip hashes, so the duplicate insert is a no-op and the
+/// pre-existing parent chain is retained.
+#[test]
+fn invalidating_same_height_fork_tips_is_idempotent() {
+    let _init_guard = zebra_test::init();
+
+    let network = Network::Mainnet;
+    let block1: Arc<Block> = Arc::new(network.test_block(653599, 583999).unwrap());
+    let block2a = block1.make_fake_child().set_work(10);
+    let block2b = block1.make_fake_child().set_work(11);
+
+    let (mut state, finalized_state) = new_invalidate_test_state(&network);
+
+    state
+        .commit_new_chain(block1.clone().prepare(), &finalized_state)
+        .expect("fake root block should commit to an empty non-finalized state");
+    state
+        .commit_block(block2a.clone().prepare(), &finalized_state)
+        .expect("first fork tip should extend the root chain");
+    state
+        .commit_block(block2b.clone().prepare(), &finalized_state)
+        .expect("second fork tip should fork from the root chain");
+
+    state
+        .invalidate_block(block2a.hash())
+        .expect("first fork tip should invalidate cleanly");
+    state
+        .invalidate_block(block2b.hash())
+        .expect("second sibling fork tip should not panic on collapse to shared parent");
+
+    let best_chain = state
+        .best_chain()
+        .expect("the parent chain should remain after both sibling tips are invalidated");
+    assert!(best_chain.contains_block_hash(block1.hash()));
+    assert!(!best_chain.contains_block_hash(block2a.hash()));
+    assert!(!best_chain.contains_block_hash(block2b.hash()));
+}
+
+/// Regression test for https://github.com/ZcashFoundation/zebra/issues/10586.
+///
+/// `reconsider_block` previously removed the invalidation record from a clone
+/// of `invalidated_blocks` rather than from the live map. A second
+/// `reconsider_block` for the same hash then replayed the same chain suffix
+/// into a chain set that already contained the restored tip, panicking in
+/// `Chain::cmp`'s duplicate-tip check. After the fix, the live entry is
+/// removed and the second call returns `MissingInvalidatedBlock`.
+#[test]
+fn reconsider_block_removes_live_entry_and_second_call_returns_missing() {
+    let _init_guard = zebra_test::init();
+
+    let network = Network::Mainnet;
+    let block1: Arc<Block> = Arc::new(network.test_block(653599, 583999).unwrap());
+    let block2 = block1.make_fake_child().set_work(10);
+    let block3 = block2.make_fake_child().set_work(1);
+
+    let (mut state, finalized_state) = new_invalidate_test_state(&network);
+
+    state
+        .commit_new_chain(block1.prepare(), &finalized_state)
+        .expect("fake root block should commit");
+    state
+        .commit_block(block2.clone().prepare(), &finalized_state)
+        .expect("fake child should extend the root chain");
+    state
+        .commit_block(block3.prepare(), &finalized_state)
+        .expect("fake grandchild should extend the child chain");
+
+    state
+        .invalidate_block(block2.hash())
+        .expect("invalidating the child should succeed");
+
+    state
+        .reconsider_block(block2.hash(), &finalized_state.db)
+        .expect("first reconsider should restore the invalidated chain");
+
+    assert!(
+        state.invalidated_blocks().values().all(|blocks| {
+            blocks
+                .first()
+                .map(|block| block.hash != block2.hash())
+                .unwrap_or(true)
+        }),
+        "first reconsider should remove the invalidated entry from the live map"
+    );
+
+    let second = state.reconsider_block(block2.hash(), &finalized_state.db);
+    assert!(
+        matches!(second, Err(ReconsiderError::MissingInvalidatedBlock(_))),
+        "a second reconsider for the same hash should return MissingInvalidatedBlock; got {second:?}"
+    );
+}
+
+/// Regression test for https://github.com/ZcashFoundation/zebra/issues/10586.
+///
+/// `reconsider_block` must not destroy the invalidation record when a fallible
+/// step fails. We invalidate child `B` (which has a grandchild), then invalidate
+/// its parent/root `A`. Calling `reconsider_block(B)` now must fail with
+/// `ParentChainNotFound` (because `A` is no longer in the non-finalized state)
+/// without removing `B`'s record. A subsequent `reconsider_block(A)` must
+/// restore `A`, after which the original `B` record remains available for a
+/// later reconsider.
+#[test]
+fn reconsider_block_preserves_record_when_parent_chain_missing() {
+    let _init_guard = zebra_test::init();
+
+    let network = Network::Mainnet;
+    let block1: Arc<Block> = Arc::new(network.test_block(653599, 583999).unwrap());
+    let block2 = block1.make_fake_child().set_work(10);
+    let block3 = block2.make_fake_child().set_work(1);
+
+    let (mut state, finalized_state) = new_invalidate_test_state(&network);
+
+    state
+        .commit_new_chain(block1.clone().prepare(), &finalized_state)
+        .expect("fake root should commit");
+    state
+        .commit_block(block2.clone().prepare(), &finalized_state)
+        .expect("fake child should extend the root chain");
+    state
+        .commit_block(block3.prepare(), &finalized_state)
+        .expect("fake grandchild should extend the child chain");
+
+    state
+        .invalidate_block(block2.hash())
+        .expect("invalidating the child should succeed");
+    state
+        .invalidate_block(block1.hash())
+        .expect("invalidating the root should not panic and should succeed");
+
+    // Now block2's parent (block1) is no longer in the non-finalized state, so
+    // reconsidering block2 must fail. The record for block2 must survive the
+    // failure so a later reconsider can still restore it.
+    let result = state.reconsider_block(block2.hash(), &finalized_state.db);
+    assert!(
+        matches!(result, Err(ReconsiderError::ParentChainNotFound(_))),
+        "reconsider with missing parent chain should fail, got {result:?}"
+    );
+
+    assert!(
+        state.invalidated_blocks().values().any(|blocks| {
+            blocks
+                .first()
+                .map(|block| block.hash == block2.hash())
+                .unwrap_or(false)
+        }),
+        "a failed reconsider must not destroy the invalidation record"
+    );
+}
+
 #[test]
 fn reconsider_block_and_reconsider_chain_correctly_reconsiders_blocks_and_descendants() -> Result<()>
 {
```
