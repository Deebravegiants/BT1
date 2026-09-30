# [?] fix(txpool): prevent underflow in blobstore versioned hash lookup (#22454)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-02-21
Source: https://github.com/paradigmxyz/reth/commit/bc33eb764a8ec351ffbd7d6177410121e002bc8b
Type: security-commit

## Details
fix(txpool): prevent underflow in blobstore versioned hash lookup (#22454)

Co-authored-by: Matthias Seitz <matthias.seitz@outlook.de>
Co-authored-by: Amp <amp@ampcode.com>

## Patch
### crates/transaction-pool/src/blobstore/disk.rs
```diff
@@ -82,8 +82,11 @@ impl DiskFileBlobStore {
                 for (hash_idx, match_result) in
                     blob_sidecar.match_versioned_hashes(versioned_hashes)
                 {
-                    result[hash_idx] = Some(match_result);
-                    missing_count -= 1;
+                    let slot = &mut result[hash_idx];
+                    if slot.is_none() {
+                        missing_count -= 1;
+                    }
+                    *slot = Some(match_result);
                 }
             }
 
```

### crates/transaction-pool/src/blobstore/mem.rs
```diff
@@ -30,8 +30,11 @@ impl InMemoryBlobStore {
                 for (hash_idx, match_result) in
                     blob_sidecar.match_versioned_hashes(versioned_hashes)
                 {
-                    result[hash_idx] = Some(match_result);
-                    missing_count -= 1;
+                    let slot = &mut result[hash_idx];
+                    if slot.is_none() {
+                        missing_count -= 1;
+                    }
+                    *slot = Some(match_result);
                 }
             }
 
```
