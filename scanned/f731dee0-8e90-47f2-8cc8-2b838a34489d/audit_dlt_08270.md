# [?] bundle: fix for startup crash

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-11-19
Source: https://github.com/firedancer-io/firedancer/commit/01b7851d78e7b7622a6a03e41f22b4117209cd33
Type: security-commit

## Details
bundle: fix for startup crash

## Patch
### src/disco/bundle/fd_bundle_tile.c
```diff
@@ -349,6 +349,7 @@ fd_bundle_tile_load_certs( SSL_CTX * ssl_ctx ) {
       /* Not all files in /etc/ssl/certs are valid certs, so ignore errors */
       continue;
     }
+    errno = 0;
   }
 
   if( FD_UNLIKELY( errno && errno!=ENOENT ) ) {
```
