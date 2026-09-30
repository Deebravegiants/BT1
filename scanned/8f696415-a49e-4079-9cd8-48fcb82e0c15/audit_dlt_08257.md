# [?] gossip: fix wfs overflow (#9449)

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-04-22
Source: https://github.com/firedancer-io/firedancer/commit/57db38c6cc0cfc291cf005552f9f0d2a9ca89933
Type: security-commit

## Details
gossip: fix wfs overflow (#9449)

## Patch
### src/discof/gossip/fd_gossip_tile.c
```diff
@@ -138,7 +138,7 @@ gossip_activity_update_fn( void *                           _ctx,
     ctx->wfs_active[ stake_idx ] = 0;
   }
 
-  if( FD_UNLIKELY( ctx->wfs_stake.total>0UL && (100UL*ctx->wfs_stake.online) / ctx->wfs_stake.total >= 80UL ) ) {
+  if( FD_UNLIKELY( ctx->wfs_stake.total>0UL && (ulong)( ((double)ctx->wfs_stake.online / (double)ctx->wfs_stake.total) * 100.0 ) >= 80UL ) ) {
     ctx->wfs_state = FD_GOSSIP_WFS_STATE_PUBLISH;
   }
 }
```
