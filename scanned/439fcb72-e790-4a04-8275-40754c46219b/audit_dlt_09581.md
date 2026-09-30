# [?] Fix a possible panic during mining.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2021-11-29
Source: https://github.com/Conflux-Chain/conflux-rust/commit/3f41e4d502a7905d823958b7f7d249b530c2c67e
Type: security-commit

## Details
Fix a possible panic during mining.

## Patch
### core/src/consensus/consensus_inner/mod.rs
```diff
@@ -1219,7 +1219,7 @@ impl ConsensusGraphInner {
             }
             for referee in &self.arena[index].referees {
                 if anticone.contains(*referee as u32)
-                    || self.arena[idx_parent].era_block == NULL
+                    || self.arena[*referee].era_block == NULL
                 {
                     queue.push_back(*referee);
                 }
@@ -3995,7 +3995,7 @@ impl ConsensusGraphInner {
             }
             for referee in &self.arena[index].referees {
                 if anticone.contains(*referee as u32)
-                    || self.arena[idx_parent].era_block == NULL
+                    || self.arena[*referee].era_block == NULL
                 {
                     queue.push_back(*referee);
                 }
```
