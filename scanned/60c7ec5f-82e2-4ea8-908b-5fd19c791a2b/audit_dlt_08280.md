# [?] txncache: fix data race

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-09-30
Source: https://github.com/firedancer-io/firedancer/commit/ceee408d37a3b821c76ef1fe5ff691801ffec63f
Type: security-commit

## Details
txncache: fix data race

## Patch
### src/flamenco/runtime/fd_txncache.c
```diff
@@ -372,7 +372,7 @@ static inline blockcache_t *
 blockhash_on_fork( fd_txncache_t *      tc,
                    blockcache_t const * fork,
                    uchar const *        blockhash ) {
-  fd_txncache_blockcache_shmem_t const * candidate = blockhash_map_ele_query( tc->blockhash_map, fd_type_pun_const( blockhash ), NULL, tc->blockcache_shmem_pool );
+  fd_txncache_blockcache_shmem_t const * candidate = blockhash_map_ele_query_const( tc->blockhash_map, fd_type_pun_const( blockhash ), NULL, tc->blockcache_shmem_pool );
   if( FD_UNLIKELY( !candidate ) ) FD_LOG_CRIT(( "transaction refers to blockhash %s which does not exist", FD_BASE58_ENC_32_ALLOCA( blockhash ) ));
 
   while( candidate ) {
```
