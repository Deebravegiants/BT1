# [?] txncache: fix deadlock when global txnpage limit is hit

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-07-14
Source: https://github.com/firedancer-io/firedancer/commit/e4e8c65b62e4b17ac4850395e4b2a4612d6ab48a
Type: security-commit

## Details
txncache: fix deadlock when global txnpage limit is hit

The early return caused by per-blockcache txnpage limit does not lead to
a deadlock.

## Patch
### src/flamenco/runtime/fd_txncache.c
```diff
@@ -181,7 +181,11 @@ fd_txncache_ensure_txnpage( fd_txncache_t * tc,
   if( FD_LIKELY( FD_ATOMIC_CAS( &blockcache->pages[ page_cnt ], (ushort)USHORT_MAX, (ushort)(USHORT_MAX-1UL) )==(ushort)USHORT_MAX ) ) {
     ulong txnpages_free_cnt = tc->shmem->txnpages_free_cnt;
     for(;;) {
-      if( FD_UNLIKELY( !txnpages_free_cnt ) ) return NULL;
+      if( FD_UNLIKELY( !txnpages_free_cnt ) ) {
+        blockcache->pages[ page_cnt ] = (ushort)USHORT_MAX;
+        FD_COMPILER_MFENCE();
+        return NULL;
+      }
       ulong old_txnpages_free_cnt = FD_ATOMIC_CAS( &tc->shmem->txnpages_free_cnt, (ushort)txnpages_free_cnt, (ushort)(txnpages_free_cnt-1UL) );
       if( FD_LIKELY( old_txnpages_free_cnt==txnpages_free_cnt ) ) break;
       txnpages_free_cnt = old_txnpages_free_cnt;
@@ -198,10 +202,11 @@ fd_txncache_ensure_txnpage( fd_txncache_t * tc,
     return txnpage;
   } else {
     ushort txnpage_idx = blockcache->pages[ page_cnt ];
-    while( FD_UNLIKELY( txnpage_idx>=USHORT_MAX-1UL ) ) {
+    while( FD_UNLIKELY( txnpage_idx==(ushort)(USHORT_MAX-1UL) ) ) {
       txnpage_idx = blockcache->pages[ page_cnt ];
       FD_SPIN_PAUSE();
     }
+    if( FD_UNLIKELY( txnpage_idx==(ushort)USHORT_MAX ) ) return NULL;
     return &tc->txnpages[ txnpage_idx ];
   }
 }
```

