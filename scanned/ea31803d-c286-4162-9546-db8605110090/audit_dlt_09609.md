# [?] Fix panic in construct_pivot_state of full node. (#1017)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-03-11
Source: https://github.com/Conflux-Chain/conflux-rust/commit/98cac91f1bb30e3780451ce48665db9d78994589
Type: security-commit

## Details
Fix panic in construct_pivot_state of full node. (#1017)

## Patch
### core/src/consensus/consensus_inner/consensus_new_block_handler.rs
```diff
@@ -1884,6 +1884,11 @@ impl ConsensusNewBlockHandler {
             self.data_man.state_availability_boundary.read().lower_bound;
         let start_pivot_index =
             (state_boundary_height - inner.cur_era_genesis_height) as usize;
+        if start_pivot_index >= inner.pivot_chain.len() {
+            // The pivot chain of recovered blocks is before state lower_bound,
+            // so we do not need to construct any pivot state.
+            return;
+        }
         let start_hash = inner.arena[inner.pivot_chain[start_pivot_index]].hash;
         // Here, we should ensure the epoch_execution_commitment for stable hash
         // must be loaded into memory. Since, in some rare cases, the number of
```
