# [?] poh: fix rare race condition

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-10-27
Source: https://github.com/firedancer-io/firedancer/commit/d5e73d16d227ebb34159c6ba9ac0adb37bf6f261
Type: security-commit

## Details
poh: fix rare race condition

## Patch
### src/discof/poh/fd_poh_tile.c
```diff
@@ -119,6 +119,15 @@ returnable_frag( fd_poh_tile_t *     ctx,
   if( FD_UNLIKELY( chunk<ctx->in[ in_idx ].chunk0 || chunk>ctx->in[ in_idx ].wmark || sz>ctx->in[ in_idx ].mtu ) )
     FD_LOG_ERR(( "chunk %lu %lu corrupt, not in range [%lu,%lu]", chunk, sz, ctx->in[ in_idx ].chunk0, ctx->in[ in_idx ].wmark ));
 
+  /* There's a race condition where we might receive microblocks from
+     banks before we have learned what the leader bank is from replay
+     (the become_leader message makes it from replay->pack->bank->poh)
+     before it just makes it from replay->poh.  This is rare but
+     violates invariants in poh, so we simply do not process any
+     transactions for mixin until we have learned what the leader bank
+     is. */
+  if( FD_UNLIKELY( ctx->in_kind[ in_idx ]==IN_KIND_BANK && !fd_poh_have_leader_bank( ctx->poh ) ) ) return 1;
+
   if( FD_UNLIKELY( ctx->in_kind[ in_idx ]==IN_KIND_REPLAY && fd_poh_have_leader_bank( ctx->poh ) ) ) return 1;
   /* If prior leaders skipped, it might happen that replay tells us to
      become leader, but poh is still hashing through the skipped slots
```