### src/flamenco/runtime/test_txncache.c
```diff
@@ -286,6 +286,133 @@ test_purge_stale_frees_pages( uchar * scratch0,
   }
 }
 
+void
+test_purge_stale_global( uchar * scratch0,
+                         uchar * scratch1 ) {
+  FD_LOG_NOTICE(( "TEST PURGE STALE GLOBAL" ));
+
+  /* max_live_slots=4, max_txn_per_slot=16384.
+
+     This gives:
+       max_active_slots           = 155
+       max_txnpages_per_blockhash = 156
+       max_txnpages               = 309
+       FD_TXNCACHE_TXNS_PER_PAGE  = 16384
+
+     Unlike test_purge_stale and test_purge_stale_frees_pages, which
+     trigger purge_stale via the per-blockhash page limit, this test
+     triggers purge_stale via the global max_txnpages limit.
+
+     We allocate 155 pages of stale txns in the root's blockcache, then
+     154 more pages spread across 153 child blockcaches with valid txns.
+     The next page allocation hits the global exhaustion path. */
+
+  fd_txncache_shmem_t * shtc = fd_txncache_shmem_join( fd_txncache_shmem_new( scratch0, 4UL, FD_TXNCACHE_TXNS_PER_PAGE, 0, 0UL ) );
+  FD_TEST( shtc );
+  fd_txncache_t * tc = fd_txncache_join( fd_txncache_new( scratch1, shtc ) );
+  FD_TEST( tc );
+
+  /* Step 1: Create root R0 with blockhash 0. */
+
+  fd_txncache_fork_id_t root = fd_txncache_attach_child( tc, NULL_FORK );
+  fd_txncache_finalize_fork( tc, root, 0UL, BLOCKHASH(0UL) );
+
+  /* Step 2: Fill R0's blockcache with 155 pages of stale txns via a
+     single child fork that we cancel afterwards. */
+
+  ulong const stale_id_base = 1000000UL;
+  ulong const r0_pages      = 155UL;
+  ulong const total_stale   = r0_pages*FD_TXNCACHE_TXNS_PER_PAGE;
+
+  uchar blockhash_buf[ 32UL ] = {0};
+  uchar txnhash_buf  [ 32UL ] = {0};
+
+  FD_LOG_NOTICE(( "inserting %lu stale txns into R0 (%lu pages)", total_stale, r0_pages ));
+
+  fd_txncache_fork_id_t loser = fd_txncache_attach_child( tc, root );
+  FD_STORE( ulong, blockhash_buf, 0UL );
+  for( ulong i=0UL; i<total_stale; i++ ) {
+    FD_STORE( ulong, txnhash_buf, stale_id_base+i );
+    fd_txncache_insert( tc, loser, blockhash_buf, txnhash_buf );
+  }
+  fd_txncache_cancel_fork( tc, loser );
+
+  /* Step 3: Build a chain of 153 finalized child forks F_1..F_153, each
+     with its own blockhash, plus an unfinalized inserter fork at the
+     tip.  The inserter is used to insert into ancestor blockcaches.
+
+     Pool budget: 1 (R0) + 153 (F_1..F_153) + 1 (inserter) = 155, which
+     exactly fills the blockcache pool. */
+
+  ulong const chain_len = 153UL;
+  fd_txncache_fork_id_t f_chain[ chain_len ];
+  fd_txncache_fork_id_t prev = root;
+  for( ulong i=0UL; i<chain_len; i++ ) {
+    f_chain[ i ] = fd_txncache_attach_child( tc, prev );
+    fd_txncache_finalize_fork( tc, f_chain[ i ], 0UL, BLOCKHASH(2000UL+i) );
+    prev = f_chain[ i ];
+  }
+  fd_txncache_fork_id_t inserter = fd_txncache_attach_child( tc, prev );
+
+  /* Step 4: Insert valid txns through the inserter:
+       - 1 valid txn into each of F_1..F_152 (1 page each, 152 pages).
+       - 2*16384 valid txns into F_153 (2 full pages).
+
+     After this, total pages allocated = 155 (R0) + 152 + 2 = 309 =
+     max_txnpages.  txnpages_free_cnt is now 0. */
+
+  ulong const valid_id_base    = 5000000UL;
+  ulong const f153_blockhash   = 2000UL+chain_len-1UL;
+  ulong const f153_valid_count = 2UL*FD_TXNCACHE_TXNS_PER_PAGE;
+
+  FD_LOG_NOTICE(( "inserting %lu valid txns into F_1..F_152 (1 page each)", chain_len-1UL ));
+  for( ulong i=0UL; i<chain_len-1UL; i++ ) {
+    FD_STORE( ulong, blockhash_buf, 2000UL+i );
+    FD_STORE( ulong, txnhash_buf,   valid_id_base+i );
+    fd_txncache_insert( tc, inserter, blockhash_buf, txnhash_buf );
+  }
+
+  FD_LOG_NOTICE(( "inserting %lu valid txns into F_153 (filling 2 pages)", f153_valid_count ));
+  FD_STORE( ulong, blockhash_buf, f153_blockhash );
+  for( ulong i=0UL; i<f153_valid_count; i++ ) {
+    FD_STORE( ulong, txnhash_buf, valid_id_base+chain_len+i );
+    fd_txncache_insert( tc, inserter, blockhash_buf, txnhash_buf );
+  }
+
+  /* Step 5: Trigger global exhaustion.  purge_stale() then compacts
+     R0's blockcache, dropping all 155 pages of stale txns and freeing
+     them back to the global pool. */
+
+  ulong const trigger_id = 9000000UL;
+  FD_LOG_NOTICE(( "inserting trigger txn (should trigger global purge_stale)" ));
+  FD_STORE( ulong, blockhash_buf, f153_blockhash );
+  FD_STORE( ulong, txnhash_buf,   trigger_id );
+  fd_txncache_insert( tc, inserter, blockhash_buf, txnhash_buf );
+
+  /* Step 6: Verify all valid txns survived. */
+
+  FD_LOG_NOTICE(( "verifying valid txns survived purge" ));
+  for( ulong i=0UL; i<chain_len-1UL; i++ ) {
+    FD_STORE( ulong, blockhash_buf, 2000UL+i );
+    FD_STORE( ulong, txnhash_buf,   valid_id_base+i );
+    FD_TEST( fd_txncache_query( tc, inserter, blockhash_buf, txnhash_buf ) );
+  }
+  FD_STORE( ulong, blockhash_buf, f153_blockhash );
+  for( ulong i=0UL; i<f153_valid_count; i++ ) {
+    FD_STORE( ulong, txnhash_buf, valid_id_base+chain_len+i );
+    FD_TEST( fd_txncache_query( tc, inserter, blockhash_buf, txnhash_buf ) );
+  }
+  FD_STORE( ulong, txnhash_buf, trigger_id );
+  FD_TEST( fd_txncache_query( tc, inserter, blockhash_buf, txnhash_buf ) );
+
+  /* Spot-check that stale txns in R0 are not queryable. */
+  FD_STORE( ulong, blockhash_buf, 0UL );
+  for( ulong i=0UL; i<10UL; i++ ) {
+    FD_STORE( ulong, txnhash_buf, stale_id_base+i );
+    FD_TEST( !fd_txncache_query( tc, inserter, blockhash_buf, txnhash_buf ) );
+  }
+}
+
 int
 main( int     argc,
       char ** argv ) {
@@ -305,6 +432,7 @@ main( int     argc,
   test_advance_root( scratch0, scratch1 );
   test_purge_stale( scratch0, scratch1 );
   test_purge_stale_frees_pages( scratch0, scratch1 );
+  test_purge_stale_global( scratch0, scratch1 );
 
   FD_LOG_NOTICE(( "pass" ));
   fd_halt();
```
