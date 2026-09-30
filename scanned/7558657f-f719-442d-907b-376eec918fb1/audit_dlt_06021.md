# [?] fix: group reconciliation votes by block_id to resolve same-block deadlock (#3269)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2026-04-17
Source: https://github.com/FuelLabs/fuel-core/commit/f7826d1c1b58cdfeabbf44bc7b671a7b14ea3039
Type: security-commit

## Details
fix: group reconciliation votes by block_id to resolve same-block deadlock (#3269)

## Summary

- Fixes a PoA reconciliation deadlock observed on devnet 2026-04-17
where the same block ended up on all 6 Redis nodes with three different
epochs, causing permanent livelock
- `unreconciled_blocks` now groups votes by `block_id` only, tracking
max epoch as a tiebreaker. Identical blocks written during re-promotion
storms count toward quorum.
- Added a regression test that reproduces the exact production error
string

## The bug

During re-promotion storms (two pods racing for leadership), the same
block can be written to different Redis nodes with different epochs. The
old vote grouping `(epoch, block_id)` fragmented these identical blocks
into separate vote groups:

```
Node state (same block_id, different epoch stamps):
  1a-0, 1a-1, 1b-1: epoch 268 → vote group A, count=3
  1b-0:            epoch 269 → vote group B, count=1
  1c-0, 1c-1:      epoch 270 → vote group C, count=2  ← max-epoch winner

Required quorum: 4.  Winner count: 2 → repair attempted.
Repair writes the winner to all 6 nodes → HEIGHT_EXISTS on every node
(each has SOME entry at that height) → Written=0 → total=2 < quorum.
Permanent livelock.
```

## The fix

Group by `block_id` alone; track max epoch per block_id as the
tiebreaker when block_ids genuinely differ:

```rust
// Before
HashMap::<(u64, BlockId), (usize, SealedBlock)>
vote_key = (*epoch, block.entity.id())
winner = max_by_key(epoch)

// After
HashMap::<BlockId, (u64, usize, SealedBlock)>  // (max_epoch, count, block)
vote_key = block.entity.id()
winner = max_by_key(max_epoch)
```

**Behavior change:**
- Same block with multiple epochs → single vote group → counts as a
single block on N nodes → reconciles directly without repair (this fixes
the deadlock)
- Genuinely different blocks at same height → picks higher-epoch block →
same behavior as before

## Test plan

- [x] New test
`leader_state__when_same_block_has_different_epochs_across_nodes_then_reconciles_without_repair`
reproduces the exact production error without the fix (`"Backlog
unresolved at height 1: repair failed to reach quorum"`) and passes with
it
- [x] All 9 existing `leader_state__*` tests still pass
- [ ] Deploy to devnet and verify the stuck authority recovers

### .changes/fixed/3269.md
```diff
@@ -0,0 +1 @@
+Fix PoA reconciliation deadlock when the same block exists on all Redis nodes but with different epochs. `unreconciled_blocks` now groups votes by `block_id` only (tracking max epoch as tiebreaker), so identical blocks written during re-promotion storms count toward quorum.
```

### Cargo.lock
```diff
@@ -10896,7 +10896,6 @@ dependencies = [
  "fuel-core",
  "fuel-core-bin",
  "fuel-core-client",
- "fuel-core-executor",
  "fuel-core-p2p",
  "fuel-core-poa",
  "fuel-core-relayer",
```

### crates/fuel-core/src/service/adapters/consensus_module/poa.rs
```diff
@@ -797,20 +797,29 @@ impl RedisLeaderLeaseAdapter {
                 break;
             }
 
+            // Group votes by block_id only (not epoch). The same block can
+            // be written to different nodes with different epochs during
+            // re-promotion storms — but if the block_id matches, it's the
+            // same block and all copies count toward quorum. We track the
+            // max epoch per block_id as the tiebreaker for fork resolution
+            // when block_ids genuinely differ.
             let votes = blocks_by_node
                 .iter()
                 .filter_map(|blocks_by_height| blocks_by_height.get(&current_height))
                 .flat_map(|blocks_by_epoch| blocks_by_epoch.iter())
                 .fold(
-                    HashMap::<(u64, BlockId), (usize, SealedBlock)>::new(),
+                    HashMap::<BlockId, (u64, usize, SealedBlock)>::new(),
                     |mut votes, (epoch, block)| {
-                        let vote_key = (*epoch, block.entity.id());
+                        let vote_key = block.entity.id();
                         match votes.get_mut(&vote_key) {
-                            Some((count, _)) => {
+                            Some((max_epoch, count, _)) => {
                                 *count = count.saturating_add(1);
+                                if *epoch > *max_epoch {
+                                    *max_epoch = *epoch;
+                                }
                             }
                             None => {
-                                votes.insert(vote_key, (1, block.clone()));
+                                votes.insert(vote_key, (*epoch, 1, block.clone()));
                             }
                         }
                         votes
@@ -819,8 +828,8 @@ impl RedisLeaderLeaseAdapter {
 
             let winner = votes
                 .into_iter()
-                .max_by_key(|((epoch, _), _)| *epoch)
-                .map(|(_, (count, block))| (count, block));
+                .max_by_key(|(_, (max_epoch, _, _))| *max_epoch)
+                .map(|(_, (_, count, block))| (count, block));
 
             if let Some((count, block)) = winner {
                 if self.quorum_reached(count) {
@@ -1565,6 +1574,81 @@ mod tests {
         );
     }
 
+    /// Reproduces the devnet deadlock from April 17, 2026.
+    ///
+    /// The same block was written to all 3 nodes during re-promotion storms,
+    /// so each node has the same block_id but with different epoch metadata.
+    /// The old `(epoch, block_id)` vote grouping fragmented these into
+    /// separate vote groups, with the max-epoch group having a count below
+    /// quorum. Repair then failed because every node returned HEIGHT_EXISTS.
+    ///
+    /// With the fix (grouping by block_id only), all copies of the same
+    /// block count toward quorum regardless of epoch metadata — so this
+    /// state resolves without repair.
+    #[tokio::test(flavor = "multi_thread")]
+    async fn leader_state__when_same_block_has_different_epochs_across_nodes_then_reconciles_without_repair()
+     {
+        // given: same block on all 3 nodes, but with different epochs
+        // (as happens when re-promotion writes race during production)
+        let redis_a = RedisTestServer::spawn();
+        let redis_b = RedisTestServer::spawn();
+        let redis_c = RedisTestServer::spawn();
+        let lease_key = "poa:test:same-block-different-epochs".to_string();
+        let stream_key = format!("{lease_key}:block:stream");
+        let adapter = new_test_adapter(
+            vec![
+                redis_a.redis_url(),
+                redis_b.redis_url(),
+                redis_c.redis_url(),
+            ],
+            lease_key,
+        );
+        assert!(
+            adapter
+                .acquire_lease_if_free()
+                .await
+                .expect("acquire should succeed"),
+            "adapter should acquire lease"
+        );
+
+        // Same block (same data, same block_id) on all 3 nodes, but each
+        // with a different epoch. This simulates what happens when the
+        // original leader was re-promoted repeatedly during a race,
+        // writing the same block content each time with a bumped epoch.
+        let block = poa_block_at_time(1, 10);
+        let block_data = postcard::to_allocvec(&block).expect("should serialize");
+
+        let redis_a_client =
+            redis::Client::open(redis_a.redis_url()).expect("redis a client");
+        let redis_b_client =
+            redis::Client::open(redis_b.redis_url()).expect("redis b client");
+        let redis_c_client =
+            redis::Client::open(redis_c.redis_url()).expect("redis c client");
+        let mut conn_a = redis_a_client.get_connection().expect("redis a conn");
+        let mut conn_b = redis_b_client.get_connection().expect("redis b conn");
+        let mut conn_c = redis_c_client.get_connection().expect("redis c conn");
+
+        // Same block_id, three different epochs
+        append_stream_block(&mut conn_a, &stream_key, 1, &block_data, 5);
+        append_stream_block(&mut conn_b, &stream_key, 1, &block_data, 7);
+        append_stream_block(&mut conn_c, &stream_key, 1, &block_data, 9);
+
+        // when: leader reconciles
+        let leader_state = adapter
+            .leader_state(1.into())
+            .await
+            .expect("leader_state should succeed");
+
+        // then: the block is reconciled directly (no repair needed). Without
+        // the fix, the old logic would have split the 3 copies into 3 vote
+        // groups and tried to repair the max-epoch group (count=1), which
+        // would deadlock because every node returns HEIGHT_EXISTS.
+        assert!(
+            matches!(leader_state, LeaderState::UnreconciledBlocks(ref blocks) if blocks.len() == 1),
+            "Expected block to be reconciled from quorum across mixed epochs, got {leader_state:?}"
+        );
+    }
+
     #[tokio::test(flavor = "multi_thread")]
     async fn leader_state__when_same_height_entry_exists_on_less_than_quorum_nodes_then_repairs_it()
      {
```
