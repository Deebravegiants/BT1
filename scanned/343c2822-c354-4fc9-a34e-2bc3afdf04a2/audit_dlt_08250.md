# [?] fix(tower): vote txn tower sync overflow (#9962)

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-05-27
Source: https://github.com/firedancer-io/firedancer/commit/8091b748fc4a054186fea2b2b201d8f4f3a459c2
Type: security-commit

## Details
fix(tower): vote txn tower sync overflow (#9962)

## Patch
### src/choreo/tower/fd_tower_serdes.c
```diff
@@ -204,8 +204,10 @@ fd_txn_parse_simple_vote( fd_txn_t const * txn,
     int err = fd_compact_tower_sync_de( compact_tower_sync_serde, instr_data + sizeof(uint), instr->data_sz - sizeof(uint) );
     if( FD_LIKELY( !err ) ) {
       if( !!opt_vote_slot ) {
-        *opt_vote_slot = compact_tower_sync_serde->root;
-        for( ulong i = 0; i < compact_tower_sync_serde->lockouts_cnt; i++ ) *opt_vote_slot += compact_tower_sync_serde->lockouts[ i ].offset;
+        *opt_vote_slot =  fd_ulong_if( compact_tower_sync_serde->root==ULONG_MAX, 0, compact_tower_sync_serde->root );
+        for( ulong i = 0; i < compact_tower_sync_serde->lockouts_cnt; i++ ) {
+          if( FD_UNLIKELY( __builtin_uaddl_overflow( *opt_vote_slot, compact_tower_sync_serde->lockouts[ i ].offset, opt_vote_slot ) ) ) return 0;
+        }
       }
       fd_pubkey_t const * accs = (fd_pubkey_t const *)fd_type_pun_const( payload + txn->acct_addr_off );
       if( !!opt_vote_acct ) {
```

### src/discof/tower/fd_tower_tile.c
```diff
@@ -778,10 +778,10 @@ count_vote_txn( fd_tower_tile_t * ctx,
 
   int err = fd_compact_tower_sync_de( &ctx->compact_tower_sync_serde, instr_data + sizeof(uint), instr->data_sz - sizeof(uint) );
   if( FD_UNLIKELY( err==-1 ) ) { ctx->metrics.txn_bad_deser++; return; }
-  ulong slot = ctx->compact_tower_sync_serde.root;
+  ulong slot = fd_ulong_if( ctx->compact_tower_sync_serde.root==ULONG_MAX, 0, ctx->compact_tower_sync_serde.root );
   fd_tower_vote_remove_all( ctx->scratch_tower );
   for( ulong i = 0; i < ctx->compact_tower_sync_serde.lockouts_cnt; i++ ) {
-    slot += ctx->compact_tower_sync_serde.lockouts[i].offset;
+    if( FD_UNLIKELY( __builtin_uaddl_overflow( slot, ctx->compact_tower_sync_serde.lockouts[i].offset, &slot ) ) ) { ctx->metrics.txn_bad_deser++; return; };
     fd_tower_vote_push_tail( ctx->scratch_tower, (fd_tower_vote_t){ .slot = slot, .conf = ctx->compact_tower_sync_serde.lockouts[i].confirmation_count } );
   }
 
```
