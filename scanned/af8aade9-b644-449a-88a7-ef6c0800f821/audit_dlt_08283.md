# [?] replay: fix buffer overflow in scheduler

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-09-15
Source: https://github.com/firedancer-io/firedancer/commit/4507bc93b15bed10f98f1f5296d301365ee34b8d
Type: security-commit

## Details
replay: fix buffer overflow in scheduler

## Patch
### src/discof/replay/fd_sched.c
```diff
@@ -42,7 +42,6 @@ struct fd_sched_block {
   uint                txn_in_flight_cnt;
   uint                txn_done_cnt;
   uint                shred_cnt;
-  uint                fec_cnt;
 
   /* Parser state. */
   uchar               txn[ FD_TXN_MAX_SZ ] __attribute__((aligned(alignof(fd_txn_t))));
@@ -109,17 +108,26 @@ struct fd_sched_metrics {
   uint  lane_switch_cnt;
   uint  lane_promoted_cnt;
   uint  lane_demoted_cnt;
-  uint  serializing_cnt;
-  ulong fec_cnt;
-  ulong txn_parsed_cnt;
-  ulong txn_done_cnt;
+  uint  alut_success_cnt;
+  uint  alut_serializing_cnt;
   uint  txn_abandoned_parsed_cnt;
   uint  txn_abandoned_done_cnt;
+  uint  txn_max_in_flight_cnt;
+  ulong txn_weighted_in_flight_cnt;
+  ulong txn_weighted_in_flight_tickcount;
+  ulong txn_none_in_flight_tickcount;
+  ulong txn_parsed_cnt;
+  ulong txn_done_cnt;
+  ulong bytes_ingested_cnt;
+  ulong bytes_ingested_unparsed_cnt;
+  ulong bytes_dropped_cnt;
+  ulong fec_cnt;
 };
 typedef struct fd_sched_metrics fd_sched_metrics_t;
 
 struct fd_sched {
   fd_sched_metrics_t  metrics[ 1 ];
+  long                txn_in_flight_last_tick;
   ulong               root_idx;
   fd_rdisp_t *        rdisp;
   ulong               active_block_idx; /* index of the actively replayed block, or null_idx if no block is
@@ -220,10 +228,15 @@ block_is_activatable( fd_sched_block_t * block ) {
 
 FD_FN_UNUSED static void
 debug_print_block( fd_sched_block_t * block ) {
-  FD_LOG_INFO(( "block slot %lu, prime %lu, staged %d (lane %lu), dying %d, in_rdisp %d, fec_eos %d, rooted %d, block_start_signaled %d, block_end_signaled %d, txn_parsed_cnt %u, txn_in_flight_cnt %u, txn_done_cnt %u, shred_cnt %u, fec_cnt %u",
-                (ulong)block->block_id.slot, (ulong)block->block_id.prime, block->staged, block->staging_lane, block->dying, block->in_rdisp, block->fec_eos, block->rooted, block->block_start_signaled, block->block_end_signaled, block->txn_parsed_cnt, block->txn_in_flight_cnt, block->txn_done_cnt, block->shred_cnt, block->fec_cnt ));
+  FD_LOG_INFO(( "block slot %lu, prime %lu, staged %d (lane %lu), dying %d, in_rdisp %d, fec_eos %d, rooted %d, block_start_signaled %d, block_end_signaled %d, txn_parsed_cnt %u, txn_in_flight_cnt %u, txn_done_cnt %u, shred_cnt %u",
+                (ulong)block->block_id.slot, (ulong)block->block_id.prime, block->staged, block->staging_lane, block->dying, block->in_rdisp, block->fec_eos, block->rooted, block->block_start_signaled, block->block_end_signaled, block->txn_parsed_cnt, block->txn_in_flight_cnt, block->txn_done_cnt, block->shred_cnt ));
 }
 
+FD_FN_UNUSED static void
+debug_print_metrics( fd_sched_t * sched ) {
+  FD_LOG_INFO(( "metrics: block_added_cnt %u, block_added_staged_cnt %u, block_added_unstaged_cnt %u, block_added_dead_ood_cnt %u, block_removed_cnt %u, block_abandoned_cnt %u, block_promoted_cnt %u, block_demoted_cnt %u, deactivate_no_child_cnt %u, deactivate_no_txn_cnt %u, deactivate_pruned_cnt %u, deactivate_abandoned_cnt %u, lane_switch_cnt %u, lane_promoted_cnt %u, lane_demoted_cnt %u, alut_success_cnt %u, alut_serializing_cnt %u, txn_abandoned_parsed_cnt %u, txn_abandoned_done_cnt %u, txn_max_in_flight_cnt %u, txn_weighted_in_flight_cnt %lu, txn_weighted_in_flight_tickcount %lu, txn_none_in_flight_tickcount %lu, txn_parsed_cnt %lu, txn_done_cnt %lu, bytes_ingested_cnt %lu, bytes_ingested_unparsed_cnt %lu, bytes_dropped_cnt %lu, fec_cnt %lu",
+                sched->metrics->block_added_cnt, sched->metrics->block_added_staged_cnt, sched->metrics->block_added_unstaged_cnt, sched->metrics->block_added_dead_ood_cnt, sched->metrics->block_removed_cnt, sched->metrics->block_abandoned_cnt, sched->metrics->block_promoted_cnt, sched->metrics->block_demoted_cnt, sched->metrics->deactivate_no_child_cnt, sched->metrics->deactivate_no_txn_cnt, sched->metrics->deactivate_pruned_cnt, sched->metrics->deactivate_abandoned_cnt, sched->metrics->lane_switch_cnt, sched->metrics->lane_promoted_cnt, sched->metrics->lane_demoted_cnt, sched->metrics->alut_success_cnt, sched->metrics->alut_serializing_cnt, sched->metrics->txn_abandoned_parsed_cnt, sched->metrics->txn_abandoned_done_cnt, sched->metrics->txn_max_in_flight_cnt, sched->metrics->txn_weighted_in_flight_cnt, sched->metrics->txn_weighted_in_flight_tickcount, sched->metrics->txn_none_in_flight_tickcount, sched->metrics->txn_parsed_cnt, sched->metrics->txn_done_cnt, sched->metrics->bytes_ingested_cnt, sched->metrics->bytes_ingested_unparsed_cnt, sched->metrics->bytes_dropped_cnt, sched->metrics->fec_cnt ));
+}
 
 /* Public functions. */
 
@@ -267,6 +280,7 @@ fd_sched_new( void * mem ) {
   block_pool_leave( _bpool_join );
 
   fd_memset( sched->metrics, 0, sizeof(fd_sched_metrics_t) );
+  sched->txn_in_flight_last_tick = LONG_MAX;
 
   sched->root_idx         = null_idx;
   sched->active_block_idx = null_idx;
@@ -364,6 +378,7 @@ fd_sched_fec_ingest( fd_sched_t * sched, fd_sched_fec_t * fec ) {
       sched->metrics->block_added_dead_ood_cnt++;
 
       /* Ignore the FEC set for a dead block. */
+      sched->metrics->bytes_dropped_cnt += fec->fec->data_sz;
       return;
     }
 
@@ -439,6 +454,7 @@ fd_sched_fec_ingest( fd_sched_t * sched, fd_sched_fec_t * fec ) {
 
   if( FD_UNLIKELY( block->dying ) ) {
     /* Ignore the FEC set for a dead block. */
+    sched->metrics->bytes_dropped_cnt += fec->fec->data_sz;
     return;
   }
 
@@ -459,6 +475,7 @@ fd_sched_fec_ingest( fd_sched_t * sched, fd_sched_fec_t * fec ) {
     FD_LOG_WARNING(( "invariant violation: block->fec_eob set but getting another FEC set that is last in batch fec->mr %s, slot %lu, prime %lu, parent slot %lu, parent prime %lu",
                      FD_BASE58_ENC_32_ALLOCA( fec->fec->key.mr.hash ), (ulong)fec->block_id.slot, (ulong)fec->block_id.prime, (ulong)fec->parent_block_id.slot, (ulong)fec->parent_block_id.prime ));
     block->dying = 1;//FIXME inform replay/banks that it's dead?
+    sched->metrics->bytes_dropped_cnt += fec->fec->data_sz;
     return;
   }
   if( FD_UNLIKELY( block->child_idx!=null_idx ) ) {
@@ -468,35 +485,37 @@ fd_sched_fec_ingest( fd_sched_t * sched, fd_sched_fec_t * fec ) {
                   block->child_idx, FD_BASE58_ENC_32_ALLOCA( fec->fec->key.mr.hash ), (ulong)fec->block_id.slot, (ulong)fec->block_id.prime, (ulong)fec->parent_block_id.slot, (ulong)fec->parent_block_id.prime ));
   }
 
-  /* If there is residual data from the previous FEC set within the same
-     batch, we move it to the beginning of the buffer and append the new
-     FEC set. */
+  FD_TEST( block->fec_buf_sz>=block->fec_buf_soff );
   if( FD_LIKELY( block->fec_buf_sz>block->fec_buf_soff ) ) {
-    /* Addition is safe and won't overflow because we checked the FEC
-       set size above. */
-    if( FD_UNLIKELY( block->fec_buf_sz-block->fec_buf_soff+fec->fec->data_sz>FD_SCHED_MAX_FEC_BUF_SZ ) ) {
-      /* In a conformant block, there shouldn't be more than a
-         transaction's worth of residual data left over from the
-         previous FEC set within the same batch.  So if this condition
-         doesn't hold, it's a bad block.  Instead of crashing, we should
-         refuse to replay down the fork. */
-      FD_LOG_WARNING(( "bad block: fec_buf_sz %u, fec_buf_soff %u, fec->data_sz %lu, fec->mr %s, slot %lu, prime %lu, parent slot %lu, parent prime %lu",
-                       block->fec_buf_sz, block->fec_buf_soff, fec->fec->data_sz, FD_BASE58_ENC_32_ALLOCA( fec->fec->key.mr.hash ), (ulong)fec->block_id.slot, (ulong)fec->block_id.prime, (ulong)fec->parent_block_id.slot, (ulong)fec->parent_block_id.prime ));
-      block->dying = 1;//FIXME inform replay/banks that it's dead?
-      return;
-    }
+    /* If there is residual data from the previous FEC set within the
+       same batch, we move it to the beginning of the buffer and append
+       the new FEC set. */
     memmove( block->fec_buf, block->fec_buf+block->fec_buf_soff, block->fec_buf_sz-block->fec_buf_soff );
-    block->fec_buf_sz -= block->fec_buf_soff;
-    block->fec_buf_soff = 0;
+  }
+  block->fec_buf_sz  -= block->fec_buf_soff;
+  block->fec_buf_soff = 0;
+  /* Addition is safe and won't overflow because we checked the FEC
+     set size above. */
+  if( FD_UNLIKELY( block->fec_buf_sz-block->fec_buf_soff+fec->fec->data_sz>FD_SCHED_MAX_FEC_BUF_SZ ) ) {
+    /* In a conformant block, there shouldn't be more than a
+       transaction's worth of residual data left over from the previous
+       FEC set within the same batch.  So if this condition doesn't
+       hold, it's a bad block.  Instead of crashing, we should refuse to
+       replay down the fork. */
+    FD_LOG_WARNING(( "bad block: fec_buf_sz %u, fec_buf_soff %u, fec->data_sz %lu, fec->mr %s, slot %lu, prime %lu, parent slot %lu, parent prime %lu",
+                     block->fec_buf_sz, block->fec_buf_soff, fec->fec->data_sz, FD_BASE58_ENC_32_ALLOCA( fec->fec->key.mr.hash ), (ulong)fec->block_id.slot, (ulong)fec->block_id.prime, (ulong)fec->parent_block_id.slot, (ulong)fec->parent_block_id.prime ));
+    block->dying = 1;//FIXME inform replay/banks that it's dead?
+    sched->metrics->bytes_dropped_cnt += fec->fec->data_sz;
+    return;
   }
 
   block->shred_cnt += fec->shred_cnt;
-  block->fec_cnt++;
   sched->metrics->fec_cnt++;
 
   /* Append the new FEC set to the end of the buffer. */
   fd_memcpy( block->fec_buf+block->fec_buf_sz, fec->fec->data, fec->fec->data_sz );
   block->fec_buf_sz += (uint)fec->fec->data_sz;
+  sched->metrics->bytes_ingested_cnt += fec->fec->data_sz;
 
   block->fec_eob = fec->is_last_in_batch;
   block->fec_eos = fec->is_last_in_block;
@@ -569,8 +588,17 @@ fd_sched_txn_next_ready( fd_sched_t * sched, fd_sched_txn_ready_t * out_txn ) {
     }
     out_txn->block_id         = block->block_id;
     out_txn->parent_block_id  = block_pool_ele( sched->block_pool, block->parent_idx )->block_id;
+
+    long now = fd_tickcount();
+    ulong delta = (ulong)(now-sched->txn_in_flight_last_tick);
+    sched->metrics->txn_none_in_flight_tickcount     += fd_ulong_if( block->txn_in_flight_cnt==0U && sched->txn_in_flight_last_tick!=LONG_MAX, delta, 0UL );
+    sched->metrics->txn_weighted_in_flight_tickcount += fd_ulong_if( block->txn_in_flight_cnt!=0U, delta, 0UL );
+    sched->metrics->txn_weighted_in_flight_cnt       += delta*block->txn_in_flight_cnt;
+    sched->txn_in_flight_last_tick = now;
+
     block->txn_in_flight_cnt++;
     txn_queued_cnt--;
+    sched->metrics->txn_max_in_flight_cnt = fd_uint_max( sched->metrics->txn_max_in_flight_cnt, block->txn_in_flight_cnt );
     return 1UL;
   }
 
@@ -623,6 +651,13 @@ fd_sched_txn_done( fd_sched_t * sched, ulong txn_id ) {
   }
 
   if( FD_LIKELY( txn_id!=FD_SCHED_TXN_ID_BLOCK_START && txn_id!=FD_SCHED_TXN_ID_BLOCK_END ) ) {
+    FD_TEST( txn_id<FD_SCHED_MAX_DEPTH );
+    long now = fd_tickcount();
+    ulong delta = (ulong)(now-sched->txn_in_flight_last_tick);
+    sched->metrics->txn_weighted_in_flight_tickcount += delta;
+    sched->metrics->txn_weighted_in_flight_cnt       += delta*block->txn_in_flight_cnt;
+    sched->txn_in_flight_last_tick = now;
+
     block->txn_done_cnt++;
     block->txn_in_flight_cnt--;
     fd_rdisp_complete_txn( sched->rdisp, txn_id );
@@ -639,7 +674,7 @@ fd_sched_txn_done( fd_sched_t * sched, ulong txn_id ) {
     return;
   }
 
-  if( FD_UNLIKELY( sched->active_block_idx!=block_idx ) ) {
+  if( FD_UNLIKELY( !block->dying && sched->active_block_idx!=block_idx ) ) {
     /* Block is not dead.  So we should be actively replaying it. */
     fd_sched_block_t * active_block = block_pool_ele( sched->block_pool, sched->active_block_idx );
     FD_LOG_CRIT(( "invariant violation: sched->active_block_idx %lu, slot %lu, prime %lu, block_idx %lu, slot %lu, prime %lu",
@@ -953,7 +988,6 @@ add_block( fd_sched_t *          sched,
   block->txn_in_flight_cnt = 0U;
   block->txn_done_cnt      = 0U;
   block->shred_cnt         = 0U;
-  block->fec_cnt           = 0U;
 
   block->mblks_rem    = 0UL;
   block->txns_rem     = 0UL;
@@ -1056,6 +1090,7 @@ fd_sched_parse( fd_sched_t * sched, fd_sched_block_t * block, fd_sched_alut_ctx_
   }
   if( block->fec_eob ) {
     /* Ignore trailing bytes at the end of a batch. */
+    sched->metrics->bytes_ingested_unparsed_cnt += block->fec_buf_sz-block->fec_buf_soff;
     block->fec_buf_soff = 0U;
     block->fec_buf_sz   = 0U;
     block->fec_sob      = 1;
@@ -1089,24 +1124,23 @@ fd_sched_parse_txn( fd_sched_t * sched, fd_sched_block_t * block, fd_sched_alut_
     if( FD_LIKELY( slot_hashes_global ) ) {
       fd_slot_hash_t * slot_hash = deq_fd_slot_hash_t_join( (uchar *)slot_hashes_global + slot_hashes_global->hashes_offset );
       serializing = !!fd_runtime_load_txn_address_lookup_tables( txn, block->fec_buf+block->fec_buf_soff, alut_ctx->funk, alut_ctx->funk_txn, alut_ctx->els, slot_hash, block->aluts );
+      sched->metrics->alut_success_cnt += (uint)!serializing;
     } else {
       serializing = 1;
     }
     } FD_SPAD_FRAME_END;
   }
 
   ulong txn_idx = fd_rdisp_add_txn( sched->rdisp, block->block_id.id, txn, block->fec_buf+block->fec_buf_soff, serializing ? NULL : block->aluts, serializing );
-  if( FD_UNLIKELY( txn_idx==0UL ) ) {
-    FD_LOG_CRIT(( "invariant violation: fd_rdisp_add_txn returned 0" ));
-  }
+  FD_TEST( txn_idx!=0UL );
   sched->metrics->txn_parsed_cnt++;
-  sched->metrics->serializing_cnt += (uint)serializing;
+  sched->metrics->alut_serializing_cnt += (uint)serializing;
   sched->txn_pool_free_cnt--;
   fd_txn_p_t * txn_p = sched->txn_pool + txn_idx;
   txn_p->payload_sz  = pay_sz;
   fd_memcpy( txn_p->payload, block->fec_buf+block->fec_buf_soff, pay_sz );
   fd_memcpy( TXN(txn_p),     txn,                                txn_sz );
-  sched->txn_to_block_idx[txn_idx] = block_pool_idx( sched->block_pool, block );
+  sched->txn_to_block_idx[ txn_idx ] = block_pool_idx( sched->block_pool, block );
 
   block->fec_buf_soff += (uint)pay_sz;
   block->txn_parsed_cnt++;
```
