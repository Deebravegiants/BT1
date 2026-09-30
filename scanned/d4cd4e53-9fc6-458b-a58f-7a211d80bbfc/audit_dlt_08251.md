# [?] accdb: fix zero lamport account race condition

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-05-22
Source: https://github.com/firedancer-io/firedancer/commit/3a941f1efd4e3381f3b1d7e817c0d8a1167d84a2
Type: security-commit

## Details
accdb: fix zero lamport account race condition

- clarify funk reclamation rules
- fix a race condition when handling deleted accounts

## Patch
### src/flamenco/accdb/fd_accdb_impl_v1.c
```diff
@@ -7,13 +7,75 @@
 FD_STATIC_ASSERT( alignof(fd_accdb_user_v1_t)<=alignof(fd_accdb_user_t), layout );
 FD_STATIC_ASSERT( sizeof (fd_accdb_user_v1_t)<=sizeof(fd_accdb_user_t),  layout );
 
+/* Note on memory reclamation:
+
+   ### Background
+
+   fd_accdb is a multi-versioned database. Every time an account changes
+   in a slot, a copy of that account is saved, in case the runtime needs
+   to revert to an earlier revision.
+
+   Space is finite, so stale revisions have to be deleted (i.e. the
+   underlying memory is "reclaimed").  When a slot gets rooted, ancient
+   account revisions can be deleted.  A revision is ancient when it
+   predates the root slot, and is not visible at the root slot.
+
+   When all revisions of an account are deleted, accdb must free all
+   resources associated with that account.  (Otherwise, the index will
+   run out of memory after long enough operation.)  The simplest way to
+   do that is to ensure all rooted revisions have non-zero lamports.
+   (And delete a revision with zero lamports when its slot gets rooted.)
+
+   ### Reclaim points
+
+   To summarize, fd_accdb reclaims revisions at the following points.
+
+   1. revision shadowed by a root slot
+   2. revision reaches zero lampots at the root slot
+
+   ### Reclaim safety
+
+   "Reclamation" means immediately freeing the account record and heap
+   allocations.  The runtime must guarantee that no references to an
+   account are active before it is reclaimed.
+
+   The system guarantees safety with reclaim rule 1 as follows:
+   - each tile only has one active fork view (xid) at a time
+   - all active references of a tile must have been obtained via that
+     fork view (when switching forks, all references are released)
+   - the replay tile does not advance the root unless it is certain that
+     no tile has a fork view for the previous root
+   Therefore, it is impossible for a compliant tile to have an accdb
+   reference that is susceptible to reclaim per rule 1.
+
+   The accdb API guarantees safety with reclaim rule 2 as follows:
+   - accdb APIs never return references to a zero-lamport account
+     (they return NULL, i.e. "account not found" instead)
+   - the accdb APIs themselves safely recover from overrun if reclaim
+     per rule 2 kicks in during an accdb_open_{ro,rw} operation */
+
+
+/* fd_accdb_found_rec_t describes an unsafe reference to a revision.
+   (i.e. the revision discovered is potentially susceptible to reclaim,
+   and it is the caller's responsibility to verify pointer stability.) */
+
+struct fd_accdb_found_rec {
+  fd_funk_rec_t *   rec; /* unstable */
+  fd_funk_txn_xid_t xid;
+  ulong             lamports;
+};
+typedef struct fd_accdb_found_rec fd_accdb_found_rec_t;
+
+/* fd_accdb_search_chain searches for a record revision in an index
+   hash chain.  Robust under concurrent modification via seqlock. */
+
 static int
 fd_accdb_search_chain( fd_funk_t const *          funk,
                        fd_accdb_lineage_t const * lineage,
                        ulong                      chain_idx,
                        fd_funk_rec_key_t const *  key,
-                       fd_funk_rec_t **           out_rec ) {
-  *out_rec = NULL;
+                       fd_accdb_found_rec_t *     out_rec ) {
+  *out_rec = (fd_accdb_found_rec_t){0};
 
   fd_funk_rec_map_shmem_t const *               shmap     = funk->rec_map->map;
   fd_funk_rec_map_shmem_private_chain_t const * chain_tbl = fd_funk_rec_map_shmem_private_chain_const( shmap, 0UL );
@@ -68,20 +130,43 @@ fd_accdb_search_chain( fd_funk_t const *          funk,
 next:
     ele_idx = ele_next;
   }
+  fd_funk_txn_xid_t xid       = { .ul={ ULONG_MAX,ULONG_MAX } };
+  ulong             val_gaddr = 0UL;
+  if( best ) val_gaddr = best->val_gaddr;
   fd_racesan_hook( "accdb_search_chain:seqlock_check" );
   if( FD_UNLIKELY( atomic_load_explicit( ver_cnt_p, memory_order_acquire )!=ver_cnt ) ) {
     return FD_MAP_ERR_AGAIN;
   }
   if( FD_UNLIKELY( !best && ele_idx!=FD_FUNK_REC_IDX_NULL ) ) {
     FD_LOG_CRIT(( "fd_accdb_search_chain detected malformed chain (%lu): found more nodes than chain header indicated (%lu)", chain_idx, cnt ));
   }
-  *out_rec = best;
+
+  ulong lamports = 0UL;
+  if( best && val_gaddr ) {
+    fd_account_meta_t const * meta = fd_wksp_laddr_fast( funk->wksp, val_gaddr );
+    lamports = meta->lamports;
+    xid      = *best->pair.xid;
+  }
+  fd_racesan_hook( "accdb_search_chain:seqlock_check2" );
+  if( FD_UNLIKELY( atomic_load_explicit( ver_cnt_p, memory_order_acquire )!=ver_cnt ) ) {
+    return FD_MAP_ERR_AGAIN;
+  }
+  *out_rec = (fd_accdb_found_rec_t){
+    .rec      = best,
+    .xid      = xid,
+    .lamports = lamports
+  };
   return FD_MAP_SUCCESS;
 }
 
-fd_accdb_ro_t *
+/* fd_accdb_peek_funk returns a read-only reference to an account.
+   Zero lamports are treated special:  If the account reached zero
+   lamports prior to this xid, NULL is returned.  Otherwise, the
+   tombstone for that account is returned. */
+
+static fd_accdb_found_rec_t *
 fd_accdb_peek_funk( fd_accdb_user_v1_t *      accdb,
-                    fd_accdb_ro_t *           ro,
+                    fd_accdb_found_rec_t *    rec,
                     fd_funk_txn_xid_t const * xid,
                     void const *              address ) {
   fd_funk_t const * funk = accdb->funk;
@@ -96,22 +181,28 @@ fd_accdb_peek_funk( fd_accdb_user_v1_t *      accdb,
   ulong chain_idx = (hash & (rec_map->map->chain_cnt-1UL) );
 
   /* Traverse chain for candidate */
-  fd_funk_rec_t * rec = NULL;
   for(;;) {
-    int err = fd_accdb_search_chain( accdb->funk, accdb->lineage, chain_idx, key, &rec );
+    int err = fd_accdb_search_chain( accdb->funk, accdb->lineage, chain_idx, key, rec );
     if( FD_LIKELY( err==FD_MAP_SUCCESS ) ) break;
     FD_SPIN_PAUSE();
     /* FIXME backoff */
   }
-  if( !rec ) return NULL;
+  if( !rec->rec ) return NULL; /* not found */
+
+  fd_racesan_hook( "accdb:post_peek" );
+  return rec;
+}
 
-  memcpy( ro->ref->address, address, 32UL );
+static fd_accdb_ro_t *
+fd_accdb_ro_init_funk( fd_accdb_ro_t *        ro,
+                       fd_accdb_found_rec_t * rec,
+                       fd_wksp_t *            wksp ) {
+  memcpy( ro->ref->address, rec->rec->pair.key, 32UL );
   ro->ref->accdb_type = FD_ACCDB_TYPE_V1;
   ro->ref->ref_type   = FD_ACCDB_REF_RO;
-  ro->ref->user_data  = (ulong)rec;
+  ro->ref->user_data  = (ulong)rec->rec;
   ro->ref->user_data2 = 0UL;
-  ro->meta            = fd_funk_val( rec, funk->wksp );
-  fd_racesan_hook( "accdb_peek_funk:post_val" );
+  ro->meta            = fd_wksp_laddr_fast( wksp, rec->rec->val_gaddr );
   return ro;
 }
 
@@ -138,10 +229,13 @@ fd_accdb_user_v1_open_ro_multi( fd_accdb_user_t *         accdb,
   fd_accdb_lineage_set_fork( v1->lineage, v1->funk, xid );
   ulong addr_laddr = (ulong)address;
   for( ulong i=0UL; i<cnt; i++ ) {
-    void const *    addr_i = (void const *)( (ulong)addr_laddr + i*32UL );
-    if( !fd_accdb_peek_funk( v1, &ro[i], xid, addr_i ) ) {
+    void const * addr_i = (void const *)( (ulong)addr_laddr + i*32UL );
+    fd_accdb_found_rec_t found;
+    if( !fd_accdb_peek_funk( v1, &found, xid, addr_i ) ||
+        !found.lamports ) {
       fd_accdb_ro_init_empty( &ro[i], addr_i );
     } else {
+      fd_accdb_ro_init_funk( &ro[i], &found, v1->funk->wksp );
       v1->base.ro_active++;
     }
   }
@@ -177,19 +271,23 @@ fd_accdb_user_v1_open_rw( fd_accdb_user_t *         accdb,
 
   /* Query old record value */
 
-  fd_accdb_ro_t ro[1];
-  if( FD_UNLIKELY( !fd_accdb_peek_funk( v1, ro, xid, address ) ) ) {
+  fd_accdb_found_rec_t found;
+  if( FD_UNLIKELY( !fd_accdb_peek_funk( v1, &found, xid, address ) ) ) {
     /* Record not found */
     if( flag_create ) return fd_accdb_funk_create( v1->funk, rw, txn, address, data_max );
     return NULL;
   }
 
-  if( !ro->meta->lamports ) {
-    /* Record previously deleted */
-    if( !flag_create ) return NULL;
+  if( FD_UNLIKELY( !found.lamports && !flag_create ) ) return NULL;
+
+  /* Zero lamport references are only stable at the current XID, since
+     writable forks cannot be rooted (reclaim rule 2) */
+  if( FD_UNLIKELY( !found.lamports && !fd_funk_txn_xid_eq( &found.xid, xid ) ) ) {
+    return fd_accdb_funk_create( v1->funk, rw, txn, address, data_max );
   }
 
-  fd_funk_rec_t * rec = (fd_funk_rec_t *)ro->ref->user_data;
+  fd_funk_rec_t * rec = found.rec;
+  fd_accdb_ro_t ro[1]; fd_accdb_ro_init_funk( ro, &found, v1->funk->wksp );
   if( fd_funk_txn_xid_eq( rec->pair.xid, xid ) ) {
 
     /* Mutable record found, modify in-place */
```

