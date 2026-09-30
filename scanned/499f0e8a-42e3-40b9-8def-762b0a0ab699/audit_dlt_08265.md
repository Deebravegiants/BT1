# [?] fix openssl overflow

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-02-11
Source: https://github.com/firedancer-io/firedancer/commit/a1e64d63afbb9b74ac299ef371a55e7ebfa1e93b
Type: security-commit

## Details
fix openssl overflow

## Patch
### src/waltz/openssl/fd_openssl_tile.c
```diff
@@ -32,7 +32,12 @@ crypto_malloc( ulong        num,
                int          line ) {
   (void)file;
   (void)line;
-  void * result = fd_alloc_malloc( fd_ossl_alloc, 8UL, num + 8UL );
+  ulong alloc_sz;
+  if( FD_UNLIKELY( __builtin_uaddl_overflow( num, 8UL, &alloc_sz ) ) ) {
+    fd_ossl_alloc_errors++;
+    return NULL;
+  }
+  void * result = fd_alloc_malloc( fd_ossl_alloc, 8UL, alloc_sz );
   if( FD_UNLIKELY( !result ) ) {
     fd_ossl_alloc_errors++;
     return NULL;
@@ -66,7 +71,12 @@ crypto_realloc( void *       addr,
     return NULL;
   }
 
-  void * new = fd_alloc_malloc( fd_ossl_alloc, 8UL, num + 8UL );
+  ulong alloc_sz;
+  if( FD_UNLIKELY( __builtin_uaddl_overflow( num, 8UL, &alloc_sz ) ) ) {
+    fd_ossl_alloc_errors++;
+    return NULL;
+  }
+  void * new = fd_alloc_malloc( fd_ossl_alloc, 8UL, alloc_sz );
   if( FD_UNLIKELY( !new ) ) return NULL;
 
   ulong old_num = *(ulong*)( (uchar*)addr - 8UL );
```
