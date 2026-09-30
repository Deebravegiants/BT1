# [?] backtest: fix race condition

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-09-18
Source: https://github.com/firedancer-io/firedancer/commit/bf26248a3f6faf5cf5b20637f12c574ce3f5fb0e
Type: security-commit

## Details
backtest: fix race condition

## Patch
### src/app/firedancer-dev/commands/backtest.c
```diff
@@ -332,7 +332,6 @@ backtest_topo( config_t * config ) {
   /**********************************************************************/
   /* Finish and print out the topo information                          */
   /**********************************************************************/
-  FD_LOG_WARNING(( "AAAA" ));
   fd_topob_finish( topo, CALLBACKS );
 }
 
```

### src/discof/backtest/fd_backtest_tile.c
```diff
@@ -23,6 +23,8 @@ typedef struct {
 
 typedef struct {
 
+  int initialized;
+
   /* Flag for whether after_credit can publish another FEC set to
      progress replay */
 
@@ -46,11 +48,6 @@ typedef struct {
 
   fd_valloc_t valloc;
 
-  /* Manifest is received from the snap_out link to discover the
-     snapshot slot (TODO block id) */
-
-  fd_snapshot_manifest_t snapshot_manifest;
-
   /* RocksDB-related ctx for iterating shreds in RocksDB and checking
      bank hash */
 
@@ -75,12 +72,11 @@ typedef struct {
   uchar    in_kind [ MAX_IN_LINKS ];
   in_ctx_t in_links[ MAX_IN_LINKS ];
 
-  fd_wksp_t *           replay_out_mem;
-  ulong                 replay_out_chunk0;
-  ulong                 replay_out_wmark;
-  ulong                 replay_out_chunk;
-  ulong                 replay_out_idx;
-  fd_replay_slot_completed_t replay_slot_info;
+  fd_wksp_t * replay_out_mem;
+  ulong       replay_out_chunk0;
+  ulong       replay_out_wmark;
+  ulong       replay_out_chunk;
+  ulong       replay_out_idx;
 
   ulong       tower_out_idx;
   fd_wksp_t * tower_out_mem;
@@ -158,7 +154,7 @@ rocksdb_next_shred( ctx_t * ctx,
    recorded in RocksDB. */
 
 static void
-rocksdb_check_bank_hash( ctx_t * ctx, ulong slot, fd_hash_t * bank_hash ) {
+rocksdb_check_bank_hash( ctx_t * ctx, ulong slot, fd_hash_t const * bank_hash ) {
   ulong slot_be = fd_ulong_bswap(slot);
 
   size_t vallen = 0;
@@ -305,107 +301,95 @@ after_credit( ctx_t *             ctx,
 }
 
 static inline int
-before_frag( ctx_t * ctx,
-             ulong                  in_idx,
-             ulong                  seq FD_PARAM_UNUSED,
-             ulong                  sig ) {
-  uint in_kind = ctx->in_kind[ in_idx ];
-  switch( in_kind ) {
-  case IN_KIND_REPLAY: return sig!=REPLAY_SIG_SLOT_COMPLETED;
-  case IN_KIND_SNAP:   ctx->credit = fd_ssmsg_sig_message( sig ) == FD_SSMSG_DONE; return ctx->credit;
-  default:             FD_LOG_ERR(( "unhandled in_kind: %u in_idx: %lu", in_kind, in_idx ));
-  }
-}
-
-static void
-during_frag( ctx_t * ctx,
-             ulong   in_idx,
-             ulong   seq FD_PARAM_UNUSED,
-             ulong   sig FD_PARAM_UNUSED,
-             ulong   chunk,
-             ulong   sz FD_PARAM_UNUSED,
-             ulong   ctl FD_PARAM_UNUSED ) {
-  uint          in_kind     = ctx->in_kind[in_idx];
-  uchar const * chunk_laddr = fd_chunk_to_laddr( ctx->in_links[in_idx].mem, chunk );
-  switch( in_kind ) {
-  case IN_KIND_REPLAY: memcpy( &ctx->replay_slot_info,  chunk_laddr, sizeof(fd_replay_slot_completed_t ) ); break;
-  case IN_KIND_SNAP:   memcpy( &ctx->snapshot_manifest, chunk_laddr, sizeof(fd_snapshot_manifest_t) ); break;
-  default:             FD_LOG_ERR(( "unhandled in_kind: %u in_idx: %lu", in_kind, in_idx ));
-  }
-}
-
-static void
-after_frag( ctx_t *             ctx,
-            ulong               in_idx,
-            ulong               seq FD_PARAM_UNUSED,
-            ulong               sig FD_PARAM_UNUSED,
-            ulong               sz FD_PARAM_UNUSED,
-            ulong               tsorig FD_PARAM_UNUSED,
-            ulong               tspub,
-            fd_stem_context_t * stem ) {
-  uint in_kind = ctx->in_kind[ in_idx ];
-  switch( in_kind ) {
-  case IN_KIND_REPLAY: {
-    ulong slot = ctx->replay_slot_info.slot;
-    if( slot==0UL ) {
-      if( FD_UNLIKELY( ctx->start_from_genesis ) ) {
-        FD_LOG_CRIT(( "invariant violation: start_from_genesis is true for slot 0" ));
-      }
-      ctx->start_from_genesis = 1;
-      ctx->root               = 0UL;
-      ctx->start_slot         = 0UL;
-      ctx->replay_time        = -fd_log_wallclock();
+returnable_frag( ctx_t *             ctx,
+                 ulong               in_idx,
+                 ulong               seq,
+                 ulong               sig,
+                 ulong               chunk,
+                 ulong               sz,
+                 ulong               ctl,
+                 ulong               tsorig,
+                 ulong               tspub,
+                 fd_stem_context_t * stem ) {
+  (void)seq;
+  (void)sz;
+  (void)ctl;
+  (void)tsorig;
+
+  switch( ctx->in_kind[ in_idx ] ) {
+    case IN_KIND_SNAP: {
+      ctx->credit = fd_ssmsg_sig_message( sig )==FD_SSMSG_DONE;
+      if( FD_LIKELY( fd_ssmsg_sig_message( sig )==FD_SSMSG_DONE ) ) return 0;
+
+      fd_snapshot_manifest_t const * manifest = fd_chunk_to_laddr_const( ctx->in_links[ in_idx ].mem, chunk );
+
+      ctx->initialized = 1;
+      ctx->root        = manifest->slot;
+      ctx->start_slot  = manifest->slot;
+      ctx->replay_time = -fd_log_wallclock();
 
-      /* Initialize RocksDB iterator for genesis case, similar to snapshot case */
       fd_rocksdb_root_iter_new( &ctx->rocksdb_root_iter );
       if( FD_UNLIKELY( fd_rocksdb_root_iter_seek( &ctx->rocksdb_root_iter, &ctx->rocksdb, ctx->root, &ctx->rocksdb_slot_meta, ctx->valloc ) ) ) {
         FD_LOG_CRIT(( "Failed at seeking rocksdb root iter for slot=%lu", ctx->root ));
       }
-      ctx->rocksdb_iter = rocksdb_create_iterator_cf( ctx->rocksdb.db, ctx->rocksdb.ro, ctx->rocksdb.cf_handles[FD_ROCKSDB_CFIDX_DATA_SHRED] );
-
-      FD_LOG_NOTICE(( "Genesis case: initialized RocksDB iterator for slot %lu", ctx->root ));
+      ctx->rocksdb_iter = rocksdb_create_iterator_cf(ctx->rocksdb.db, ctx->rocksdb.ro, ctx->rocksdb.cf_handles[FD_ROCKSDB_CFIDX_DATA_SHRED]);
+      break;
     }
+    case IN_KIND_REPLAY: {
+      if( FD_UNLIKELY( sig!=REPLAY_SIG_SLOT_COMPLETED ) ) return 0;
 
-    rocksdb_check_bank_hash( ctx, slot, &ctx->replay_slot_info.bank_hash );
-    if( FD_UNLIKELY( slot>=ctx->end_slot ) ) {
-      ctx->replay_time    += fd_log_wallclock();
-      double replay_time_s = (double)ctx->replay_time * 1e-9;
-      double sec_per_slot  = replay_time_s / (double)ctx->slot_cnt;
-      FD_LOG_NOTICE(( "replay completed - slots: %lu, elapsed: %6.6f s, sec/slot: %6.6f", ctx->slot_cnt, replay_time_s, sec_per_slot ));
-      FD_LOG_ERR(( "Backtest playback done." ));
-    } else {
+      fd_replay_slot_completed_t const * msg = fd_chunk_to_laddr_const( ctx->in_links[ in_idx ].mem, chunk );
 
-      /* Delay publishing by 1 slot otherwise there is a replay tile race when it tries to query the parent. */
+      if( FD_UNLIKELY( !ctx->initialized && msg->slot ) ) return 1;
+      ctx->initialized = 1;
 
-      fd_tower_slot_done_t * msg = fd_chunk_to_laddr( ctx->tower_out_mem, ctx->tower_out_chunk );
-      msg->root_slot             = ctx->staged_root;
-      msg->root_block_id         = ctx->staged_root_block_id;
-      msg->new_root              = 1;
-      msg->reset_block_id        = ctx->replay_slot_info.block_id;
+      ulong slot = msg->slot;
+      if( FD_UNLIKELY( !slot ) ) {
+        if( FD_UNLIKELY( ctx->start_from_genesis ) ) FD_LOG_CRIT(( "invariant violation: start_from_genesis is true for slot 0" ));
 
-      if( FD_UNLIKELY( ctx->staged_root!=ULONG_MAX || ctx->start_from_genesis ) ) fd_stem_publish( stem, ctx->tower_out_idx, 0UL, ctx->tower_out_chunk, sizeof(fd_hash_t), 0UL, tspub, fd_frag_meta_ts_comp( fd_tickcount() ) );
-      ctx->tower_out_chunk = fd_dcache_compact_next( ctx->tower_out_chunk, sizeof(fd_tower_slot_done_t), ctx->tower_out_chunk0, ctx->tower_out_wmark );
-      ctx->staged_root          = slot;
-      ctx->staged_root_block_id = ctx->replay_slot_info.block_id;
-      ctx->credit = 1;
-    }
-    break;
-  }
-  case IN_KIND_SNAP: {
-    if( FD_UNLIKELY( ctx->root != ULONG_MAX ) ) FD_LOG_CRIT(( "backtest got multiple manifests" ));
-    ctx->root        = ctx->snapshot_manifest.slot;
-    ctx->start_slot  = ctx->snapshot_manifest.slot;
-    ctx->replay_time = -fd_log_wallclock();
-
-    fd_rocksdb_root_iter_new( &ctx->rocksdb_root_iter );
-    if( FD_UNLIKELY( fd_rocksdb_root_iter_seek( &ctx->rocksdb_root_iter, &ctx->rocksdb, ctx->root, &ctx->rocksdb_slot_meta, ctx->valloc ) ) ) {
-      FD_LOG_CRIT(( "Failed at seeking rocksdb root iter for slot=%lu", ctx->root ));
+        ctx->start_from_genesis = 1;
+        ctx->root               = 0UL;
+        ctx->start_slot         = 0UL;
+        ctx->replay_time        = -fd_log_wallclock();
+
+        /* Initialize RocksDB iterator for genesis case, similar to snapshot case */
+        fd_rocksdb_root_iter_new( &ctx->rocksdb_root_iter );
+        if( FD_UNLIKELY( fd_rocksdb_root_iter_seek( &ctx->rocksdb_root_iter, &ctx->rocksdb, ctx->root, &ctx->rocksdb_slot_meta, ctx->valloc ) ) ) {
+          FD_LOG_CRIT(( "Failed at seeking rocksdb root iter for slot=%lu", ctx->root ));
+        }
+        ctx->rocksdb_iter = rocksdb_create_iterator_cf( ctx->rocksdb.db, ctx->rocksdb.ro, ctx->rocksdb.cf_handles[FD_ROCKSDB_CFIDX_DATA_SHRED] );
+
+        FD_LOG_NOTICE(( "Genesis case: initialized RocksDB iterator for slot %lu", ctx->root ));
+      }
+
+      rocksdb_check_bank_hash( ctx, slot, &msg->bank_hash );
+      if( FD_UNLIKELY( slot>=ctx->end_slot ) ) {
+        ctx->replay_time    += fd_log_wallclock();
+        double replay_time_s = (double)ctx->replay_time * 1e-9;
+        double sec_per_slot  = replay_time_s / (double)ctx->slot_cnt;
+        FD_LOG_NOTICE(( "replay completed - slots: %lu, elapsed: %6.6f s, sec/slot: %6.6f", ctx->slot_cnt, replay_time_s, sec_per_slot ));
+        FD_LOG_ERR(( "Backtest playback done." ));
+      } else {
+        /* Delay publishing by 1 slot otherwise there is a replay tile race when it tries to query the parent. */
+
+        fd_tower_slot_done_t * dst = fd_chunk_to_laddr( ctx->tower_out_mem, ctx->tower_out_chunk );
+        dst->root_slot      = ctx->staged_root;
+        dst->root_block_id  = ctx->staged_root_block_id;
+        dst->new_root       = 1;
+        dst->reset_block_id = msg->block_id;
+
+        if( FD_UNLIKELY( ctx->staged_root!=ULONG_MAX || ctx->start_from_genesis ) ) fd_stem_publish( stem, ctx->tower_out_idx, 0UL, ctx->tower_out_chunk, sizeof(fd_hash_t), 0UL, tspub, fd_frag_meta_ts_comp( fd_tickcount() ) );
+        ctx->tower_out_chunk = fd_dcache_compact_next( ctx->tower_out_chunk, sizeof(fd_tower_slot_done_t), ctx->tower_out_chunk0, ctx->tower_out_wmark );
+        ctx->staged_root          = slot;
+        ctx->staged_root_block_id = msg->block_id;
+        ctx->credit = 1;
+      }
+      break;
     }
-    ctx->rocksdb_iter = rocksdb_create_iterator_cf(ctx->rocksdb.db, ctx->rocksdb.ro, ctx->rocksdb.cf_handles[FD_ROCKSDB_CFIDX_DATA_SHRED]);
-    break;
-  }
-  default: FD_LOG_ERR(( "unhandled in_kind: %u in_idx: %lu", in_kind, in_idx ));
+    default: FD_LOG_ERR(( "unhandled in_kind: %u in_idx: %lu", ctx->in_kind[in_idx], in_idx ));
   }
+
+  return 0;
 }
 
 static void
@@ -419,6 +403,7 @@ unprivileged_init( fd_topo_t *      topo,
   ulong   scratch_top       = FD_SCRATCH_ALLOC_FINI  ( l, scratch_align()                        );
   FD_TEST( scratch_top == (ulong)scratch + scratch_footprint( tile ) );
 
+  ctx->initialized = 0;
   ctx->credit = 0;
 
   ctx->root        = ULONG_MAX;
@@ -493,10 +478,8 @@ unprivileged_init( fd_topo_t *      topo,
 #define STEM_CALLBACK_CONTEXT_TYPE  ctx_t
 #define STEM_CALLBACK_CONTEXT_ALIGN alignof(ctx_t)
 
-#define STEM_CALLBACK_AFTER_CREDIT  after_credit
-#define STEM_CALLBACK_BEFORE_FRAG   before_frag
-#define STEM_CALLBACK_DURING_FRAG   during_frag
-#define STEM_CALLBACK_AFTER_FRAG    after_frag
+#define STEM_CALLBACK_AFTER_CREDIT    after_credit
+#define STEM_CALLBACK_RETURNABLE_FRAG returnable_frag
 
 #include "../../disco/stem/fd_stem.c"
 
```

