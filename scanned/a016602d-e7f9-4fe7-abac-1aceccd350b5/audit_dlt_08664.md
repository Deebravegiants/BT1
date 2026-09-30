# [?] Use try_read to avoid deadlock due to rayon releasing concurrent reads all at once

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkOS-test
Published: 2025-01-03
Source: https://github.com/AleoNet/snarkOS-test/commit/970386ff51cecdd47005d76dc60c4d41e2732dc2
Type: security-commit

## Details
Use try_read to avoid deadlock due to rayon releasing concurrent reads all at once

## Patch
### node/bft/ledger-service/src/ledger.rs
```diff
@@ -126,11 +126,15 @@ impl<N: Network, C: ConsensusStorage<N>> LedgerService<N> for CoreLedgerService<
 
     /// Returns the block for the given block height.
     fn get_block(&self, height: u32) -> Result<Block<N>> {
-        if let Some(block) = self.block_cache.read().get(&height) {
-            Ok(block.clone())
-        } else {
-            self.ledger.get_block(height)
+        // First, check if the block is in the block cache.
+        // Using `try_read` to avoid blocking the thread: https://github.com/rayon-rs/rayon/issues/1205
+        if let Some(block_cache) = self.block_cache.try_read() {
+            if let Some(block) = block_cache.get(&height) {
+                return Ok(block.clone());
+            }
         }
+        // If no block is found in the cache, then retrieve the block from the ledger.
+        self.ledger.get_block(height)
     }
 
     /// Returns the blocks in the given block range.
```