### src/flamenco/accdb/test_accdb_v1.c
```diff
@@ -343,6 +343,53 @@ test_account_creation( fd_accdb_user_t *         accdb,
   FD_TEST( accdb->base.ro_active==0 && accdb->base.rw_active==0 );
 }
 
+static void
+test_zero_balance_ro( fd_accdb_admin_t * admin,
+                      fd_accdb_user_t *  accdb ) {
+  static uchar const key_live[ 32 ] = { 10 };
+  static uchar const key_dead[ 32 ] = { 11 };
+
+  add_account_funk( accdb, key_live, 500UL );
+  add_account_funk( accdb, key_dead,   0UL );
+
+  fd_funk_txn_xid_t root = fd_accdb_root_get( admin );
+  fd_funk_txn_xid_t xid = { .ul={ 7UL, 0UL } };
+  fd_accdb_attach_child( admin, &root, &xid );
+
+  fd_accdb_ro_t ro[1];
+  FD_TEST( fd_accdb_open_ro( accdb, ro, &xid, key_live ) );
+  FD_TEST( fd_accdb_ref_lamports( ro )==500UL );
+  fd_accdb_close_ro( accdb, ro );
+  FD_TEST( !fd_accdb_open_ro( accdb, ro, &xid, key_dead ) );
+
+  fd_accdb_advance_root( admin, &xid );
+  fd_accdb_v1_clear( admin );
+}
+
+static void
+test_zero_balance_rw( fd_accdb_admin_t * admin,
+                      fd_accdb_user_t *  accdb ) {
+  static uchar const key_dead[ 32 ] = { 11 };
+
+  add_account_funk( accdb, key_dead, 0UL );
+
+  fd_funk_txn_xid_t root = fd_accdb_root_get( admin );
+  fd_funk_txn_xid_t xid = { .ul={ 8UL, 0UL } };
+  fd_accdb_attach_child( admin, &root, &xid );
+
+  fd_accdb_rw_t rw[1];
+  fd_accdb_ro_t ro[1];
+  FD_TEST( !fd_accdb_open_rw( accdb, rw, &xid, key_dead, 0UL, 0 ) );
+  for( ulong i=0UL; i<1000000UL; i++ ) {
+    FD_TEST( !fd_accdb_open_ro( accdb, ro, &xid, key_dead ) );
+    FD_TEST( fd_accdb_open_rw( accdb, rw, &xid, key_dead, 0UL, FD_ACCDB_FLAG_CREATE ) );
+    fd_accdb_close_rw( accdb, rw ); /* creates a tombstone */
+  }
+
+  fd_accdb_advance_root( admin, &xid );
+  fd_accdb_v1_clear( admin );
+}
+
 static void
 test_tombstone( fd_accdb_admin_t * admin,
                 fd_accdb_user_t *  accdb ) {
@@ -407,6 +454,8 @@ test_simple( fd_wksp_t * wksp ) {
   test_truncate_nonexist( admin, accdb );
   test_truncate_inplace ( admin, accdb );
   test_truncate_copy    ( admin, accdb );
+  test_zero_balance_ro  ( admin, accdb );
+  test_zero_balance_rw  ( admin, accdb );
 
   fd_accdb_v1_clear( admin );
   test_tombstone( admin, accdb );
```
