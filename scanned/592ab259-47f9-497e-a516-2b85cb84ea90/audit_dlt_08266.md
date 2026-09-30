# [?] stake_ci: add return to prevent overflow

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-02-17
Source: https://github.com/firedancer-io/firedancer/commit/0426d3a5eeb6ab2764b4775a565e3405d97f183e
Type: security-commit

## Details
stake_ci: add return to prevent overflow

## Patch
### src/disco/shred/fd_stake_ci.c
```diff
@@ -434,6 +434,7 @@ ci_dest_add_one_unstaked( fd_stake_ci_t *            info,
                           fd_per_epoch_info_t *      ei ) {
   if( fd_shred_dest_cnt_all( ei->sdest )>=MAX_SHRED_DESTS ) {
     FD_LOG_WARNING(( "Too many validators in shred table to add a new validator." ));
+    return;
   }
   ulong cur_cnt = fd_shred_dest_cnt_all( ei->sdest );
   for( ulong i=0UL; i<cur_cnt; i++ ) {
```

### src/disco/shred/test_stake_ci.c
```diff
@@ -814,6 +814,66 @@ test_dest_update( void ) {
   fd_stake_ci_delete( fd_stake_ci_leave( info ) );
 }
 
+static void
+test_dest_update_overflow( void ) {
+  /* Fill the shred dest table to MAX_SHRED_DESTS staked validators,
+     then try to add one more unstaked validator via
+     fd_stake_ci_dest_update.  This exercises ci_dest_add_one_unstaked
+     when the table is already at capacity and should hit the
+     FD_LOG_WARNING. */
+  fd_stake_ci_t * info = fd_stake_ci_join( fd_stake_ci_new( _info, identity_key ) );
+  /* Verify the table contains the identity and is otherwise empty */
+  FD_TEST( fd_shred_dest_cnt_all( info->epoch_info[0].sdest )==1 );
+
+  /* Add MAX_SHRED_DESTS-2 entries*/
+  fd_epoch_info_msg_t *buf = fd_type_pun( epoch_msg );
+  buf->epoch          = 0UL;
+  buf->start_slot     = 0UL;
+  buf->slot_cnt       = SLOTS_PER_EPOCH;
+  buf->staked_cnt     = MAX_SHRED_DESTS - 2UL;
+  buf->excluded_stake = 0UL;
+  buf->vote_keyed_lsched = 0UL;
+  memset( &buf->features, 0, sizeof(fd_features_t) );
+
+  for(ulong i = 0UL; i<buf->staked_cnt; i++ ) {
+    FD_STORE( ulong, buf->weights[i].vote_key.uc, fd_ulong_bswap( i ) );
+    FD_STORE( ulong, buf->weights[i].id_key.uc, fd_ulong_bswap( i ) );
+    buf->weights[i].stake = i+1UL;
+  }
+
+  fd_stake_ci_epoch_msg_init( info, buf );  fd_stake_ci_epoch_msg_fini( info );
+
+  /* Verify the table contains MAX_SHRED_DESTS-1 entries (identity + MAX_SHRED_DESTS-2 staked) */
+  fd_shred_dest_t * sdest = fd_stake_ci_get_sdest_for_slot( info, 0UL );
+  FD_TEST( sdest );
+  FD_TEST( fd_shred_dest_cnt_all( sdest )==MAX_SHRED_DESTS-1UL );
+
+  /* Add another entry */
+  fd_pubkey_t pubkey;
+  memset( pubkey.uc, 0x01, sizeof(fd_pubkey_t) );
+  FD_STORE( ulong, pubkey.uc, fd_ulong_bswap( MAX_SHRED_DESTS-1UL ) );
+  fd_stake_ci_dest_update( info, &pubkey, 0x11111111U, 1111 );
+
+  /* Verify the table is full with MAX_SHRED_DESTS */
+  sdest = fd_stake_ci_get_sdest_for_slot( info, 0UL );
+  FD_TEST( sdest );
+  FD_TEST( fd_shred_dest_cnt_all( sdest )==MAX_SHRED_DESTS );
+
+  /* Try to add a new unstaked validator. This calls
+     ci_dest_add_one_unstaked which should now warn and return early
+     instead of overflowing the array. */
+  fd_pubkey_t new_pubkey;
+  memset( new_pubkey.uc, 0x01, sizeof(fd_pubkey_t) );
+  FD_STORE( ulong, new_pubkey.uc, fd_ulong_bswap( MAX_SHRED_DESTS ) );
+  fd_stake_ci_dest_update( info, &new_pubkey, 0xAABBCCDDU, 7777 );
+
+  /* The table should still be at MAX_SHRED_DESTS (new entry rejected) */
+  sdest = fd_stake_ci_get_sdest_for_slot( info, 0UL );
+  FD_TEST( fd_shred_dest_cnt_all( sdest )==MAX_SHRED_DESTS );
+
+  fd_stake_ci_delete( fd_stake_ci_leave( info ) );
+}
+
 static void
 test_dest_remove( void ) {
   fd_stake_ci_t * info = fd_stake_ci_join( fd_stake_ci_new( _info, identity_key ) );
@@ -933,6 +993,7 @@ main( int     argc,
   test_limits();
   test_set_identity();
   test_dest_update();
+  test_dest_update_overflow();
   test_dest_remove();
 
   FD_LOG_NOTICE(( "pass" ));
```
