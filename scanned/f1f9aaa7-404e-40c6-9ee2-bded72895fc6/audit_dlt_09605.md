# [?] Fix skipped_blockset causing crash (#1225)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-04-11
Source: https://github.com/Conflux-Chain/conflux-rust/commit/62926e2df30403c561b2e1225aa3354e1bc3f332
Type: security-commit

## Details
Fix skipped_blockset causing crash (#1225)

## Patch
### core/src/consensus/consensus_inner/consensus_new_block_handler.rs
```diff
@@ -161,6 +161,13 @@ impl ConsensusNewBlockHandler {
                 .data
                 .blockset_in_own_view_of_epoch
                 .retain(|v| new_era_block_arena_index_set.contains(v));
+            // FIXME: This causes inconsistency between the db and the memory.
+            // FIXME: Although it does not impact the sync process. We should
+            // consider fix it.
+            inner.arena[me]
+                .data
+                .skipped_epoch_blocks
+                .retain(|v| new_era_block_arena_index_set.contains(v));
             if !new_era_block_arena_index_set.contains(
                 &inner.arena[me].data.past_view_last_timer_block_arena_index,
             ) {
```
