# [?] runtime: genesis file oob read fix (#9522)

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-04-27
Source: https://github.com/firedancer-io/firedancer/commit/a4fe7597441bdb0a85bfe150858e2a3f3cf467d3
Type: security-commit

## Details
runtime: genesis file oob read fix (#9522)

## Patch
### src/discof/genesis/fd_genesi_tile.c
```diff
@@ -274,7 +274,7 @@ after_credit( fd_genesi_tile_t *  ctx,
     FD_TEST( !strcmp( meta->name, "genesis.bin" ) );
     uchar const * blob    = decompressed+512UL;
     ulong         blob_sz = fd_tar_meta_get_size( meta );
-    FD_TEST( actual_decompressed_sz>=512UL+blob_sz );
+    FD_TEST( actual_decompressed_sz>=fd_ulong_sat_add( 512UL, blob_sz ) );
 
     fd_hash_t hash[1];
     fd_sha256_hash( blob, blob_sz, hash->uc );
```
