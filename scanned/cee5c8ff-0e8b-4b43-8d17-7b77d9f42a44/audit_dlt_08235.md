# [?] net/sock: fix OOB access with invalid topology

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-08-27
Source: https://github.com/firedancer-io/firedancer/commit/b8a3ebfb0cf1808669977f620f30519a29e306fa
Type: security-commit

## Details
net/sock: fix OOB access with invalid topology

## Patch
### src/disco/net/sock/fd_sock_tile.c
```diff
@@ -294,6 +294,10 @@ unprivileged_init( fd_topo_t const *      topo,
     }
   }
 
+  if( FD_UNLIKELY( ctx->repair_shred_sock_idx!=UINT_MAX && ctx->repair_rx==0xFF ) ) {
+    FD_LOG_ERR(( "repair intake socket configured but no net_repair out link was found" ));
+  }
+
   for( ulong i=0UL; i<(tile->in_cnt); i++ ) {
     if( !strstr( topo->links[ tile->in_link_id[ i ] ].name, "_net" ) ) {
       FD_LOG_ERR(( "in link %lu is not a net TX link", i ));
```
