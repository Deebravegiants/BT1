# [?] flamenco, gossip: fix OOB on voter-in link

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-04-14
Source: https://github.com/firedancer-io/firedancer/commit/5eeb524af8cad789095dd6c37b89dc75e48f42a4
Type: security-commit

## Details
flamenco, gossip: fix OOB on voter-in link

## Patch
### src/discof/gossip/fd_gossip_tile.c
```diff
@@ -446,7 +446,7 @@ during_frag( fd_gossip_tile_ctx_t * ctx,
   }
 
   if( in_kind == IN_KIND_VOTER ) {
-    if( FD_UNLIKELY( chunk<in_ctx->chunk0 || chunk>in_ctx->wmark || sz>USHORT_MAX ) ) {
+    if( FD_UNLIKELY( chunk<in_ctx->chunk0 || chunk>in_ctx->wmark || sz>FD_TXN_MTU ) ) {
       FD_LOG_ERR(( "chunk %lu %lu corrupt, not in range [%lu,%lu]", chunk, sz, in_ctx->chunk0, in_ctx->wmark ));
     }
 
```
