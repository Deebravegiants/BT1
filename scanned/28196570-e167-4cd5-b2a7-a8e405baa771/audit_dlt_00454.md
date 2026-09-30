# [?] progcache: fix rec lock underflow

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-05-27
Source: https://github.com/firedancer-io/firedancer/commit/8b4e864b3d30230dd40d08cf26556f21eb1af7df
Type: security-commit

## Details
progcache: fix rec lock underflow

Fixes a race between search_chain recovery (unread after map_chain
seqlock failure) and record allocation (resets lock to 0), thus
underflowing rec lock to USHORT_MAX and causing a deadlock.

## Patch
### src/flamenco/progcache/fd_progcache.c
```diff
@@ -298,9 +298,7 @@ fd_progcache_shmem_delete( fd_progcache_shmem_t * shmem ) {
   FD_TEST( !shmem->spill.lock.value );
   FD_TEST( !shmem->clock.lock.value );
   fd_progcache_txn_t * txn0 = fd_wksp_laddr_fast( wksp, shmem->txn.ele_gaddr );
-  fd_progcache_rec_t * rec0 = fd_wksp_laddr_fast( wksp, shmem->rec.ele_gaddr );
   for( ulong i=0UL; i<shmem->txn.max; i++ ) FD_TEST( !txn0[ i ].lock.value );
-  for( ulong i=0UL; i<shmem->rec.max; i++ ) FD_TEST( !rec0[ i ].lock.value );
 
   /* Free all fd_alloc allocations made, individually
      (FIXME consider walking the element pool instead of the map?) */
```

### src/flamenco/progcache/fd_progcache_reclaim.c
```diff
@@ -42,12 +42,9 @@ rec_reclaim( fd_progcache_join_t * join,
   fd_racesan_hook( "prog_reclaim:post_unlink" );
 
   /* Drain existing users
+     Leave record in locked state (lock is reset when allocating) */
 
-     Records are removed from recm (index) before the record is selected
-     for reclamation.  Therefore, it is not necessary to acquire a lock.
-     It is fine to wait for existing users to drain. */
-
-  if( FD_UNLIKELY( FD_VOLATILE_CONST( rec->lock.value ) ) ) return 0;
+  if( FD_UNLIKELY( !fd_rwlock_trywrite( &rec->lock ) ) ) return 0;
 
   /* All users are gone, deallocate record */
 
```
