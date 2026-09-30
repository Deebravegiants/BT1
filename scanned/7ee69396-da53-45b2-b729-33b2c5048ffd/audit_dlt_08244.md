# [?] shred: harden returned constant on overflow

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-06-22
Source: https://github.com/firedancer-io/firedancer/commit/d661b2d97fdf8035808f8c861440741db034d10d
Type: security-commit

## Details
shred: harden returned constant on overflow

## Patch
### src/ballet/wsample/fd_wsample.c
```diff
@@ -162,11 +162,10 @@ static inline int
 compute_height( ulong   leaf_cnt,
                 ulong * out_height,
                 ulong * out_internal_cnt ) {
-  /* This max is a bit conservative.  The actual max is height <= 25,
-     and leaf_cnt < 5^25 approx 2^58.  A tree that large would take an
-     astronomical amount of memory, so we just retain this max for the
-     moment. */
-  if( FD_UNLIKELY( leaf_cnt >= UINT_MAX-2UL ) ) return -1;
+  /* If we made the sentinel values larger, we could take larger
+     leaf_cnt, but at INT_MAX this would still use an astronomical
+     amount of memory, so we retain ths max for the moment. */
+  if( FD_UNLIKELY( leaf_cnt >= (ulong)INT_MAX ) ) return -1;
 
   ulong height   = 0;
   ulong internal = 0UL;
@@ -294,6 +293,7 @@ fd_wsample_new_init( void             * shmem,
 
   fd_wsample_t *  sampler = (fd_wsample_t *)shmem;
 
+  sampler->total_cnt         = 0UL;
   sampler->total_weight      = 0UL;
   sampler->unremoved_cnt     = 0UL;
   sampler->unremoved_weight  = 0UL;
```

### src/ballet/wsample/fd_wsample.h
```diff
@@ -37,14 +37,13 @@ typedef struct fd_wsample_private fd_wsample_t;
                  ((ele_cnt)<=    531441UL)?    66430UL :                   \
                  ((ele_cnt)<=   4782969UL)?   597871UL :                   \
                  ((ele_cnt)<=  43046721UL)?  5380840UL :                   \
-                 ((ele_cnt)<= 387420489UL)? 48427561UL :                   \
-                 ((ele_cnt)<=3486784401UL)?435848050UL : 3922632451UL ))   \
+                 ((ele_cnt)<= 387420489UL)? 48427561UL : 435848050UL  ))
 
 /* fd_wsample_{align, footprint} give the alignment and footprint
    respectively required to create a weighted sampler with at most
    ele_cnt stake weights.  If restore_enabled is zero, calls to
    wsample_restore_all will be no-ops, but the footprint required will
-   be smaller. ele_cnt in [0, UINT_MAX-2) (note, not ULONG MAX).
+   be smaller. ele_cnt in [0, INT_MAX) (note, not ULONG MAX).
 
    fd_wsample_{join,leave} join and leave a memory region formatted as a
    weighted sampler, respectively.  They both are simple casts.
@@ -95,7 +94,7 @@ void *            fd_wsample_delete   ( void * shmem  );
    weighted sampler to own its own rng, but this is done to facilitate
    sharing of rngs between weighted samplers, which is useful for
    Turbine.  ele_cnt specifies the number of elements that can be
-   sampled from and must be less than UINT_MAX.  If restore_enabled is
+   sampled from and must be less than INT_MAX.  If restore_enabled is
    set to 0, fd_wsample_restore_all will not work but the required
    footprint is smaller.  opt_hint gives a hint of the shape of the
    weights and the style of queries that will be most common; this hint
```

