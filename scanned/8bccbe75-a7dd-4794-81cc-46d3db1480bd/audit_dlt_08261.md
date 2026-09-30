# [?] runtime: increase vote/stake account bound to be dos resistant (#8955)

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-03-18
Source: https://github.com/firedancer-io/firedancer/commit/eab52c581ffec33c070c262116609a552889b413
Type: security-commit

## Details
runtime: increase vote/stake account bound to be dos resistant (#8955)

## Patch
### src/discof/gossip/fd_gossip_tile.c
```diff
@@ -377,7 +377,7 @@ returnable_frag( fd_gossip_tile_ctx_t * ctx,
       ctx->wfs_peers.total  = 0UL;
       memset( ctx->wfs_active, 0, sizeof(ctx->wfs_active) );
 
-      FD_TEST( manifest->vote_accounts_len<=FD_RUNTIME_MAX_VOTE_ACCOUNTS );
+      FD_TEST( manifest->vote_accounts_len<=40200UL );
       for( ulong i=0UL; i<manifest->vote_accounts_len; i++ ) {
           if( FD_UNLIKELY( manifest->vote_accounts[ i ].stake==0UL ) ) continue;
           ctx->wfs_stake.total += manifest->vote_accounts[ i ].stake;
```

### src/discof/gossip/fd_gossip_tile.h
```diff
@@ -52,20 +52,20 @@ struct fd_gossip_tile_ctx {
   fd_rng_t          rng[ 1 ];
 
 
-  /* FIXME: Get rid of this and use the stake map instead. */
+  /* FIXME: Support a larger bound. */
   /* The condition for complete = 1 is 80% of the cluster has joined
      gossip. "joining gossip" is based on contact info CRDS values
      with a wallclock timestamp in the last 15 seconds.
 
      We keep a copy of the snapshot bank's votes states in an array here
      for quick look up. */
-  fd_vote_stake_weight_t wfs_stakes_scratch[ FD_RUNTIME_MAX_VOTE_ACCOUNTS ];
-  fd_stake_weight_t      wfs_stakes        [ FD_RUNTIME_MAX_VOTE_ACCOUNTS ];
+  fd_vote_stake_weight_t wfs_stakes_scratch[ 40200UL ];
+  fd_stake_weight_t      wfs_stakes        [ 40200UL ];
   ulong                  wfs_stakes_cnt;
 
   /* wfs_active is used to keep track of nodes we've already labeled as
      being active on gossip, so we don't double count their stake. */
-  uchar             wfs_active[ FD_RUNTIME_MAX_VOTE_ACCOUNTS ];
+  uchar             wfs_active[ 40200UL ];
   int               wfs_state;
 
   struct {
```

### src/discof/replay/fd_replay_tile.c
```diff
@@ -469,8 +469,8 @@ struct fd_replay_tile {
 
   uchar __attribute__((aligned(FD_MULTI_EPOCH_LEADERS_ALIGN))) mleaders_mem[ FD_MULTI_EPOCH_LEADERS_FOOTPRINT ];
 
-  ulong              runtime_stack_seed;
-  fd_runtime_stack_t runtime_stack;
+  ulong                runtime_stack_seed;
+  fd_runtime_stack_t * runtime_stack;
 };
 
 typedef struct fd_replay_tile fd_replay_tile_t;
@@ -485,6 +485,7 @@ scratch_footprint( fd_topo_tile_t const * tile ) {
 
   ulong l = FD_LAYOUT_INIT;
   l = FD_LAYOUT_APPEND( l, alignof(fd_replay_tile_t),    sizeof(fd_replay_tile_t) );
+  l = FD_LAYOUT_APPEND( l, fd_runtime_stack_align(),     fd_runtime_stack_footprint( FD_RUNTIME_MAX_VOTE_ACCOUNTS, FD_RUNTIME_EXPECTED_VOTE_ACCOUNTS, FD_RUNTIME_EXPECTED_STAKE_ACCOUNTS ) );
   l = FD_LAYOUT_APPEND( l, alignof(fd_block_id_ele_t),   sizeof(fd_block_id_ele_t) * tile->replay.max_live_slots );
   l = FD_LAYOUT_APPEND( l, fd_block_id_map_align(),      fd_block_id_map_footprint( chain_cnt ) );
   l = FD_LAYOUT_APPEND( l, fd_txncache_align(),          fd_txncache_footprint( tile->replay.max_live_slots ) );
@@ -657,7 +658,7 @@ replay_block_start( fd_replay_tile_t *  ctx,
   fd_bank_block_height_set( bank, fd_bank_block_height_get( bank ) + 1UL );
 
   int is_epoch_boundary = 0;
-  fd_runtime_block_execute_prepare( ctx->banks, bank, ctx->accdb, &ctx->runtime_stack, ctx->capture_ctx, &is_epoch_boundary );
+  fd_runtime_block_execute_prepare( ctx->banks, bank, ctx->accdb, ctx->runtime_stack, ctx->capture_ctx, &is_epoch_boundary );
   if( FD_UNLIKELY( is_epoch_boundary ) ) publish_epoch_info( ctx, stem, bank, 0 );
 
   ulong max_tick_height;
@@ -888,7 +889,7 @@ replay_block_finalize( fd_replay_tile_t *  ctx,
   /* If enabled, dump the block to a file and reset the dumping
      context state */
   if( FD_UNLIKELY( ctx->dump_proto_ctx && ctx->dump_proto_ctx->dump_block_to_pb ) ) {
-    fd_dump_block_to_protobuf( ctx->block_dump_ctx, ctx->banks, bank, ctx->accdb, ctx->dump_proto_ctx, &ctx->runtime_stack );
+    fd_dump_block_to_protobuf( ctx->block_dump_ctx, ctx->banks, bank, ctx->accdb, ctx->dump_proto_ctx, ctx->runtime_stack );
     fd_block_dump_context_reset( ctx->block_dump_ctx );
   }
 # endif
@@ -951,7 +952,7 @@ prepare_leader_bank( fd_replay_tile_t *  ctx,
   fd_bank_block_height_set( ctx->leader_bank, fd_bank_block_height_get( ctx->leader_bank ) + 1UL );
 
   int is_epoch_boundary = 0;
-  fd_runtime_block_execute_prepare( ctx->banks, ctx->leader_bank, ctx->accdb, &ctx->runtime_stack, ctx->capture_ctx, &is_epoch_boundary );
+  fd_runtime_block_execute_prepare( ctx->banks, ctx->leader_bank, ctx->accdb, ctx->runtime_stack, ctx->capture_ctx, &is_epoch_boundary );
   if( FD_UNLIKELY( is_epoch_boundary ) ) publish_epoch_info( ctx, stem, ctx->leader_bank, 0 );
 
   ulong max_tick_height;
@@ -1164,15 +1165,15 @@ init_after_snapshot( fd_replay_tile_t * ctx ) {
   /* After both snapshots have been loaded in, we can determine if we should
      start distributing rewards. */
 
-  fd_rewards_recalculate_partitioned_rewards( ctx->banks, bank, ctx->accdb, &xid, &ctx->runtime_stack, ctx->capture_ctx );
+  fd_rewards_recalculate_partitioned_rewards( ctx->banks, bank, ctx->accdb, &xid, ctx->runtime_stack, ctx->capture_ctx );
 
   ulong snapshot_slot = fd_bank_slot_get( bank );
   if( FD_UNLIKELY( !snapshot_slot ) ) {
     /* Genesis-specific setup. */
     /* FIXME: This branch does not set up a new block exec ctx
        properly. Needs to do whatever prepare_new_block_execution
        does, but just hacking that in breaks stuff. */
-    fd_runtime_update_leaders( bank, &ctx->runtime_stack );
+    fd_runtime_update_leaders( bank, ctx->runtime_stack );
 
     ulong hashcnt_per_slot = fd_bank_hashes_per_tick_get( bank ) * fd_bank_ticks_per_slot_get( bank );
     fd_hash_t * poh = fd_bank_poh_modify( bank );
@@ -1181,7 +1182,7 @@ init_after_snapshot( fd_replay_tile_t * ctx ) {
     }
 
     int is_epoch_boundary = 0;
-    fd_runtime_block_execute_prepare( ctx->banks, bank, ctx->accdb, &ctx->runtime_stack, ctx->capture_ctx, &is_epoch_boundary );
+    fd_runtime_block_execute_prepare( ctx->banks, bank, ctx->accdb, ctx->runtime_stack, ctx->capture_ctx, &is_epoch_boundary );
     FD_TEST( !is_epoch_boundary );
     fd_runtime_block_execute_finalize( bank, ctx->accdb, ctx->capture_ctx );
 
@@ -1427,7 +1428,7 @@ boot_genesis( fd_replay_tile_t *        ctx,
   fd_funk_txn_xid_t root_xid = { .ul = { LONG_MAX, LONG_MAX } };
   fd_funk_txn_xid_t target_xid = { .ul = { 0UL, 0UL } };
   fd_accdb_attach_child( ctx->accdb_admin, &root_xid, &target_xid );
-  fd_runtime_read_genesis( ctx->banks, bank, ctx->accdb, &xid, NULL, &meta->genesis_hash, &meta->lthash, ctx->genesis, genesis_blob, &ctx->runtime_stack );
+  fd_runtime_read_genesis( ctx->banks, bank, ctx->accdb, &xid, NULL, &meta->genesis_hash, &meta->lthash, ctx->genesis, genesis_blob, ctx->runtime_stack );
   fd_accdb_advance_root( ctx->accdb_admin, &target_xid );
 
   static const fd_txncache_fork_id_t txncache_root = { .val = USHORT_MAX };
@@ -1576,7 +1577,7 @@ on_snapshot_message( fd_replay_tile_t *  ctx,
     fd_sched_block_add_done( ctx->sched, bank->data->idx, ULONG_MAX, snapshot_slot );
     FD_TEST( bank->data->idx==0UL );
 
-    fd_runtime_update_leaders( bank, &ctx->runtime_stack );
+    fd_runtime_update_leaders( bank, ctx->runtime_stack );
 
     /* Typically, when we cross an epoch boundary during normal
        operation, we publish the stake weights for the new epoch.  But
@@ -1631,7 +1632,7 @@ on_snapshot_message( fd_replay_tile_t *  ctx,
       fd_ssload_recover( fd_chunk_to_laddr( ctx->in[ in_idx ].mem, chunk ),
                          ctx->banks,
                          fd_banks_bank_query( bank, ctx->banks, FD_REPLAY_BOOT_BANK_IDX ),
-                         &ctx->runtime_stack,
+                         ctx->runtime_stack,
                          msg==FD_SSMSG_MANIFEST_INCREMENTAL );
 
       fd_snapshot_manifest_t const * manifest = fd_chunk_to_laddr( ctx->in[ in_idx ].mem, chunk );
@@ -2804,6 +2805,7 @@ unprivileged_init( fd_topo_t *      topo,
 
   FD_SCRATCH_ALLOC_INIT( l, scratch );
   fd_replay_tile_t * ctx    = FD_SCRATCH_ALLOC_APPEND( l, alignof(fd_replay_tile_t),   sizeof(fd_replay_tile_t) );
+  void * runtime_stack_mem  = FD_SCRATCH_ALLOC_APPEND( l, fd_runtime_stack_align(),    fd_runtime_stack_footprint( FD_RUNTIME_MAX_VOTE_ACCOUNTS, FD_RUNTIME_EXPECTED_VOTE_ACCOUNTS, FD_RUNTIME_EXPECTED_STAKE_ACCOUNTS ) );
   void * block_id_arr_mem   = FD_SCRATCH_ALLOC_APPEND( l, alignof(fd_block_id_ele_t),  sizeof(fd_block_id_ele_t) * tile->replay.max_live_slots );
   void * block_id_map_mem   = FD_SCRATCH_ALLOC_APPEND( l, fd_block_id_map_align(),     fd_block_id_map_footprint( chain_cnt ) );
   void * _txncache          = FD_SCRATCH_ALLOC_APPEND( l, fd_txncache_align(),         fd_txncache_footprint( tile->replay.max_live_slots ) );
@@ -2820,7 +2822,8 @@ unprivileged_init( fd_topo_t *      topo,
   }
 # endif
 
-  FD_TEST( fd_vote_rewards_map_join( fd_vote_rewards_map_new( ctx->runtime_stack.stakes.vote_map_mem, FD_RUNTIME_EXPECTED_VOTE_ACCOUNTS, ctx->runtime_stack_seed ) ) );
+  ctx->runtime_stack = fd_runtime_stack_join( fd_runtime_stack_new( runtime_stack_mem, FD_RUNTIME_MAX_VOTE_ACCOUNTS, FD_RUNTIME_EXPECTED_VOTE_ACCOUNTS, FD_RUNTIME_EXPECTED_STAKE_ACCOUNTS, ctx->runtime_stack_seed ) );
+  FD_TEST( ctx->runtime_stack );
 
   ctx->wksp = topo->workspaces[ topo->objs[ tile->tile_obj_id ].wksp_id ].wksp;
 
```

### src/discof/restore/utils/fd_ssload.c
```diff
@@ -190,7 +190,7 @@ fd_ssload_recover( fd_snapshot_manifest_t * manifest,
     if( FD_UNLIKELY( elem->stake_delegation==0UL ) ) {
       continue;
     }
-    fd_stake_delegations_update(
+    fd_stake_delegations_root_update(
         stake_delegations,
         (fd_pubkey_t *)elem->stake_pubkey,
         (fd_pubkey_t *)elem->vote_pubkey,
@@ -247,11 +247,15 @@ fd_ssload_recover( fd_snapshot_manifest_t * manifest,
         elem->stake,
         fd_bank_epoch_get( bank ) );
 
-    vote_ele->epoch_credits.cnt = elem->epoch_credits_history_len;
-    for( ulong j=0UL; j<elem->epoch_credits_history_len; j++ ) {
-      vote_ele->epoch_credits.epoch[ j ]        = (ushort)elem->epoch_credits[ j ].epoch;
-      vote_ele->epoch_credits.credits[ j ]      = elem->epoch_credits[ j ].credits;
-      vote_ele->epoch_credits.prev_credits[ j ] = elem->epoch_credits[ j ].prev_credits;
+    if( i<runtime_stack->expected_vote_accounts ) {
+      runtime_stack->stakes.epoch_credits[i].cnt = elem->epoch_credits_history_len;
+      for( ulong j=0UL; j<elem->epoch_credits_history_len; j++ ) {
+        runtime_stack->stakes.epoch_credits[ i ].epoch[ j ]        = (ushort)elem->epoch_credits[ j ].epoch;
+        runtime_stack->stakes.epoch_credits[ i ].credits[ j ]      = elem->epoch_credits[ j ].credits;
+        runtime_stack->stakes.epoch_credits[ i ].prev_credits[ j ] = elem->epoch_credits[ j ].prev_credits;
+      }
+    } else {
+      FD_LOG_ERR(( "snapshot loading currently does not support more than %lu vote accounts, %lu", runtime_stack->expected_vote_accounts, manifest->epoch_stakes[1].vote_stakes_len ));
     }
   }
 
```

### src/discof/restore/utils/fd_ssmsg.h
```diff
@@ -147,9 +147,10 @@ struct fd_snapshot_manifest_epoch_stakes {
   /* The total amount of active stake at the end of the given epoch.*/
   ulong                              total_stake;
 
-  /* The vote accounts and their stakes for a given epoch. */
+  /* The vote accounts and their stakes for a given epoch.
+     FIXME: Snapshot manifest has to support a much larger bound. */
   ulong                              vote_stakes_len;
-  fd_snapshot_manifest_vote_stakes_t vote_stakes[ FD_RUNTIME_MAX_VOTE_ACCOUNTS ];
+  fd_snapshot_manifest_vote_stakes_t vote_stakes[ 40200UL ];
 };
 
 typedef struct fd_snapshot_manifest_epoch_stakes fd_snapshot_manifest_epoch_stakes_t;
@@ -454,12 +455,14 @@ struct fd_snapshot_manifest {
      epoch in the slots immediately after the epoch boundary.  These
      vote and stake rewards are calculated as a stake-weighted
      percentage of the inflation rewards for the epoch and validator
-     uptime, which is measured by vote account vote credits. */
+     uptime, which is measured by vote account vote credits.
+     FIXME: Make this unbounded or support a much larger bound. */
   ulong                               vote_accounts_len;
-  fd_snapshot_manifest_vote_account_t vote_accounts[ FD_RUNTIME_MAX_VOTE_ACCOUNTS ];
+  fd_snapshot_manifest_vote_account_t vote_accounts[ 40200UL ];
 
+  /* FIXME: Make this unbounded or support a much larger bound. */
   ulong stake_delegations_len;
-  fd_snapshot_manifest_stake_delegation_t stake_delegations[ FD_RUNTIME_MAX_STAKE_ACCOUNTS ];
+  fd_snapshot_manifest_stake_delegation_t stake_delegations[ 3000000UL ];
 
   /* Epoch stakes represent the exact amount staked to each vote
      account at the beginning of the previous epoch. They are
```

### src/flamenco/leaders/fd_leaders.h
```diff
@@ -53,13 +53,6 @@
 
 #define FD_EPOCH_SLOTS_PER_ROTATION (4UL)
 
-/* FD_EPOCH_LEADERS_MAX_FOOTPRINT is the maximum footprint of a leader
-   schedule object that the runtime can support given a constant
-   slots per epoch (432K) and a max number of vote accounts (108000).
-   FIXME: This needs to be bumped up */
-
-#define FD_EPOCH_LEADERS_MAX_FOOTPRINT (FD_EPOCH_LEADERS_FOOTPRINT(FD_RUNTIME_MAX_VOTE_ACCOUNTS, FD_RUNTIME_SLOTS_PER_EPOCH))
-
 /* fd_epoch_leaders_t contains the leader schedule of a Solana epoch. */
 
 struct fd_epoch_leaders {
```

### src/flamenco/rewards/fd_rewards.c
```diff
@@ -85,23 +85,66 @@ slot_in_year_for_inflation( fd_bank_t const * bank ) {
   return (double)num_slots / (double)fd_bank_slots_per_year_get( bank );
 }
 
+
+static void
+get_credits( uchar const *       account_data,
+             ulong               account_data_len,
+             uchar *             buf,
+             fd_epoch_credits_t * epoch_credits ) {
+
+  fd_bincode_decode_ctx_t ctx = {
+    .data    = account_data,
+    .dataend = account_data + account_data_len,
+  };
+
+  fd_vote_state_versioned_t * vsv = fd_vote_state_versioned_decode( buf, &ctx );
+  if( FD_UNLIKELY( vsv==NULL ) ) {
+    FD_LOG_CRIT(( "unable to decode vote state versioned" ));
+  }
+
+  fd_vote_epoch_credits_t * vote_credits = NULL;
+
+  switch( vsv->discriminant ) {
+  case fd_vote_state_versioned_enum_v1_14_11:
+    vote_credits = vsv->inner.v1_14_11.epoch_credits;
+    break;
+  case fd_vote_state_versioned_enum_v3:
+    vote_credits = vsv->inner.v3.epoch_credits;
+    break;
+  case fd_vote_state_versioned_enum_v4:
+    vote_credits = vsv->inner.v4.epoch_credits;
+    break;
+  default:
+    FD_LOG_CRIT(( "invalid vote state version %u", vsv->discriminant ));
+  }
+
+  epoch_credits->cnt = 0UL;
+  for( deq_fd_vote_epoch_credits_t_iter_t iter = deq_fd_vote_epoch_credits_t_iter_init( vote_credits );
+       !deq_fd_vote_epoch_credits_t_iter_done( vote_credits, iter );
+       iter = deq_fd_vote_epoch_credits_t_iter_next( vote_credits, iter ) ) {
+    fd_vote_epoch_credits_t * ele = deq_fd_vote_epoch_credits_t_iter_ele( vote_credits, iter );
+    epoch_credits->epoch[ epoch_credits->cnt ]        = (ushort)ele->epoch;
+    epoch_credits->credits[ epoch_credits->cnt ]      = ele->credits;
+    epoch_credits->prev_credits[ epoch_credits->cnt ] = ele->prev_credits;
+    epoch_credits->cnt++;
+  }
+}
+
 /* For a given stake and vote_state, calculate how many points were earned (credits * stake) and new value
    for credits_observed were the points paid
 
     https://github.com/anza-xyz/agave/blob/cbc8320d35358da14d79ebcada4dfb6756ffac79/programs/stake/src/points.rs#L109 */
 static void
-calculate_stake_points_and_credits( fd_stake_history_t const *     stake_history,
+calculate_stake_points_and_credits( fd_epoch_credits_t *           epoch_credits,
+                                    fd_stake_history_t const *     stake_history,
                                     fd_stake_delegation_t const *  stake,
-                                    fd_runtime_stack_t *           runtime_stack,
-                                    ulong                          vote_state_idx,
                                     ulong *                        new_rate_activation_epoch,
                                     fd_calculated_stake_points_t * result ) {
 
-  fd_vote_rewards_t * vote_ele = &runtime_stack->stakes.vote_ele[ vote_state_idx ];
-
   ulong credits_in_stake = stake->credits_observed;
-  ulong credits_cnt      = vote_ele->epoch_credits.cnt;
-  ulong credits_in_vote  = credits_cnt > 0UL ? vote_ele->epoch_credits.credits[ credits_cnt - 1UL ] : 0UL;
+  ulong credits_cnt      = epoch_credits->cnt;
+  ulong credits_in_vote  = credits_cnt > 0UL ? epoch_credits->credits[ credits_cnt - 1UL ] : 0UL;
+
 
   /* If the Vote account has less credits observed than the Stake account,
       something is wrong and we need to force an update.
@@ -128,10 +171,10 @@ calculate_stake_points_and_credits( fd_stake_history_t const *     stake_history
   /* Calculate the points for each epoch credit */
   uint128 points               = 0;
   ulong   new_credits_observed = credits_in_stake;
-  for( ulong i=0UL; i<vote_ele->epoch_credits.cnt; i++ ) {
+  for( ulong i=0UL; i<epoch_credits->cnt; i++ ) {
 
-    ulong final_epoch_credits   = vote_ele->epoch_credits.credits[ i ];
-    ulong initial_epoch_credits = vote_ele->epoch_credits.prev_credits[ i ];
+    ulong final_epoch_credits   = epoch_credits->credits[ i ];
+    ulong initial_epoch_credits = epoch_credits->prev_credits[ i ];
     uint128 earned_credits = 0;
     if( FD_LIKELY( credits_in_stake < initial_epoch_credits ) ) {
       earned_credits = (uint128)(final_epoch_credits - initial_epoch_credits);
@@ -143,7 +186,7 @@ calculate_stake_points_and_credits( fd_stake_history_t const *     stake_history
 
     ulong stake_amount = fd_stakes_activating_and_deactivating(
         stake,
-        vote_ele->epoch_credits.epoch[ i ],
+        epoch_credits->epoch[ i ],
         stake_history,
         new_rate_activation_epoch ).effective;
 
@@ -338,7 +381,9 @@ get_minimum_stake_delegation( fd_bank_t * bank ) {
 /* Calculates epoch reward points from stake/vote accounts.
    https://github.com/anza-xyz/agave/blob/v2.3.1/runtime/src/bank/partitioned_epoch_rewards/calculation.rs#L445 */
 static uint128
-calculate_reward_points_partitioned( fd_bank_t *                    bank,
+calculate_reward_points_partitioned( fd_accdb_user_t *              accdb,
+                                     fd_funk_txn_xid_t const *      xid,
+                                     fd_bank_t *                    bank,
                                      fd_stake_delegations_t const * stake_delegations,
                                      fd_stake_history_t const *     stake_history,
                                      fd_runtime_stack_t *           runtime_stack ) {
@@ -366,7 +411,8 @@ calculate_reward_points_partitioned( fd_bank_t *                    bank,
   for( fd_stake_delegations_iter_t * iter = fd_stake_delegations_iter_init( iter_, stake_delegations );
        !fd_stake_delegations_iter_done( iter );
        fd_stake_delegations_iter_next( iter ) ) {
-    fd_stake_delegation_t const * stake_delegation = fd_stake_delegations_iter_ele( iter );
+    fd_stake_delegation_t const * stake_delegation     = fd_stake_delegations_iter_ele( iter );
+    ulong                         stake_delegation_idx = fd_stake_delegations_iter_idx( iter );
 
     if( FD_UNLIKELY( stake_delegation->stake<minimum_stake_delegation ) ) {
       continue;
@@ -377,16 +423,30 @@ calculate_reward_points_partitioned( fd_bank_t *                    bank,
 
     fd_calculated_stake_points_t   stake_points_result_[1];
     fd_calculated_stake_points_t * stake_points_result;
-    if( FD_UNLIKELY( stake_delegation->idx>=FD_RUNTIME_EXPECTED_STAKE_ACCOUNTS ) ) {
+    if( FD_UNLIKELY( stake_delegation_idx>=runtime_stack->expected_stake_accounts ) ) {
       stake_points_result = stake_points_result_;
     } else {
-      stake_points_result = &runtime_stack->stakes.stake_points_result[ stake_delegation->idx ];
+      stake_points_result = &runtime_stack->stakes.stake_points_result[ stake_delegation_idx ];
+    }
+
+    fd_epoch_credits_t   epoch_credits_;
+    fd_epoch_credits_t * epoch_credits = NULL;
+    if( idx>=runtime_stack->expected_vote_accounts ) {
+      fd_vote_rewards_t * vote_ele = &runtime_stack->stakes.vote_ele[ idx ];
+      fd_accdb_ro_t vote_ro[1];
+      FD_TEST( fd_accdb_open_ro( accdb, vote_ro, xid, &vote_ele->pubkey ) );
+
+      uchar __attribute__((aligned(128))) vsv_buf[ FD_VOTE_STATE_VERSIONED_FOOTPRINT ];
+      get_credits( fd_accdb_ref_data_const( vote_ro ), fd_accdb_ref_data_sz( vote_ro ), vsv_buf, &epoch_credits_ );
+      fd_accdb_close_ro( accdb, vote_ro );
+      epoch_credits = &epoch_credits_;
+    } else {
+      epoch_credits = &runtime_stack->stakes.epoch_credits[ idx ];
     }
 
-    calculate_stake_points_and_credits( stake_history,
+    calculate_stake_points_and_credits( epoch_credits,
+                                        stake_history,
                                         stake_delegation,
-                                        runtime_stack,
-                                        idx,
                                         new_warmup_cooldown_rate_epoch,
                                         stake_points_result );
 
@@ -413,7 +473,9 @@ calculate_reward_points_partitioned( fd_bank_t *                    bank,
 
    https://github.com/anza-xyz/agave/blob/v2.3.1/runtime/src/bank/partitioned_epoch_rewards/calculation.rs#L323 */
 static void
-calculate_stake_vote_rewards( fd_bank_t *                    bank,
+calculate_stake_vote_rewards( fd_accdb_user_t *              accdb,
+                              fd_funk_txn_xid_t const *      xid,
+                              fd_bank_t *                    bank,
                               fd_stake_delegations_t const * stake_delegations,
                               fd_capture_ctx_t *             capture_ctx FD_PARAM_UNUSED,
                               fd_stake_history_t const *     stake_history,
@@ -441,11 +503,14 @@ calculate_stake_vote_rewards( fd_bank_t *                    bank,
 
   fd_calculated_stake_rewards_t calculated_stake_rewards_[1];
 
+  uchar __attribute__((aligned(128))) vsv_buf[ FD_VOTE_STATE_VERSIONED_FOOTPRINT ];
+
   fd_stake_delegations_iter_t iter_[1];
   for( fd_stake_delegations_iter_t * iter = fd_stake_delegations_iter_init( iter_, stake_delegations );
        !fd_stake_delegations_iter_done( iter );
        fd_stake_delegations_iter_next( iter ) ) {
-    fd_stake_delegation_t const * stake_delegation = fd_stake_delegations_iter_ele( iter );
+    fd_stake_delegation_t const * stake_delegation     = fd_stake_delegations_iter_ele( iter );
+    ulong                         stake_delegation_idx = fd_stake_delegations_iter_idx( iter );
 
     if( FD_FEATURE_ACTIVE_BANK( bank, stake_minimum_delegation_for_rewards ) ) {
       if( stake_delegation->stake<minimum_stake_delegation ) {
@@ -454,10 +519,10 @@ calculate_stake_vote_rewards( fd_bank_t *                    bank,
     }
 
     fd_calculated_stake_rewards_t * calculated_stake_rewards = NULL;
-    if( stake_delegation->idx>=FD_RUNTIME_EXPECTED_STAKE_ACCOUNTS ) {
+    if( stake_delegation_idx>=runtime_stack->expected_stake_accounts ) {
       calculated_stake_rewards = calculated_stake_rewards_;
     } else {
-      calculated_stake_rewards = &runtime_stack->stakes.stake_rewards_result[ stake_delegation->idx ];
+      calculated_stake_rewards = &runtime_stack->stakes.stake_rewards_result[ stake_delegation_idx ];
     }
     calculated_stake_rewards->success = 0;
 
@@ -468,19 +533,32 @@ calculate_stake_vote_rewards( fd_bank_t *                    bank,
 
     fd_calculated_stake_points_t   stake_points_result_[1];
     fd_calculated_stake_points_t * stake_points_result;
-    if( is_recalculation || FD_UNLIKELY( stake_delegation->idx>=FD_RUNTIME_EXPECTED_STAKE_ACCOUNTS ) ) {
+    if( is_recalculation || FD_UNLIKELY( stake_delegation_idx>=runtime_stack->expected_stake_accounts ) ) {
+      fd_vote_rewards_t * vote_ele = &runtime_stack->stakes.vote_ele[ idx ];
+
+      fd_epoch_credits_t   epoch_credits_;
+      fd_epoch_credits_t * epoch_credits = NULL;
+      if( idx<runtime_stack->expected_vote_accounts ) {
+        epoch_credits = &runtime_stack->stakes.epoch_credits[ idx ];
+      } else {
+        fd_accdb_ro_t vote_ro[1];
+        FD_TEST( fd_accdb_open_ro( accdb, vote_ro, xid, &vote_ele->pubkey ) );
+        get_credits( fd_accdb_ref_data_const( vote_ro ), fd_accdb_ref_data_sz( vote_ro ), vsv_buf, &epoch_credits_ );
+        fd_accdb_close_ro( accdb, vote_ro );
+        epoch_credits = &epoch_credits_;
+      }
+
       /* We have not cached the stake points yet if we are recalculating
          stake rewards so we need to recalculate them. */
       calculate_stake_points_and_credits(
+          epoch_credits,
           stake_history,
           stake_delegation,
-          runtime_stack,
-          idx,
           new_warmup_cooldown_rate_epoch,
           stake_points_result_ );
       stake_points_result = stake_points_result_;
     } else {
-      stake_points_result = &runtime_stack->stakes.stake_points_result[ stake_delegation->idx ];
+      stake_points_result = &runtime_stack->stakes.stake_points_result[ stake_delegation_idx ];
     }
 
     /* redeem_rewards is actually just responsible for calculating the
@@ -520,7 +598,9 @@ calculate_stake_vote_rewards( fd_bank_t *                    bank,
 }
 
 static void
-setup_stake_partitions( fd_bank_t *                    bank,
+setup_stake_partitions( fd_accdb_user_t *              accdb,
+                        fd_funk_txn_xid_t const *      xid,
+                        fd_bank_t *                    bank,
                         fd_stake_history_t const *     stake_history,
                         fd_stake_delegations_t const * stake_delegations,
                         fd_runtime_stack_t *           runtime_stack,
@@ -535,16 +615,19 @@ setup_stake_partitions( fd_bank_t *                    bank,
   uchar fork_idx = fd_stake_rewards_init( stake_rewards, fd_bank_epoch_get( bank ), parent_blockhash, starting_block_height, (uint)num_partitions );
   bank->data->stake_rewards_fork_id = fork_idx;
 
+  uchar __attribute__((aligned(128))) vsv_buf[ FD_VOTE_STATE_VERSIONED_FOOTPRINT ];
+
   fd_stake_delegations_iter_t iter_[1];
   for( fd_stake_delegations_iter_t * iter = fd_stake_delegations_iter_init( iter_, stake_delegations );
        !fd_stake_delegations_iter_done( iter );
        fd_stake_delegations_iter_next( iter ) ) {
-    fd_stake_delegation_t const * stake_delegation = fd_stake_delegations_iter_ele( iter );
+    fd_stake_delegation_t const * stake_delegation     = fd_stake_delegations_iter_ele( iter );
+    ulong                         stake_delegation_idx = fd_stake_delegations_iter_idx( iter );
 
     fd_calculated_stake_rewards_t calculated_stake_rewards_[1];
     fd_calculated_stake_rewards_t * calculated_stake_rewards = NULL;
 
-    if( FD_UNLIKELY( stake_delegation->idx>=FD_RUNTIME_EXPECTED_STAKE_ACCOUNTS ) ) {
+    if( FD_UNLIKELY( stake_delegation_idx>=runtime_stack->expected_stake_accounts ) ) {
 
       calculated_stake_rewards = calculated_stake_rewards_;
 
@@ -565,12 +648,24 @@ setup_stake_partitions( fd_bank_t *                    bank,
         new_warmup_cooldown_rate_epoch = NULL;
       }
 
+      fd_epoch_credits_t   epoch_credits_;
+      fd_epoch_credits_t * epoch_credits = NULL;
+      if( idx>=runtime_stack->expected_vote_accounts ) {
+        fd_vote_rewards_t * vote_ele = &runtime_stack->stakes.vote_ele[ idx ];
+        fd_accdb_ro_t vote_ro[1];
+        FD_TEST( fd_accdb_open_ro( accdb, vote_ro, xid, &vote_ele->pubkey ) );
+        get_credits( fd_accdb_ref_data_const( vote_ro ), fd_accdb_ref_data_sz( vote_ro ), vsv_buf, &epoch_credits_ );
+        fd_accdb_close_ro( accdb, vote_ro );
+        epoch_credits = &epoch_credits_;
+      } else {
+        epoch_credits = &runtime_stack->stakes.epoch_credits[ idx ];
+      }
+
       fd_calculated_stake_points_t stake_points_result[1];
       calculate_stake_points_and_credits(
+          epoch_credits,
           stake_history,
           stake_delegation,
-          runtime_stack,
-          idx,
           new_warmup_cooldown_rate_epoch,
           stake_points_result );
 
@@ -588,7 +683,7 @@ setup_stake_partitions( fd_bank_t *                    bank,
           calculated_stake_rewards );
       calculated_stake_rewards->success = err==0;
     } else {
-      calculated_stake_rewards = &runtime_stack->stakes.stake_rewards_result[ stake_delegation->idx ];
+      calculated_stake_rewards = &runtime_stack->stakes.stake_rewards_result[ stake_delegation_idx ];
     }
 
     if( FD_UNLIKELY( !calculated_stake_rewards->success ) ) continue;
@@ -623,6 +718,8 @@ calculate_validator_rewards( fd_bank_t *                    bank,
 
   /* Calculate the epoch reward points from stake/vote accounts */
   uint128 total_points = calculate_reward_points_partitioned(
+      accdb,
+      xid,
       bank,
       stake_delegations,
       stake_history,
@@ -645,6 +742,8 @@ calculate_validator_rewards( fd_bank_t *                    bank,
   /* Calculate the stake and vote rewards for each account. We want to
      use the vote states from the end of the current_epoch. */
   calculate_stake_vote_rewards(
+      accdb,
+      xid,
       bank,
       stake_delegations,
       capture_ctx,
@@ -662,6 +761,8 @@ calculate_validator_rewards( fd_bank_t *                    bank,
                                                                                 runtime_stack->stakes.stake_rewards_cnt );
 
   setup_stake_partitions(
+      accdb,
+      xid,
       bank,
       stake_history,
       stake_delegations,
@@ -836,17 +937,16 @@ distribute_epoch_reward_to_stake_acc( fd_bank_t *               bank,
   stake_state->inner.stake.stake.delegation.stake = fd_ulong_sat_add( stake_state->inner.stake.stake.delegation.stake,
                                                                       reward_lamports );
 
-  fd_stake_delegations_delta_t * stake_delegations_delta = fd_bank_stake_delegations_delta_locking_modify( bank );
-  fd_stake_delegations_delta_update( stake_delegations_delta,
-                                     bank->data->stake_delegations_fork_id,
-                                     stake_pubkey,
-                                     &stake_state->inner.stake.stake.delegation.voter_pubkey,
-                                     stake_state->inner.stake.stake.delegation.stake,
-                                     stake_state->inner.stake.stake.delegation.activation_epoch,
-                                     stake_state->inner.stake.stake.delegation.deactivation_epoch,
-                                     stake_state->inner.stake.stake.credits_observed,
-                                     stake_state->inner.stake.stake.delegation.warmup_cooldown_rate );
-  fd_bank_stake_delegations_delta_end_locking_modify( bank );
+  fd_stake_delegations_t * stake_delegations_upd = fd_bank_stake_delegations_modify( bank );
+  fd_stake_delegations_fork_update( stake_delegations_upd,
+                                    bank->data->stake_delegations_fork_id,
+                                    stake_pubkey,
+                                    &stake_state->inner.stake.stake.delegation.voter_pubkey,
+                                    stake_state->inner.stake.stake.delegation.stake,
+                                    stake_state->inner.stake.stake.delegation.activation_epoch,
+                                    stake_state->inner.stake.stake.delegation.deactivation_epoch,
+                                    stake_state->inner.stake.stake.credits_observed,
+                                    stake_state->inner.stake.stake.delegation.warmup_cooldown_rate );
 
   if( capture_ctx && capture_ctx->capture_solcap ) {
     fd_capture_link_write_stake_account_payout( capture_ctx,
@@ -1059,6 +1159,8 @@ fd_rewards_recalculate_partitioned_rewards( fd_banks_t *              banks,
   }
 
   calculate_stake_vote_rewards(
+      accdb,
+      xid,
       bank,
       stake_delegations,
       capture_ctx,
@@ -1070,6 +1172,8 @@ fd_rewards_recalculate_partitioned_rewards( fd_banks_t *              banks,
       1 );
 
   setup_stake_partitions(
+      accdb,
+      xid,
       bank,
       stake_history,
       stake_delegations,
@@ -1080,4 +1184,6 @@ fd_rewards_recalculate_partitioned_rewards( fd_banks_t *              banks,
       rewarded_epoch,
       epoch_rewards_sysvar->total_rewards,
       epoch_rewards_sysvar->total_points.ud );
+
+  fd_bank_stake_delegations_end_frontier_query( banks, bank );
 }
```

### src/flamenco/rewards/fd_stake_rewards.c
```diff
@@ -26,12 +26,6 @@ struct index_ele {
 };
 typedef struct index_ele index_ele_t;
 
-#define POOL_NAME  index_pool
-#define POOL_T     index_ele_t
-#define POOL_NEXT  next
-#define POOL_IDX_T uint
-#include "../../util/tmpl/fd_pool.c"
-
 #define MAP_NAME               index_map
 #define MAP_KEY_T              index_key_t
 #define MAP_ELE_T              index_ele_t
@@ -124,7 +118,7 @@ fd_stake_rewards_footprint( ulong max_stake_accounts,
   ulong l = FD_LAYOUT_INIT;
   l  = FD_LAYOUT_APPEND( l, fd_stake_rewards_align(),  sizeof(fd_stake_rewards_t) );
   l =  FD_LAYOUT_APPEND( l, fork_pool_align(),         fork_pool_footprint( max_fork_width ) );
-  l  = FD_LAYOUT_APPEND( l, index_pool_align(),        index_pool_footprint( max_stake_accounts ) );
+  l  = FD_LAYOUT_APPEND( l, alignof(index_ele_t),      sizeof(index_ele_t) * max_stake_accounts );
   l  = FD_LAYOUT_APPEND( l, index_map_align(),         index_map_footprint( map_chain_cnt ) );
   l  = FD_LAYOUT_APPEND( l, alignof(partition_ele_t),  max_fork_width * max_stake_accounts * sizeof(partition_ele_t) );
 
@@ -154,7 +148,7 @@ fd_stake_rewards_new( void * shmem,
   FD_SCRATCH_ALLOC_INIT( l, shmem );
   fd_stake_rewards_t * stake_rewards  = FD_SCRATCH_ALLOC_APPEND( l, fd_stake_rewards_align(), sizeof(fd_stake_rewards_t) );
   void *               fork_pool_mem  = FD_SCRATCH_ALLOC_APPEND( l, fork_pool_align(),        fork_pool_footprint( max_fork_width ) );
-  void *               index_pool_mem = FD_SCRATCH_ALLOC_APPEND( l, index_pool_align(),       index_pool_footprint( max_stake_accounts ) );
+  void *               index_pool_mem = FD_SCRATCH_ALLOC_APPEND( l, alignof(index_ele_t),     sizeof(index_ele_t) * max_stake_accounts );
   void *               index_map_mem  = FD_SCRATCH_ALLOC_APPEND( l, index_map_align(),        index_map_footprint( map_chain_cnt ) );
   void *               partitions_mem = FD_SCRATCH_ALLOC_APPEND( l, alignof(partition_ele_t), max_fork_width * max_stake_accounts * sizeof(partition_ele_t) );
 
@@ -165,12 +159,7 @@ fd_stake_rewards_new( void * shmem,
   }
   stake_rewards->fork_pool_offset = (ulong)fork_pool - (ulong)shmem;
 
-  index_ele_t * index_pool = index_pool_join( index_pool_new( index_pool_mem, max_stake_accounts ) );
-  if( FD_UNLIKELY( !index_pool ) ) {
-    FD_LOG_WARNING(( "Failed to create index pool" ));
-    return NULL;
-  }
-  stake_rewards->index_pool_offset = (ulong)index_pool - (ulong)shmem;
+  stake_rewards->index_pool_offset = (ulong)index_pool_mem - (ulong)shmem;
 
   index_map_t * index_map = index_map_join( index_map_new( index_map_mem, map_chain_cnt, seed ) );
   if( FD_UNLIKELY( !index_map ) ) {
@@ -181,6 +170,7 @@ fd_stake_rewards_new( void * shmem,
   stake_rewards->partitions_offset  = (ulong)partitions_mem - (ulong)shmem;
   stake_rewards->max_stake_accounts = max_stake_accounts;
   stake_rewards->epoch              = ULONG_MAX;
+  stake_rewards->total_ele_used     = 0UL;
 
   FD_COMPILER_MFENCE();
   FD_VOLATILE( stake_rewards->magic ) = FD_STAKE_REWARDS_MAGIC;
@@ -215,17 +205,16 @@ fd_stake_rewards_init( fd_stake_rewards_t * stake_rewards,
                        fd_hash_t const *    parent_blockhash,
                        ulong                starting_block_height,
                        uint                 partitions_cnt ) {
-  index_map_t * index_map  = get_index_map( stake_rewards );
-  index_ele_t * index_pool = get_index_pool( stake_rewards );
-  fork_t *      fork_pool  = get_fork_pool( stake_rewards );
+  index_map_t * index_map = get_index_map( stake_rewards );
+  fork_t *      fork_pool = get_fork_pool( stake_rewards );
 
   /* If this is the first reference to the stake rewards, we need to
      reset the backing map and pool all the forks will share. */
   if( FD_LIKELY( stake_rewards->epoch!=epoch ) ) {
     fork_pool_reset( fork_pool );
     index_map_reset( index_map );
-    index_pool_reset( index_pool );
-    stake_rewards->epoch = epoch;
+    stake_rewards->epoch          = epoch;
+    stake_rewards->total_ele_used = 0UL;
   }
 
   uchar fork_idx = (uchar)fork_pool_idx_acquire( fork_pool );
@@ -258,12 +247,13 @@ fd_stake_rewards_insert( fd_stake_rewards_t * stake_rewards,
   };
 
   uint index = (uint)index_map_idx_query( index_map, &index_key, UINT_MAX, index_ele );
-  if( FD_UNLIKELY( index==UINT_MAX ) ) {
-    if( FD_UNLIKELY( index_pool_free( index_ele )==0UL ) ) {
-      FD_LOG_CRIT(( "invariant violation: index_pool_free( index_ele )==0UL" ));
+  if( FD_LIKELY( index==UINT_MAX ) ) {
+    index = stake_rewards->total_ele_used;
+    stake_rewards->total_ele_used++;
+    if( FD_UNLIKELY( index>=stake_rewards->max_stake_accounts ) ) {
+      FD_LOG_CRIT(( "invariant violation: index>=stake_rewards->max_stake_accounts" ));
     }
-    index = (uint)index_pool_idx_acquire( index_ele );
-    index_ele_t * ele = index_pool_ele( index_ele, index );
+    index_ele_t * ele = (index_ele_t *)index_ele + index;
     ele->index_key = index_key;
     index_map_ele_insert( index_map, ele, index_ele );
   }
@@ -329,7 +319,8 @@ fd_stake_rewards_iter_ele( fd_stake_rewards_t * stake_rewards,
                            ulong *              lamports_out,
                            ulong *              credits_observed_out ) {
   partition_ele_t * partition_ele = get_partition_ele( stake_rewards, fork_idx, stake_rewards->iter_curr_fork_idx );
-  index_ele_t * index_ele = index_pool_ele( get_index_pool( stake_rewards ), partition_ele->index );
+
+  index_ele_t * index_ele = get_index_pool( stake_rewards ) + partition_ele->index;
   *pubkey_out = index_ele->index_key.pubkey;
   *lamports_out = index_ele->index_key.lamports;
   *credits_observed_out = index_ele->index_key.credits_observed;
```

### src/flamenco/runtime/fd_bank.c
```diff
@@ -29,14 +29,14 @@ fd_bank_epoch_leaders_query( fd_bank_t const * bank ) {
   if( FD_UNLIKELY( bank->data->epoch_leaders_idx==ULONG_MAX ) ) {
     return NULL;
   }
-  return (fd_epoch_leaders_t const *)fd_type_pun( fd_bank_get_epoch_leaders( bank->data ) + bank->data->epoch_leaders_idx * FD_EPOCH_LEADERS_MAX_FOOTPRINT );
+  return (fd_epoch_leaders_t const *)fd_type_pun( fd_bank_get_epoch_leaders( bank->data ) + bank->data->epoch_leaders_idx * bank->data->epoch_leaders_footprint );
 }
 
 fd_epoch_leaders_t *
 fd_bank_epoch_leaders_modify( fd_bank_t * bank ) {
   ulong idx = fd_bank_epoch_get( bank ) % 2UL;
   bank->data->epoch_leaders_idx = idx;
-  return (fd_epoch_leaders_t *)fd_type_pun( fd_bank_get_epoch_leaders( bank->data ) + idx * FD_EPOCH_LEADERS_MAX_FOOTPRINT );
+  return (fd_epoch_leaders_t *)fd_type_pun( fd_bank_get_epoch_leaders( bank->data ) + idx * bank->data->epoch_leaders_footprint );
 }
 
 
@@ -178,15 +178,20 @@ fd_banks_footprint( ulong max_total_banks,
 
   /* max_fork_width is used in the macro below. */
 
+  ulong epoch_leaders_footprint = FD_EPOCH_LEADERS_FOOTPRINT( max_vote_accounts, FD_RUNTIME_SLOTS_PER_EPOCH );
+  ulong expected_stake_accounts = fd_ulong_min( max_stake_accounts, FD_RUNTIME_EXPECTED_STAKE_ACCOUNTS );
+  ulong expected_vote_accounts  = fd_ulong_min( max_vote_accounts, FD_RUNTIME_EXPECTED_VOTE_ACCOUNTS );
+
   ulong l = FD_LAYOUT_INIT;
-  l = FD_LAYOUT_APPEND( l, fd_banks_align(),                   sizeof(fd_banks_data_t) );
-  l = FD_LAYOUT_APPEND( l, fd_banks_pool_align(),              fd_banks_pool_footprint( max_total_banks ) );
-  l = FD_LAYOUT_APPEND( l, fd_banks_dead_align(),              fd_banks_dead_footprint() );
-  l = FD_LAYOUT_APPEND( l, fd_bank_top_votes_pool_align(),     fd_bank_top_votes_pool_footprint( max_total_banks ) );
-  l = FD_LAYOUT_APPEND( l, fd_bank_cost_tracker_pool_align(),  fd_bank_cost_tracker_pool_footprint( max_fork_width ) );
-  l = FD_LAYOUT_APPEND( l, fd_stake_rewards_align(),           fd_stake_rewards_footprint( max_stake_accounts, max_stake_accounts, max_fork_width ) );
-  l = FD_LAYOUT_APPEND( l, fd_vote_stakes_align(),             fd_vote_stakes_footprint( max_vote_accounts, FD_RUNTIME_EXPECTED_VOTE_ACCOUNTS, max_fork_width ) );
-  l = FD_LAYOUT_APPEND( l, fd_stake_delegations_delta_align(), fd_stake_delegations_delta_footprint( max_stake_accounts, max_total_banks ) );
+  l = FD_LAYOUT_APPEND( l, fd_banks_align(),                  sizeof(fd_banks_data_t) );
+  l = FD_LAYOUT_APPEND( l, fd_stake_delegations_align(),      fd_stake_delegations_footprint( max_stake_accounts, expected_stake_accounts, max_total_banks ) );
+  l = FD_LAYOUT_APPEND( l, FD_EPOCH_LEADERS_ALIGN,            2UL * epoch_leaders_footprint );
+  l = FD_LAYOUT_APPEND( l, fd_banks_pool_align(),             fd_banks_pool_footprint( max_total_banks ) );
+  l = FD_LAYOUT_APPEND( l, fd_banks_dead_align(),             fd_banks_dead_footprint() );
+  l = FD_LAYOUT_APPEND( l, fd_bank_top_votes_pool_align(),    fd_bank_top_votes_pool_footprint( max_total_banks ) );
+  l = FD_LAYOUT_APPEND( l, fd_bank_cost_tracker_pool_align(), fd_bank_cost_tracker_pool_footprint( max_fork_width ) );
+  l = FD_LAYOUT_APPEND( l, fd_stake_rewards_align(),          fd_stake_rewards_footprint( max_stake_accounts, expected_stake_accounts, max_fork_width ) );
+  l = FD_LAYOUT_APPEND( l, fd_vote_stakes_align(),            fd_vote_stakes_footprint( max_vote_accounts, fd_ulong_min( max_vote_accounts, expected_vote_accounts ), max_fork_width ) );
   return FD_LAYOUT_FINI( l, fd_banks_align() );
 }
 
@@ -217,15 +222,20 @@ fd_banks_new( void * shmem,
     return NULL;
   }
 
+  ulong epoch_leaders_footprint = FD_EPOCH_LEADERS_FOOTPRINT( max_vote_accounts, FD_RUNTIME_SLOTS_PER_EPOCH );
+  ulong expected_stake_accounts = fd_ulong_min( max_stake_accounts, FD_RUNTIME_EXPECTED_STAKE_ACCOUNTS );
+  ulong expected_vote_accounts  = fd_ulong_min( max_vote_accounts, FD_RUNTIME_EXPECTED_VOTE_ACCOUNTS );
+
   FD_SCRATCH_ALLOC_INIT( l, shmem );
-  fd_banks_data_t * banks_data                  = FD_SCRATCH_ALLOC_APPEND( l, fd_banks_align(),                   sizeof(fd_banks_data_t) );
-  void *            pool_mem                    = FD_SCRATCH_ALLOC_APPEND( l, fd_banks_pool_align(),              fd_banks_pool_footprint( max_total_banks ) );
-  void *            dead_banks_deque_mem        = FD_SCRATCH_ALLOC_APPEND( l, fd_banks_dead_align(),              fd_banks_dead_footprint() );
-  void *            top_votes_pool_mem          = FD_SCRATCH_ALLOC_APPEND( l, fd_bank_top_votes_pool_align(),     fd_bank_top_votes_pool_footprint( max_total_banks ) );
-  void *            cost_tracker_pool_mem       = FD_SCRATCH_ALLOC_APPEND( l, fd_bank_cost_tracker_pool_align(),  fd_bank_cost_tracker_pool_footprint( max_fork_width ) );
-  void *            stake_rewards_pool_mem      = FD_SCRATCH_ALLOC_APPEND( l, fd_stake_rewards_align(),           fd_stake_rewards_footprint( max_stake_accounts, max_stake_accounts, max_fork_width ) );
-  void *            vote_stakes_mem             = FD_SCRATCH_ALLOC_APPEND( l, fd_vote_stakes_align(),             fd_vote_stakes_footprint( max_vote_accounts, FD_RUNTIME_EXPECTED_VOTE_ACCOUNTS, max_fork_width ) );
-  void *            stake_delegations_delta_mem = FD_SCRATCH_ALLOC_APPEND( l, fd_stake_delegations_delta_align(), fd_stake_delegations_delta_footprint( max_stake_accounts, max_total_banks ) );
+  fd_banks_data_t * banks_data             = FD_SCRATCH_ALLOC_APPEND( l, fd_banks_align(),                  sizeof(fd_banks_data_t) );
+  void *            stake_delegations_mem  = FD_SCRATCH_ALLOC_APPEND( l, fd_stake_delegations_align(),      fd_stake_delegations_footprint( max_stake_accounts, expected_stake_accounts, max_total_banks ) );
+  void *            epoch_leaders_mem      = FD_SCRATCH_ALLOC_APPEND( l, FD_EPOCH_LEADERS_ALIGN,            2UL * epoch_leaders_footprint );
+  void *            pool_mem               = FD_SCRATCH_ALLOC_APPEND( l, fd_banks_pool_align(),             fd_banks_pool_footprint( max_total_banks ) );
+  void *            dead_banks_deque_mem   = FD_SCRATCH_ALLOC_APPEND( l, fd_banks_dead_align(),             fd_banks_dead_footprint() );
+  void *            top_votes_pool_mem     = FD_SCRATCH_ALLOC_APPEND( l, fd_bank_top_votes_pool_align(),    fd_bank_top_votes_pool_footprint( max_total_banks ) );
+  void *            cost_tracker_pool_mem  = FD_SCRATCH_ALLOC_APPEND( l, fd_bank_cost_tracker_pool_align(), fd_bank_cost_tracker_pool_footprint( max_fork_width ) );
+  void *            stake_rewards_pool_mem = FD_SCRATCH_ALLOC_APPEND( l, fd_stake_rewards_align(),          fd_stake_rewards_footprint( max_stake_accounts, expected_stake_accounts, max_fork_width ) );
+  void *            vote_stakes_mem        = FD_SCRATCH_ALLOC_APPEND( l, fd_vote_stakes_align(),            fd_vote_stakes_footprint( max_vote_accounts, expected_vote_accounts, max_fork_width ) );
 
   if( FD_UNLIKELY( FD_SCRATCH_ALLOC_FINI( l, fd_banks_align() ) != (ulong)banks_data + fd_banks_footprint( max_total_banks, max_fork_width, max_stake_accounts, max_vote_accounts ) ) ) {
     FD_LOG_WARNING(( "fd_banks_new: bad layout" ));
@@ -261,6 +271,8 @@ fd_banks_new( void * shmem,
   }
   fd_banks_set_dead_banks_deque( banks_data, banks_dead_deque );
 
+  fd_banks_set_epoch_leaders( banks_data, epoch_leaders_mem, epoch_leaders_footprint );
+
   /* Assign offset of the bank pool to the banks object. */
 
   fd_banks_set_bank_pool( banks_data, bank_pool );
@@ -269,6 +281,13 @@ fd_banks_new( void * shmem,
      each of the elements in the pool as well as set up the lock for
      each of the pools. */
 
+  fd_stake_delegations_t * stake_delegations = fd_stake_delegations_join( fd_stake_delegations_new( stake_delegations_mem, seed, max_stake_accounts, expected_stake_accounts, max_total_banks ) );
+  if( FD_UNLIKELY( !stake_delegations ) ) {
+    FD_LOG_WARNING(( "Unable to create stake delegations root" ));
+    return NULL;
+  }
+  fd_banks_set_stake_delegations( banks_data, fd_type_pun( stake_delegations_mem ) );
+
   fd_bank_top_votes_t * top_votes_pool = fd_bank_top_votes_pool_join( fd_bank_top_votes_pool_new( top_votes_pool_mem, max_total_banks ) );
   if( FD_UNLIKELY( !top_votes_pool ) ) {
     FD_LOG_WARNING(( "Failed to create top votes pool" ));
@@ -298,29 +317,20 @@ fd_banks_new( void * shmem,
     }
   }
 
-  fd_stake_rewards_t * stake_rewards = fd_stake_rewards_join( fd_stake_rewards_new( stake_rewards_pool_mem, max_stake_accounts, max_stake_accounts, max_fork_width, seed ) );
+  fd_stake_rewards_t * stake_rewards = fd_stake_rewards_join( fd_stake_rewards_new( stake_rewards_pool_mem, max_stake_accounts, fd_ulong_min( max_stake_accounts, FD_RUNTIME_EXPECTED_STAKE_ACCOUNTS ), max_fork_width, seed ) );
   if( FD_UNLIKELY( !stake_rewards ) ) {
     FD_LOG_WARNING(( "Failed to create stake rewards" ));
     return NULL;
   }
 
   fd_banks_set_stake_rewards( banks_data, stake_rewards );
-  fd_vote_stakes_t * vote_stakes = fd_vote_stakes_join( fd_vote_stakes_new( vote_stakes_mem, max_vote_accounts, FD_RUNTIME_EXPECTED_VOTE_ACCOUNTS, max_fork_width, seed ) );
+  fd_vote_stakes_t * vote_stakes = fd_vote_stakes_join( fd_vote_stakes_new( vote_stakes_mem, max_vote_accounts, fd_ulong_min( max_vote_accounts, FD_RUNTIME_EXPECTED_VOTE_ACCOUNTS ), max_fork_width, seed ) );
   if( FD_UNLIKELY( !vote_stakes ) ) {
     FD_LOG_WARNING(( "Failed to create vote stakes" ));
     return NULL;
   }
   fd_banks_set_vote_stakes( banks_data, vote_stakes );
 
-  /* TODO: differeniate the max stake accounts param for the base stake
-     delegations and the stake delegations delta structs. */
-  fd_stake_delegations_delta_t * stake_delegations_delta = fd_stake_delegations_delta_join( fd_stake_delegations_delta_new( stake_delegations_delta_mem, max_stake_accounts, max_total_banks ) );
-  if( FD_UNLIKELY( !stake_delegations_delta ) ) {
-    FD_LOG_WARNING(( "Failed to create stake delegations delta" ));
-    return NULL;
-  }
-  fd_banks_set_stake_delegations_delta( banks_data, stake_delegations_delta );
-
   /* For each bank, we need to set the offset of the pools and locks
      for each of the non-inlined fields. */
 
@@ -330,7 +340,7 @@ fd_banks_new( void * shmem,
 
     fd_bank_set_stake_rewards( bank, stake_rewards );
 
-    fd_bank_set_epoch_leaders( bank, (uchar *)banks_data + offsetof(fd_banks_data_t, epoch_leaders_mem) );
+    fd_bank_set_epoch_leaders( bank, epoch_leaders_mem, banks_data->epoch_leaders_footprint );
 
     fd_bank_set_stake_weights( bank, (uchar *)banks_data + offsetof(fd_banks_data_t, stake_weights) );
     fd_bank_set_stake_weights_cnt_off( bank, (uchar *)banks_data + offsetof(fd_banks_data_t, stake_weights_cnt) );
@@ -348,21 +358,16 @@ fd_banks_new( void * shmem,
     fd_vote_stakes_t * vote_stakes = fd_banks_get_vote_stakes( banks_data );
     fd_bank_set_vote_stakes( bank, vote_stakes );
 
-    fd_stake_delegations_delta_t * stake_delegations_delta = fd_banks_get_stake_delegations_delta( banks_data );
-    fd_bank_set_stake_delegations_delta( bank, stake_delegations_delta );
+    fd_stake_delegations_t * stake_delegations = fd_banks_get_stake_delegations( banks_data );
+    fd_bank_set_stake_delegations( bank, stake_delegations );
   }
 
   banks_data->max_total_banks    = max_total_banks;
   banks_data->max_fork_width     = max_fork_width;
   banks_data->max_stake_accounts = max_stake_accounts;
   banks_data->max_vote_accounts  = max_vote_accounts;
   banks_data->root_idx           = ULONG_MAX;
-  banks_data->bank_seq           = 0UL;  /* FIXME randomize across runs? */
-
-  if( FD_UNLIKELY( !fd_stake_delegations_new( banks_data->stake_delegations_root, 0UL, max_stake_accounts ) ) ) {
-    FD_LOG_WARNING(( "Unable to create stake delegations root" ));
-    return NULL;
-  }
+  banks_data->bank_seq           = 0UL;
 
   FD_COMPILER_MFENCE();
   FD_VOLATILE( banks_data->magic ) = FD_BANKS_MAGIC;
@@ -398,15 +403,19 @@ fd_banks_join( fd_banks_t * banks_ljoin,
     return NULL;
   }
 
+  ulong expected_stake_accounts = fd_ulong_min( banks_data->max_stake_accounts, FD_RUNTIME_EXPECTED_STAKE_ACCOUNTS );
+  ulong expected_vote_accounts  = fd_ulong_min( banks_data->max_vote_accounts, FD_RUNTIME_EXPECTED_VOTE_ACCOUNTS );
+
   FD_SCRATCH_ALLOC_INIT( l, banks_data );
-  banks_data                         = FD_SCRATCH_ALLOC_APPEND( l, fd_banks_align(),                   sizeof(fd_banks_data_t) );
-  void * pool_mem                    = FD_SCRATCH_ALLOC_APPEND( l, fd_banks_pool_align(),              fd_banks_pool_footprint( banks_data->max_total_banks ) );
-  void * dead_banks_deque_mem        = FD_SCRATCH_ALLOC_APPEND( l, fd_banks_dead_align(),              fd_banks_dead_footprint() );
-  void * top_votes_pool_mem          = FD_SCRATCH_ALLOC_APPEND( l, fd_bank_top_votes_pool_align(),     fd_bank_top_votes_pool_footprint( banks_data->max_total_banks ) );
-  void * cost_tracker_pool_mem       = FD_SCRATCH_ALLOC_APPEND( l, fd_bank_cost_tracker_pool_align(),  fd_bank_cost_tracker_pool_footprint( banks_data->max_fork_width ) );
-  void * stake_rewards_mem           = FD_SCRATCH_ALLOC_APPEND( l, fd_stake_rewards_align(),           fd_stake_rewards_footprint( banks_data->max_stake_accounts, banks_data->max_stake_accounts, banks_data->max_fork_width ) );
-  void * vote_stakes_mem             = FD_SCRATCH_ALLOC_APPEND( l, fd_vote_stakes_align(),             fd_vote_stakes_footprint( banks_data->max_vote_accounts, FD_RUNTIME_EXPECTED_VOTE_ACCOUNTS, banks_data->max_fork_width ) );
-  void * stake_delegations_delta_mem = FD_SCRATCH_ALLOC_APPEND( l, fd_stake_delegations_delta_align(), fd_stake_delegations_delta_footprint( banks_data->max_stake_accounts, banks_data->max_total_banks ) );
+  banks_data                   = FD_SCRATCH_ALLOC_APPEND( l, fd_banks_align(),                  sizeof(fd_banks_data_t) );
+  void * stake_delegations_mem = FD_SCRATCH_ALLOC_APPEND( l, fd_stake_delegations_align(),      fd_stake_delegations_footprint( banks_data->max_stake_accounts, expected_stake_accounts, banks_data->max_total_banks ) );
+  void * epoch_leaders_mem     = FD_SCRATCH_ALLOC_APPEND( l, FD_EPOCH_LEADERS_ALIGN,            2UL * banks_data->epoch_leaders_footprint );
+  void * pool_mem              = FD_SCRATCH_ALLOC_APPEND( l, fd_banks_pool_align(),             fd_banks_pool_footprint( banks_data->max_total_banks ) );
+  void * dead_banks_deque_mem  = FD_SCRATCH_ALLOC_APPEND( l, fd_banks_dead_align(),             fd_banks_dead_footprint() );
+  void * top_votes_pool_mem    = FD_SCRATCH_ALLOC_APPEND( l, fd_bank_top_votes_pool_align(),    fd_bank_top_votes_pool_footprint( banks_data->max_total_banks ) );
+  void * cost_tracker_pool_mem = FD_SCRATCH_ALLOC_APPEND( l, fd_bank_cost_tracker_pool_align(), fd_bank_cost_tracker_pool_footprint( banks_data->max_fork_width ) );
+  void * stake_rewards_mem     = FD_SCRATCH_ALLOC_APPEND( l, fd_stake_rewards_align(),          fd_stake_rewards_footprint( banks_data->max_stake_accounts, expected_stake_accounts, banks_data->max_fork_width ) );
+  void * vote_stakes_mem       = FD_SCRATCH_ALLOC_APPEND( l, fd_vote_stakes_align(),            fd_vote_stakes_footprint( banks_data->max_vote_accounts, expected_vote_accounts, banks_data->max_fork_width ) );
 
   FD_SCRATCH_ALLOC_FINI( l, fd_banks_align() );
 
@@ -427,6 +436,16 @@ fd_banks_join( fd_banks_t * banks_ljoin,
     return NULL;
   }
 
+  if( FD_UNLIKELY( epoch_leaders_mem!=fd_banks_get_epoch_leaders( banks_data ) ) ) {
+    FD_LOG_WARNING(( "Failed to join epoch leaders mem" ));
+    return NULL;
+  }
+
+  if( FD_UNLIKELY( stake_delegations_mem!=fd_banks_get_stake_delegations( banks_data ) ) ) {
+    FD_LOG_WARNING(( "Failed to join stake delegations root mem" ));
+    return NULL;
+  }
+
   fd_bank_top_votes_t * top_votes_pool = fd_banks_get_top_votes_pool( banks_data );
   if( FD_UNLIKELY( !top_votes_pool ) ) {
     FD_LOG_WARNING(( "Failed to join top votes pool" ));
@@ -453,7 +472,6 @@ fd_banks_join( fd_banks_t * banks_ljoin,
      stakes are joined correctly. */
   (void)stake_rewards_mem;
   (void)vote_stakes_mem;
-  (void)stake_delegations_delta_mem;
 
   banks_ljoin->data  = banks_data;
   banks_ljoin->locks = banks_locks;
@@ -522,6 +540,9 @@ fd_banks_init_bank( fd_bank_t *  bank_l,
   fd_vote_stakes_t * vote_stakes = fd_banks_get_vote_stakes( banks->data );
   bank->vote_stakes_fork_id      = fd_vote_stakes_get_root_idx( vote_stakes );
 
+  fd_stake_delegations_t * stake_delegations = fd_banks_get_stake_delegations( banks->data );
+  bank->stake_delegations_fork_id = fd_stake_delegations_new_fork( stake_delegations );
+
   /* Now that the node is inserted, update the root */
 
   banks->data->root_idx = bank->idx;
@@ -607,10 +628,8 @@ fd_banks_clone_from_parent( fd_bank_t *  bank_l,
 
   /* A new stake delegation delta fork needs to be created for the child
      bank. */
-  fd_rwlock_write( &banks->locks->stake_delegations_delta_lock );
-  fd_stake_delegations_delta_t * stake_delegations_delta = fd_banks_get_stake_delegations_delta( banks->data );
-  child_bank->stake_delegations_fork_id = fd_stake_delegations_delta_new_fork( stake_delegations_delta );
-  fd_rwlock_unwrite( &banks->locks->stake_delegations_delta_lock );
+  fd_stake_delegations_t * stake_delegations = fd_banks_get_stake_delegations( banks->data );
+  child_bank->stake_delegations_fork_id = fd_stake_delegations_new_fork( stake_delegations );
 
   fd_rwlock_unwrite( &banks->locks->banks_lock );
 
@@ -619,44 +638,14 @@ fd_banks_clone_from_parent( fd_bank_t *  bank_l,
   return bank_l;
 }
 
-/* Apply a fd_stake_delegations_t into the root. This assumes that there
-   are no in-between, un-applied banks between the root and the bank
-   being applied. This also assumes that the stake delegation object
-   that is being applied is a delta. */
-
-static inline void
-fd_banks_stake_delegations_apply_delta( fd_stake_delegations_t *       stake_delegations_base,
-                                        fd_stake_delegations_delta_t * stake_delegations_delta,
-                                        ushort                         stake_delegation_fork_id ) {
-
-  for( ulong i = fd_stake_delegations_delta_iter_init( stake_delegations_delta, stake_delegation_fork_id );
-       !fd_stake_delegations_delta_iter_done( stake_delegations_delta, stake_delegation_fork_id, i );
-       i = fd_stake_delegations_delta_iter_next( stake_delegations_delta, stake_delegation_fork_id, i ) ) {
-    fd_stake_delegation_t * stake_delegation = fd_stake_delegations_delta_iter_ele( stake_delegations_delta, stake_delegation_fork_id, i );
-    if( FD_LIKELY( !stake_delegation->is_tombstone ) ) {
-      fd_stake_delegations_update( stake_delegations_base,
-                                   &stake_delegation->stake_account,
-                                   &stake_delegation->vote_account,
-                                   stake_delegation->stake,
-                                   stake_delegation->activation_epoch,
-                                   stake_delegation->deactivation_epoch,
-                                   stake_delegation->credits_observed,
-                                   fd_stake_delegations_warmup_cooldown_rate_to_double( stake_delegation->warmup_cooldown_rate ) );
-    } else {
-      fd_stake_delegations_remove( stake_delegations_base, &stake_delegation->stake_account );
-    }
-  }
-}
-
 /* fd_bank_stake_delegation_apply_deltas applies all of the stake
    delegations for the entire direct ancestry from the bank to the
    root into a full fd_stake_delegations_t object. */
 
 static inline void
-fd_bank_stake_delegation_apply_deltas( fd_banks_t *                   banks,
-                                       fd_bank_t *                    bank,
-                                       fd_stake_delegations_t *       stake_delegations_base,
-                                       fd_stake_delegations_delta_t * stake_delegations_delta ) {
+fd_bank_stake_delegation_apply_deltas( fd_banks_t *             banks,
+                                       fd_bank_t *              bank,
+                                       fd_stake_delegations_t * stake_delegations ) {
 
   /* Naively what we want to do is iterate from the old root to the new
      root and apply the delta to the full state iteratively. */
@@ -682,35 +671,87 @@ fd_bank_stake_delegation_apply_deltas( fd_banks_t *                   banks,
 
   for( ulong i=pool_indices_len; i>0; i-- ) {
     ushort idx = pool_indices[i-1UL];
-    fd_banks_stake_delegations_apply_delta( stake_delegations_base,
-                                            stake_delegations_delta,
-                                            idx );
+    fd_stake_delegations_apply_fork_delta( stake_delegations, idx );
   }
 }
 
+static inline void
+fd_bank_stake_delegation_mark_deltas( fd_banks_t *             banks,
+                                      fd_bank_t *              bank,
+                                      fd_stake_delegations_t * stake_delegations ) {
+
+  ushort pool_indices[ banks->data->max_total_banks ];
+  ulong  pool_indices_len = 0UL;
+
+  fd_bank_data_t * bank_pool = fd_banks_get_bank_pool( banks->data );
+
+  fd_bank_data_t * curr_bank = fd_banks_pool_ele( bank_pool, bank->data->idx );
+  while( !!curr_bank ) {
+    if( curr_bank->stake_delegations_fork_id!=USHORT_MAX ) {
+      pool_indices[pool_indices_len++] = curr_bank->stake_delegations_fork_id;
+    }
+    curr_bank = fd_banks_pool_ele( bank_pool, curr_bank->parent_idx );
+  }
+
+  for( ulong i=pool_indices_len; i>0; i-- ) {
+    ushort idx = pool_indices[i-1UL];
+    fd_stake_delegations_mark_delta( stake_delegations, idx );
+  }
+}
+
+static inline void
+fd_bank_stake_delegation_unmark_deltas( fd_banks_t *             banks,
+                                        fd_bank_t *              bank,
+                                        fd_stake_delegations_t * stake_delegations ) {
+
+  ushort pool_indices[ banks->data->max_total_banks ];
+  ulong  pool_indices_len = 0UL;
+
+  fd_bank_data_t * bank_pool = fd_banks_get_bank_pool( banks->data );
+
+  fd_bank_data_t * curr_bank = fd_banks_pool_ele( bank_pool, bank->data->idx );
+  while( !!curr_bank ) {
+    if( curr_bank->stake_delegations_fork_id!=USHORT_MAX ) {
+      pool_indices[pool_indices_len++] = curr_bank->stake_delegations_fork_id;
+    }
+    curr_bank = fd_banks_pool_ele( bank_pool, curr_bank->parent_idx );
+  }
+
+  for( ulong i=pool_indices_len; i>0; i-- ) {
+    ushort idx = pool_indices[i-1UL];
+    fd_stake_delegations_unmark_delta( stake_delegations, idx );
+  }
+}
+
+
 fd_stake_delegations_t *
 fd_bank_stake_delegations_frontier_query( fd_banks_t * banks,
                                           fd_bank_t *  bank ) {
-
   fd_rwlock_write( &banks->locks->banks_lock );
 
-  /* First copy the rooted state into the frontier. */
-  memcpy( banks->data->stake_delegations_frontier, banks->data->stake_delegations_root, FD_STAKE_DELEGATIONS_FOOTPRINT );
-
-  /* Now apply all of the updates from the bank and all of its
-     ancestors in order to the frontier. */
-  fd_stake_delegations_t * stake_delegations_base = fd_type_pun( banks->data->stake_delegations_frontier );
-  fd_stake_delegations_delta_t * stake_delegations_delta = fd_banks_get_stake_delegations_delta( banks->data );
-  fd_bank_stake_delegation_apply_deltas( banks, bank, stake_delegations_base, stake_delegations_delta );
+  fd_stake_delegations_t * stake_delegations = fd_banks_get_stake_delegations( banks->data );
+  fd_bank_stake_delegation_mark_deltas( banks, bank, stake_delegations );
 
   fd_rwlock_unwrite( &banks->locks->banks_lock );
 
-  return stake_delegations_base;
+  return stake_delegations;
+}
+
+void
+fd_bank_stake_delegations_end_frontier_query( fd_banks_t * banks,
+                                              fd_bank_t *  bank ) {
+  fd_rwlock_write( &banks->locks->banks_lock );
+
+  fd_stake_delegations_t * stake_delegations = fd_banks_get_stake_delegations( banks->data );
+  fd_bank_stake_delegation_unmark_deltas( banks, bank, stake_delegations );
+
+  fd_rwlock_unwrite( &banks->locks->banks_lock );
 }
 
+
 fd_stake_delegations_t *
 fd_banks_stake_delegations_root_query( fd_banks_t * banks ) {
-  return fd_type_pun( banks->data->stake_delegations_root );
+  return fd_banks_get_stake_delegations( banks->data );
 }
 
 void
@@ -744,16 +785,11 @@ fd_banks_advance_root( fd_banks_t * banks,
     FD_LOG_CRIT(( "invariant violation: trying to advance root bank by more than one" ));
   }
 
-  fd_stake_delegations_delta_t * stake_delegations_delta = fd_banks_get_stake_delegations_delta( banks->data );
-
-  fd_rwlock_write( &banks->locks->stake_delegations_delta_lock );
+  fd_stake_delegations_t * stake_delegations = fd_banks_get_stake_delegations( banks->data );
+  fd_bank_stake_delegation_apply_deltas( banks, new_root, stake_delegations );
 
-  fd_stake_delegations_t * stake_delegations_base = fd_stake_delegations_join( banks->data->stake_delegations_root );
-  fd_bank_stake_delegation_apply_deltas( banks, new_root, stake_delegations_base, stake_delegations_delta );
-
-  fd_stake_delegations_delta_evict_fork( stake_delegations_delta, new_root->data->stake_delegations_fork_id );
+  fd_stake_delegations_evict_fork( stake_delegations, new_root->data->stake_delegations_fork_id );
   new_root->data->stake_delegations_fork_id = USHORT_MAX;
-  fd_rwlock_unwrite( &banks->locks->stake_delegations_delta_lock );
 
   /* Now that the deltas have been applied, we can remove all nodes
      that are not direct descendants of the new root. */
@@ -813,9 +849,7 @@ fd_banks_advance_root( fd_banks_t * banks,
     head->vote_stakes_fork_id = USHORT_MAX;
 
     if( head->stake_delegations_fork_id!=USHORT_MAX ) {
-      fd_rwlock_write( &banks->locks->stake_delegations_delta_lock );
-      fd_stake_delegations_delta_evict_fork( stake_delegations_delta, head->stake_delegations_fork_id );
-      fd_rwlock_unwrite( &banks->locks->stake_delegations_delta_lock );
+      fd_stake_delegations_evict_fork( stake_delegations, head->stake_delegations_fork_id );
       head->stake_delegations_fork_id = USHORT_MAX;
     }
 
@@ -1140,10 +1174,9 @@ fd_banks_prune_one_dead_bank( fd_banks_t *                   banks,
       fd_rwlock_unwrite( &banks->locks->top_votes_pool_lock );
     }
 
-    fd_rwlock_write( &banks->locks->stake_delegations_delta_lock );
-    fd_stake_delegations_delta_evict_fork( fd_banks_get_stake_delegations_delta( banks->data ), bank->stake_delegations_fork_id );
+    fd_stake_delegations_t * stake_delegations = fd_banks_get_stake_delegations( banks->data );
+    fd_stake_delegations_evict_fork( stake_delegations, bank->stake_delegations_fork_id );
     bank->stake_delegations_fork_id = USHORT_MAX;
-    fd_rwlock_unwrite( &banks->locks->stake_delegations_delta_lock );
 
     bank->stake_rewards_fork_id = UCHAR_MAX;
 
@@ -1242,8 +1275,6 @@ fd_banks_clear_bank( fd_banks_t * banks,
   bank->data->cost_tracker_pool_idx = fd_bank_cost_tracker_pool_idx_acquire( cost_tracker_pool );
   fd_rwlock_unwrite( &banks->locks->cost_tracker_lock[ bank->data->idx ] );
 
-  fd_rwlock_unwrite( &banks->locks->stake_delegations_delta_lock );
-
   fd_vote_stakes_t * vote_stakes = fd_banks_get_vote_stakes( banks->data );
   fd_vote_stakes_new( vote_stakes, max_vote_accounts, max_vote_accounts, banks->data->max_fork_width, 999UL );
 
@@ -1256,7 +1287,6 @@ fd_banks_locks_init( fd_banks_locks_t * locks ) {
   fd_rwlock_new( &locks->epoch_leaders_pool_lock );
   fd_rwlock_new( &locks->top_votes_pool_lock );
   fd_rwlock_new( &locks->vote_stakes_lock );
-  fd_rwlock_new( &locks->stake_delegations_delta_lock );
 
   for( ulong i=0UL; i<FD_BANKS_MAX_BANKS; i++ ) {
     fd_rwlock_new( &locks->lthash_lock[i] );
```

### src/flamenco/runtime/fd_bank.h
```diff
@@ -20,11 +20,7 @@ FD_PROTOTYPES_BEGIN
 
 #define FD_BANKS_MAX_BANKS (4096UL)
 
-/* TODO: Some optimizations, cleanups, future work:
-   1. Simple data types (ulong, int, etc) should be stored as their
-      underlying type instead of a byte array.
-   3. Rename locks to suffix with _query_locking and _query_locking_end
-  */
+/* TODO:FIXME: REREVIEW ALL DOCUMENTATION FOR BANKS */
 
 /* A fd_bank_t struct is the representation of the bank state on Solana
    for a given block.  More specifically, the bank state corresponds to
@@ -100,10 +96,10 @@ FD_PROTOTYPES_BEGIN
 
   Currently, there is a delta-based field, fd_stake_delegations_t.
   Each bank stores a delta-based representation in the form of an
-  aligned uchar buffer.  The full state is stored in fd_banks_t also as
-  a uchar buffer which corresponds to the full state of stake
-  delegations for the current root.  fd_banks_t also reserves another
-  buffer which can store the full state of the stake delegations.
+  aligned uchar buffer.  The full state is stored in fd_banks_t in
+  out-of-line memory sized using max_stake_accounts, and fd_banks_t
+  also reserves another out-of-line buffer which can store the full
+  state of the stake delegations for frontier queries.
 
   The cost tracker is allocated from a pool.  The lifetime of a cost
   tracker element starts when the bank is linked to a parent with a
@@ -364,10 +360,11 @@ struct fd_bank_data {
 
   ulong vote_stakes_offset;
 
-  ulong stake_delegations_delta_offset;
+  ulong stake_delegations_offset;
 
   ulong epoch_leaders_idx; /* always 0 or 1 based on % epoch */
   ulong epoch_leaders_offset;
+  ulong epoch_leaders_footprint;
 
   int   top_votes_dirty;
   ulong top_votes_pool_idx;
@@ -403,8 +400,6 @@ struct fd_banks_locks {
 
   fd_rwlock_t vote_stakes_lock;
 
-  fd_rwlock_t stake_delegations_delta_lock;
-
   /* These locks are per bank and are used to atomically update their
      corresponding fields in each bank.  The locks are indexed by the
      bank index. */
@@ -467,8 +462,11 @@ fd_bank_get_stake_weights_cnt_next( fd_bank_data_t * bank ) {
 }
 
 static inline void
-fd_bank_set_epoch_leaders( fd_bank_data_t * bank, uchar * epoch_leaders_mem ) {
-  bank->epoch_leaders_offset = (ulong)bank - (ulong)epoch_leaders_mem;
+fd_bank_set_epoch_leaders( fd_bank_data_t * bank,
+                           uchar *          epoch_leaders_mem,
+                           ulong            epoch_leaders_footprint ) {
+  bank->epoch_leaders_offset    = (ulong)bank - (ulong)epoch_leaders_mem;
+  bank->epoch_leaders_footprint = epoch_leaders_footprint;
 }
 
 static inline uchar *
@@ -519,22 +517,13 @@ fd_bank_vote_stakes_end_locking_modify( fd_bank_t * bank ) {
 }
 
 static inline void
-fd_bank_set_stake_delegations_delta( fd_bank_data_t * bank, fd_stake_delegations_delta_t * stake_delegations_delta ) {
-  bank->stake_delegations_delta_offset = (ulong)stake_delegations_delta - (ulong)bank;
+fd_bank_set_stake_delegations( fd_bank_data_t * bank, fd_stake_delegations_t * stake_delegations ) {
+  bank->stake_delegations_offset = (ulong)stake_delegations - (ulong)bank;
 }
 
-static inline fd_stake_delegations_delta_t *
-fd_bank_stake_delegations_delta_locking_modify( fd_bank_t * bank ) {
-  if( FD_UNLIKELY( bank->data->stake_delegations_fork_id==USHORT_MAX ) ) {
-    FD_LOG_CRIT(( "Stake delegations fork id is not allocated" ));
-  }
-  fd_rwlock_write( &bank->locks->stake_delegations_delta_lock );
-  return fd_type_pun( (uchar *)bank->data + bank->data->stake_delegations_delta_offset );
-}
-
-static inline void
-fd_bank_stake_delegations_delta_end_locking_modify( fd_bank_t * bank ) {
-  fd_rwlock_unwrite( &bank->locks->stake_delegations_delta_lock );
+static inline fd_stake_delegations_t *
+fd_bank_stake_delegations_modify( fd_bank_t * bank ) {
+  return fd_type_pun( (uchar *)bank->data + bank->data->stake_delegations_offset );
 }
 
 /* fd_bank_t is the alignment for the bank state. */
@@ -588,40 +577,23 @@ struct fd_banks_data {
 
   ulong vote_stakes_pool_offset;
 
-  ulong stake_delegations_delta_offset;
-
   ulong stake_rewards_offset;
 
   ulong dead_banks_deque_offset;
 
-  /* stake_delegations_root will be the full state of stake delegations
-     for the current root. It can get updated in two ways:
-     1. On boot the snapshot will be directly read into the rooted
-        stake delegations because we assume that any and all snapshots
-        are a rooted slot.
-     2. Calls to fd_banks_publish() will apply all of the stake
-        delegation deltas from each of the banks that are about to be
-        published.  */
-
-  uchar stake_delegations_root[FD_STAKE_DELEGATIONS_FOOTPRINT] __attribute__((aligned(FD_STAKE_DELEGATIONS_ALIGN)));
-
-  /* stake_delegations_frontier is reserved memory that can represent
-     the full state of stake delegations for the current frontier. This
-     is done by taking the stake_delegations_root and applying all of
-     the deltas from the current bank and all of its ancestors up to the
-     root bank. */
-
-  uchar stake_delegations_frontier[FD_STAKE_DELEGATIONS_FOOTPRINT] __attribute__((aligned(FD_STAKE_DELEGATIONS_ALIGN)));
-
-  /* The set of epoch leaders for the current and previous epochs.  Only
+  /* The set of epoch leaders for the current and previous epochs is
+     allocated out-of-line and tracked by epoch_leaders_offset.  Only
      two need to be stored because in the worst case we will have a root
      that sits behind an epoch boundary, with leaf banks executing into
      the next epoch.  All banks that execute behind the boundary, will
      use the previous epoch's leader schedule, and all nodes after the
      epoch boundary are guaranteed to produce identical leader
      schedules. */
 
-  uchar epoch_leaders_mem[ 2UL ][ FD_EPOCH_LEADERS_MAX_FOOTPRINT ] __attribute__((aligned(FD_EPOCH_LEADERS_ALIGN)));
+  ulong epoch_leaders_offset;
+  ulong epoch_leaders_footprint;
+
+  ulong stake_delegations_offset;
 
   /* Set of compressed stake weights for the leader schedule for the
      current epoch. */
@@ -700,35 +672,34 @@ fd_bank_lthash_end_locking_modify( fd_bank_t * bank );
 FD_BANKS_ITER(X)
 #undef X
 
-/* Each bank has a fd_stake_delegations_t object which is delta-based.
-   The usage pattern is the same as other bank fields:
-   1. fd_bank_stake_delegations_delta_locking_modify( bank ) will return
-      a mutable pointer to the stake delegations delta object. If the
-      caller has not yet initialized the delta object, then it will
-      be initialized. Because it is a delta it is not copied over from
-      a parent bank.
-   2. fd_bank_stake_delegations_delta_locking_query( bank ) will return
-      a const pointer to the stake delegations delta object. If the
-      delta object has not been initialized, then NULL is returned.
-   3. fd_bank_stake_delegations_delta_locking_end_modify( bank ) will
-      release the write lock on the object.
-   4. fd_bank_stake_delegations_delta_locking_end_query( bank ) will
-      release a read lock on the object.
-*/
-
 /* fd_bank_stake_delegations_frontier_query() will return a pointer to
    the full stake delegations for the current frontier. The caller is
    responsible that there are no concurrent readers or writers to
    the stake delegations returned by this function.
 
-   Under the hood, the function copies the rooted stake delegations and
-   applies all of the deltas for the direct ancestry from the current
-   bank up to the rooted bank to the copy. */
+   Under the hood, the function applies all of the stake delegation
+   deltas from all banks starting from the root down to the current bank
+   to the rooted version of the stake delegations.  This is done in a
+   reversible way and is unwound with a call to
+   fd_bank_stake_delegations_end_frontier_query(). */
 
 fd_stake_delegations_t *
 fd_bank_stake_delegations_frontier_query( fd_banks_t * banks,
                                           fd_bank_t *  bank );
 
+/* fd_bank_stake_delegations_end_frontier_query() will finish the
+   reversible operation started by
+   fd_bank_stake_delegations_frontier_query().  It is unsafe to call
+   fd_bank_stake_delegations_frontier_query multiple times without
+   calling this function in between.
+
+   Under the hood, it undoes any references to the stake delegation
+   deltas that were applied. */
+
+void
+fd_bank_stake_delegations_end_frontier_query( fd_banks_t * banks,
+                                              fd_bank_t *  bank );
+
 /* fd_banks_stake_delegations_root_query() will return a pointer to the
    full stake delegations for the current root. This function should
    only be called on boot. */
@@ -766,6 +737,30 @@ fd_banks_set_dead_banks_deque( fd_banks_data_t *   banks_data,
   banks_data->dead_banks_deque_offset = (ulong)dead_banks_deque - (ulong)banks_data;
 }
 
+static inline fd_epoch_leaders_t *
+fd_banks_get_epoch_leaders( fd_banks_data_t * banks_data ) {
+  return fd_type_pun( (uchar *)banks_data + banks_data->epoch_leaders_offset );
+}
+
+static inline void
+fd_banks_set_epoch_leaders( fd_banks_data_t * banks_data,
+                            uchar *           epoch_leaders_mem,
+                            ulong             epoch_leaders_footprint ) {
+  banks_data->epoch_leaders_offset    = (ulong)epoch_leaders_mem - (ulong)banks_data;
+  banks_data->epoch_leaders_footprint = epoch_leaders_footprint;
+}
+
+static inline fd_stake_delegations_t *
+fd_banks_get_stake_delegations( fd_banks_data_t * banks_data ) {
+  return fd_type_pun( (uchar *)banks_data + banks_data->stake_delegations_offset );
+}
+
+static inline void
+fd_banks_set_stake_delegations( fd_banks_data_t * banks_data,
+                                uchar *           stake_delegations_mem ) {
+  banks_data->stake_delegations_offset = (ulong)stake_delegations_mem - (ulong)banks_data;
+}
+
 static inline fd_bank_top_votes_t *
 fd_banks_get_top_votes_pool( fd_banks_data_t * banks_data ) {
   return fd_type_pun( (uchar *)banks_data + banks_data->top_votes_pool_offset );
@@ -814,16 +809,6 @@ fd_banks_set_vote_stakes( fd_banks_data_t * banks_data, fd_vote_stakes_t * vote_
   banks_data->vote_stakes_pool_offset = (ulong)vote_stakes - (ulong)banks_data;
 }
 
-static inline fd_stake_delegations_delta_t *
-fd_banks_get_stake_delegations_delta( fd_banks_data_t * banks_data ) {
-  return fd_type_pun( (uchar *)banks_data + banks_data->stake_delegations_delta_offset );
-}
-
-static inline void
-fd_banks_set_stake_delegations_delta( fd_banks_data_t * banks_data, fd_stake_delegations_delta_t * stake_delegations_delta ) {
-  banks_data->stake_delegations_delta_offset = (ulong)stake_delegations_delta - (ulong)banks_data;
-}
-
 /* fd_banks_root() returns a pointer to the root bank respectively. */
 
 FD_FN_PURE static inline fd_bank_t *
```

### src/flamenco/runtime/fd_runtime.c
```diff
@@ -661,6 +661,8 @@ fd_runtime_process_new_epoch( fd_banks_t *              banks,
                                 parent_blockhash,
                                 parent_epoch );
 
+  fd_bank_stake_delegations_end_frontier_query( banks, bank );
+
   /* The Agave client handles updating their stakes cache with a call to
      update_epoch_stakes() which keys stakes by the leader schedule
      epochs and retains up to 6 epochs of stakes.  However, to correctly
@@ -1619,7 +1621,7 @@ fd_runtime_init_bank_from_genesis( fd_banks_t *              banks,
         FD_LOG_ERR(( "Invalid warmup cooldown rate %f for stake account %s", stake_state.inner.stake.stake.delegation.warmup_cooldown_rate, stake_b58 ));
       }
 
-      fd_stake_delegations_update(
+      fd_stake_delegations_root_update(
           stake_delegations,
           &account->pubkey,
           &stake_state.inner.stake.stake.delegation.voter_pubkey,
```

### src/flamenco/runtime/fd_runtime.h
```diff
@@ -184,20 +184,6 @@ struct fd_runtime {
 
   } vote_program;
 
-  union {
-    struct {
-      uchar vote_state_mem       [ FD_VOTE_STATE_VERSIONED_FOOTPRINT ] __attribute__((aligned(FD_VOTE_STATE_VERSIONED_ALIGN)));
-      uchar landed_votes_mem     [ FD_VOTE_STATE_VERSIONED_FOOTPRINT ] __attribute__((aligned(128UL)));
-    } delegate;
-    struct {
-      uchar delinquent_vote_state_mem       [ FD_VOTE_STATE_VERSIONED_FOOTPRINT ] __attribute__((aligned(FD_VOTE_STATE_VERSIONED_ALIGN)));
-      uchar delinquent_landed_votes_mem     [ FD_VOTE_STATE_VERSIONED_FOOTPRINT ] __attribute__((aligned(128UL)));
-
-      uchar reference_vote_state_mem       [ FD_VOTE_STATE_VERSIONED_FOOTPRINT ] __attribute__((aligned(FD_VOTE_STATE_VERSIONED_ALIGN)));
-      uchar reference_landed_votes_mem     [ FD_VOTE_STATE_VERSIONED_FOOTPRINT ] __attribute__((aligned(128UL)));
-    } deactivate_delinquent;
-  } stake_program;
-
   struct {
 
     /* Ticks spent spent preparing a txn-level VM (zeroing memory,
```
