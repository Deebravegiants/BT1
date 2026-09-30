# [?] Avoid reentrant deadlock in `latest_finalized_epoch_number`.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2022-01-18
Source: https://github.com/Conflux-Chain/conflux-rust/commit/aea61746a06571facb08d7326947ec2110b59bd7
Type: security-commit

## Details
Avoid reentrant deadlock in `latest_finalized_epoch_number`.

## Patch
### core/src/consensus/mod.rs
```diff
@@ -1559,7 +1559,10 @@ impl ConsensusGraphTrait for ConsensusGraph {
     }
 
     fn latest_finalized_epoch_number(&self) -> u64 {
-        self.inner.read().latest_epoch_confirmed_by_pos().1
+        self.inner
+            .read_recursive()
+            .latest_epoch_confirmed_by_pos()
+            .1
     }
 
     fn best_chain_id(&self) -> AllChainID {
```
