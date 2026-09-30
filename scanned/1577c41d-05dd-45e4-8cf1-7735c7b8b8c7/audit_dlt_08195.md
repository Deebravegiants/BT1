# [?] fix: possible panic when fetching double Merkle meta for block ID repair (#12679)

## Summary
Severity: Unknown
Chain: Solana
Component: anza-xyz/agave
Published: 2026-05-27
Source: https://github.com/anza-xyz/agave/commit/37ddf95d399d1a011febb4b16f470fa3afdec730
Type: security-commit

## Details
fix: possible panic when fetching double Merkle meta for block ID repair (#12679)

## Patch
### ledger/src/blockstore.rs
```diff
@@ -989,10 +989,11 @@ impl Blockstore {
             return Ok(None);
         };
 
-        // Get the doulbe merkle meta - the block must be full, so we can unwrap here
-        let dmm = self
-            .get_double_merkle_meta_maybe_populate_proofs(slot, location)?
-            .expect("block is full, double merkle meta must exist");
+        // Block was full above, get_block_location returned Some, but may have
+        // been purged by BlockstoreCleanupService in between.
+        let Some(dmm) = self.get_double_merkle_meta_maybe_populate_proofs(slot, location)? else {
+            return Ok(None);
+        };
         Ok(Some((dmm, location)))
     }
 
```