### src/ballet/wsample/test_wsample.c
```diff
@@ -389,15 +389,15 @@ test_footprint( void ) {
     FD_TEST( FD_WSAMPLE_FOOTPRINT( i, 0 ) == fd_wsample_footprint( i, 0 ) );
     FD_TEST( FD_WSAMPLE_FOOTPRINT( i, 1 ) == fd_wsample_footprint( i, 1 ) );
   }
-  for( ulong i=729UL; i<UINT_MAX; i*=3UL ) {
+  for( ulong i=729UL; i<(ulong)INT_MAX; i*=3UL ) {
     FD_TEST( FD_WSAMPLE_FOOTPRINT( i-1UL, 0 ) == fd_wsample_footprint( i-1UL, 0 ) );
     FD_TEST( FD_WSAMPLE_FOOTPRINT( i-1UL, 1 ) == fd_wsample_footprint( i-1UL, 1 ) );
     FD_TEST( FD_WSAMPLE_FOOTPRINT( i,     0 ) == fd_wsample_footprint( i,     0 ) );
     FD_TEST( FD_WSAMPLE_FOOTPRINT( i,     1 ) == fd_wsample_footprint( i,     1 ) );
     FD_TEST( FD_WSAMPLE_FOOTPRINT( i+1UL, 0 ) == fd_wsample_footprint( i+1UL, 0 ) );
     FD_TEST( FD_WSAMPLE_FOOTPRINT( i+1UL, 1 ) == fd_wsample_footprint( i+1UL, 1 ) );
   }
-  for( ulong i=512UL; i<UINT_MAX; i*=2UL ) {
+  for( ulong i=512UL; i<(ulong)INT_MAX; i*=2UL ) {
     FD_TEST( FD_WSAMPLE_FOOTPRINT( i-1UL, 0 ) == fd_wsample_footprint( i-1UL, 0 ) );
     FD_TEST( FD_WSAMPLE_FOOTPRINT( i-1UL, 1 ) == fd_wsample_footprint( i-1UL, 1 ) );
     FD_TEST( FD_WSAMPLE_FOOTPRINT( i,     0 ) == fd_wsample_footprint( i,     0 ) );
```

### src/disco/shred/fd_shred_dest.c
```diff
@@ -292,8 +292,16 @@ fd_shred_dest_compute_first( fd_shred_dest_t          * sdest,
   int any_staked_candidates = sdest->staked_cnt > (ulong)source_validator_is_staked;
   for( ulong i=0UL; i<shred_cnt; i++ ) {
     fd_wsample_seed_rng( sdest->staked, dest_hash_outputs[ i ] );
-    /* Map FD_WSAMPLE_INDETERMINATE to FD_SHRED_DEST_NO_DEST */
-    if( FD_LIKELY( any_staked_candidates ) ) out[i] = (fd_shred_dest_idx_t)fd_ulong_min( fd_wsample_sample( sdest->staked ), FD_SHRED_DEST_NO_DEST );
+    /* Map FD_WSAMPLE_INDETERMINATE (UINT_MAX-1) and FD_WSAMPLE_EMPTY
+       (UINT_MAX) to FD_SHRED_DEST_NO_DEST.  If wsample returns either
+       sentinel value, it will be cast to -2 or -1, so the max will be
+       -1, as desired.  Otherwise, since wsample guarantees the returned
+       index is in [0, INT_MAX], it will remain non-negative when cast
+       to an int, so the max will be that value. */
+    FD_STATIC_ASSERT( (int)FD_WSAMPLE_INDETERMINATE             <=-1, wsample_val );
+    FD_STATIC_ASSERT( (int)FD_WSAMPLE_EMPTY                     <=-1, wsample_val );
+    FD_STATIC_ASSERT( FD_SHRED_DEST_NO_DEST==(fd_shred_dest_idx_t)-1, wsample_val );
+    if( FD_LIKELY( any_staked_candidates ) ) out[i] = (fd_shred_dest_idx_t)fd_int_max( (int)fd_wsample_sample( sdest->staked ), -1 );
     else                                     out[i] = (fd_shred_dest_idx_t)sample_unstaked_noprepare( sdest, sdest->source_validator_orig_idx );
   }
   fd_wsample_restore_all( sdest->staked );
@@ -441,7 +449,7 @@ fd_shred_dest_compute_children( fd_shred_dest_t          * sdest,
       if( FD_UNLIKELY( sample==FD_WSAMPLE_INDETERMINATE ) ) break;
 
       if( FD_UNLIKELY( cursor == my_idx + stride*(stored_cnt+1UL) ) ) {
-        out[ stored_cnt*out_stride + i ] = (ushort)sample;
+        out[ stored_cnt*out_stride + i ] = (fd_shred_dest_idx_t)sample;
         stored_cnt++;
       }
       cursor++;
@@ -459,7 +467,7 @@ fd_shred_dest_compute_children( fd_shred_dest_t          * sdest,
       if( FD_UNLIKELY( sample==FD_WSAMPLE_EMPTY ) ) break;
 
       if( FD_UNLIKELY( cursor == my_idx + stride*(stored_cnt+1UL) ) ) {
-        out[ stored_cnt*out_stride + i ] = (ushort)sample;
+        out[ stored_cnt*out_stride + i ] = (fd_shred_dest_idx_t)sample;
         stored_cnt++;
       }
       cursor++;
```
