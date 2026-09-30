# [?] Avoid acquiring another read lock while holding one to avoid potential deadlock (#6200)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2024-07-30
Source: https://github.com/sigp/lighthouse/commit/9b3b73015925a84fbb004f63516d28e45da675ce
Type: security-commit

## Details
Avoid acquiring another read lock while holding one to avoid potential deadlock (#6200)

* Avoid acquiring another read lock to avoid potential deadlock.

## Patch
### beacon_node/eth1/src/service.rs
```diff
@@ -1129,7 +1129,7 @@ impl Service {
 
         Ok(BlockCacheUpdateOutcome {
             blocks_imported,
-            head_block_number: self.inner.block_cache.read().highest_block_number(),
+            head_block_number: block_cache.highest_block_number(),
         })
     }
 }
```