### src/flamenco/runtime/tests/run_backtest_ci.sh
```diff
@@ -11,7 +11,8 @@ src/flamenco/runtime/tests/run_ledger_backtest.sh -l testnet-321168308-v2.3.0 -y
 src/flamenco/runtime/tests/run_ledger_backtest.sh -l mainnet-327324660-v2.3.0 -y 4 -m 2000000 -e 327324660 -c 2.3.0
 src/flamenco/runtime/tests/run_ledger_backtest.sh -l devnet-370199634-v2.3.0 -y 3 -m 200000 -e 370199634 -c 2.3.0
 src/flamenco/runtime/tests/run_ledger_backtest.sh -l devnet-378683870-v2.3.0 -y 3 -m 2000000 -e 378683872 -c 2.3.0
-src/flamenco/runtime/tests/run_ledger_backtest.sh -l mainnet-330219081-v2.3.0 -y 4 -m 2000000 -e 330219082 -c 2.3.0
+# TODO: Disabled, seems corrupt.  Vote account cache has an account missing from the snapshot.
+# src/flamenco/runtime/tests/run_ledger_backtest.sh -l mainnet-330219081-v2.3.0 -y 4 -m 2000000 -e 330219082 -c 2.3.0
 src/flamenco/runtime/tests/run_ledger_backtest.sh -l devnet-372721907-v2.3.0 -y 3 -m 2000000 -e 372721910 -c 2.3.0
 src/flamenco/runtime/tests/run_ledger_backtest.sh -l mainnet-331691646-v2.3.0 -y 4 -m 2000000 -e 331691647 -c 2.3.0
 src/flamenco/runtime/tests/run_ledger_backtest.sh -l testnet-336218682-v2.3.0 -y 5 -m 2000000 -e 336218683 -c 2.3.0
```
