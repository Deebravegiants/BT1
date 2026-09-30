# [?] replay: fix bank use after free

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-11-06
Source: https://github.com/firedancer-io/firedancer/commit/79c88afddc66ff82e3f200565521e4195772000e
Type: security-commit

## Details
replay: fix bank use after free

## Patch
### src/discof/replay/fd_replay_tile.c
```diff
@@ -886,15 +886,15 @@ replay_block_finalize( fd_replay_tile_t *  ctx,
      tower stuff. */
   publish_slot_completed( ctx, stem, bank, 0 );
 
+  /* Mark the bank as frozen. */
+  fd_banks_mark_bank_frozen( ctx->banks, bank );
+
   /* If enabled, dump the block to a file and reset the dumping
      context state */
   if( FD_UNLIKELY( ctx->capture_ctx && ctx->capture_ctx->dump_block_to_pb ) ) {
     fd_dump_block_to_protobuf( ctx->block_dump_ctx, ctx->banks, bank, ctx->accdb->funk, ctx->capture_ctx );
     fd_block_dump_context_reset( ctx->block_dump_ctx );
   }
-
-  /* Mark the bank as frozen. */
-  fd_banks_mark_bank_frozen( ctx->banks, bank );
 }
 
 /**********************************************************************/
@@ -1039,6 +1039,8 @@ fini_leader_bank( fd_replay_tile_t *  ctx,
 
   publish_slot_completed( ctx, stem, ctx->leader_bank, 0 );
 
+  fd_banks_mark_bank_frozen( ctx->banks, ctx->leader_bank );
+
   /* Copy the vote tower of all the vote accounts into the buffer,
       which will be published in after_credit. */
   buffer_vote_towers( ctx, &xid, ctx->leader_bank );
@@ -1052,8 +1054,6 @@ fini_leader_bank( fd_replay_tile_t *  ctx,
   ctx->recv_block_id = 0;
   ctx->recv_poh      = 0;
   ctx->is_leader     = 0;
-
-  fd_banks_mark_bank_frozen( ctx->banks, ctx->leader_bank );
 }
 
 static void
```
