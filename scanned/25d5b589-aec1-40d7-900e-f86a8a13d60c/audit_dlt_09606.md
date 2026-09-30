# [?] Fix crash caused by using get_ordered_blockset() for non-pivot block in expected_difficulty when checking (#1127)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-03-26
Source: https://github.com/Conflux-Chain/conflux-rust/commit/ad5951d4d1bf8eb1f675c3d8dcbd421ec94be285
Type: security-commit

## Details
Fix crash caused by using get_ordered_blockset() for non-pivot block in expected_difficulty when checking (#1127)

## Patch
### core/src/consensus/consensus_inner/mod.rs
```diff
@@ -1816,7 +1816,10 @@ impl ConsensusGraphInner {
                     &self.arena[parent_arena_index].hash,
                     |h| {
                         let index = self.hash_to_arena_indices.get(h).unwrap();
-                        self.get_ordered_executable_epoch_blocks(*index).len()
+                        let parent = self.arena[*index].parent;
+                        (self.arena[*index].past_num_blocks
+                            - self.arena[parent].past_num_blocks)
+                            as usize
                     },
                 )
             }
@@ -1847,7 +1850,10 @@ impl ConsensusGraphInner {
                 &new_best_hash,
                 |h| {
                     let index = self.hash_to_arena_indices.get(h).unwrap();
-                    self.get_ordered_executable_epoch_blocks(*index).len()
+                    let parent = self.arena[*index].parent;
+                    (self.arena[*index].past_num_blocks
+                        - self.arena[parent].past_num_blocks)
+                        as usize
                 },
             );
         } else {
```
