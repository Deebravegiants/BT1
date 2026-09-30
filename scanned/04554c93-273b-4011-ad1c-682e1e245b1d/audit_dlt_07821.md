# [?] Fix deadlock on block cache. (#6412)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2024-09-19
Source: https://github.com/sigp/lighthouse/commit/46e0d66e2deea33c9ada4b4767f59c110255da65
Type: security-commit

## Details
Fix deadlock on block cache. (#6412)

* Fix deadlock on block cache.

## Patch
### beacon_node/beacon_chain/src/eth1_chain.rs
```diff
@@ -475,10 +475,10 @@ impl<E: EthSpec> Eth1ChainBackend<E> for CachingEth1Backend<E> {
             voting_period_start_slot,
         );
 
-        let blocks = self.core.blocks().read();
-
-        let votes_to_consider =
-            get_votes_to_consider(blocks.iter(), voting_period_start_seconds, spec);
+        let votes_to_consider = {
+            let blocks = self.core.blocks().read();
+            get_votes_to_consider(blocks.iter(), voting_period_start_seconds, spec)
+        };
 
         trace!(
             self.log,
```
