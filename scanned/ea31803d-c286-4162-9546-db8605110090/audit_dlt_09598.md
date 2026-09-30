# [?] Fix an underflow for timerchain computation. (#1661)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-07-12
Source: https://github.com/Conflux-Chain/conflux-rust/commit/8aee900baa7447c050d9757750c5aa2f6008225f
Type: security-commit

## Details
Fix an underflow for timerchain computation. (#1661)

## Patch
### core/src/consensus/consensus_inner/mod.rs
```diff
@@ -3208,6 +3208,9 @@ impl ConsensusGraphInner {
                 None => self.cur_era_genesis_block_arena_index,
             };
             for i in self.timer_chain.len()..(fork_at_index + tmp_chain.len()) {
+                if i < self.inner_conf.timer_chain_beta as usize {
+                    continue;
+                }
                 // `end` is the timer chain index of the end of
                 // `timer_chain_beta` consecutive blocks which
                 // we will compute accumulative lca.
```
