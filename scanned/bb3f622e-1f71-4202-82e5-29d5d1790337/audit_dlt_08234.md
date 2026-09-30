# [?] tower: fix NULL deref with misbehaving majority

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-08-28
Source: https://github.com/firedancer-io/firedancer/commit/94e993ef5e4719995e42ebdde14fd685f11d080d
Type: security-commit

## Details
tower: fix NULL deref with misbehaving majority

## Patch
### src/discof/tower/fd_tower_tile.c
```diff
@@ -1519,6 +1519,11 @@ replay_slot_completed( fd_tower_tile_t *            ctx,
     fd_ghost_blk_t * newr = fd_ghost_query( ctx->ghost, &out.root_block_id );
     fd_ghost_blk_t * oldr = fd_ghost_root( ctx->ghost );
 
+    if( FD_UNLIKELY( !newr ) ) {
+      FD_BASE58_ENCODE_32_BYTES( out.root_block_id.uc, root_blk_id );
+      FD_LOG_ERR(( "new root block %s (slot %lu) is not in ghost: our root conflicts with the cluster", root_blk_id, out.root_slot ));
+    }
+
     /* oldr is not guaranteed to be the immediate parent of newr, but is
        rather an arbitrary ancestor.  This can happen if we couldn't
        vote for those intermediate slot(s).  We publish those slots as
```
