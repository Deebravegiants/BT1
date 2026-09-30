# [?] Prevent a panic caused by delaying block deleting. (#1736)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-08-01
Source: https://github.com/Conflux-Chain/conflux-rust/commit/c22113bcfe183bce5166d235cbcd7cf48efeff7c
Type: security-commit

## Details
Prevent a panic caused by delaying block deleting. (#1736)

## Patch
### core/src/consensus/consensus_inner/mod.rs
```diff
@@ -2976,6 +2976,13 @@ impl ConsensusGraphInner {
         if !self.arena[me].is_timer || self.arena[me].data.partial_invalid {
             return NULL;
         }
+        if self.arena[me].data.ledger_view_timer_chain_height
+            < self.cur_era_genesis_timer_chain_height
+        {
+            // This is only possible if `me` is in the anticone of
+            // `cur_era_genesis`.
+            return NULL;
+        }
         let timer_chain_index =
             (self.arena[me].data.ledger_view_timer_chain_height
                 - self.cur_era_genesis_timer_chain_height) as usize;
```
