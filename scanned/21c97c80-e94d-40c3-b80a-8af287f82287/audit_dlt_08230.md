# [?] wsample: avoid unsigned pointer offset overflow in left sum lookups (#11402)

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-09-10
Source: https://github.com/firedancer-io/firedancer/commit/edc21b92a2c2a0dc7aa68e5e8d78d0950cb931ce
Type: security-commit

## Details
wsample: avoid unsigned pointer offset overflow in left sum lookups (#11402)

## Patch
### src/ballet/wsample/fd_wsample.c
```diff
@@ -458,7 +458,7 @@ fd_wsample_map_sample_i( fd_wsample_t const * sampler,
     ulong orig_m1 = temp[ -1 ];    ulong orig_Rm1 = temp[ R-1UL ];
     temp[ -1 ] = 0UL;              temp[ R-1UL ] = S;
     ulong li  = temp[ child_idx     ];
-    ulong lm1 = temp[ child_idx-1UL ];
+    ulong lm1 = temp[ (long)child_idx-1L ];
     temp[ -1 ] = orig_m1;          temp[ R-1UL ] = orig_Rm1;
 #endif
 
@@ -534,7 +534,7 @@ fd_wsample_find_weight( fd_wsample_t const * sampler,
     /* If child_idx < R-1, we can compute the weight easily.  If
        child_idx==R-1, the computation is S - left_sum[ R-2 ], but we
        don't know S, so we need to continue up the tree. */
-    lm1  += fd_ulong_if( child_idx>0UL, tree[ parent ].left_sum[ child_idx-1UL ], 0UL );
+    lm1  += fd_ulong_if( child_idx>0UL, tree[ parent ].left_sum[ (long)child_idx-1L ], 0UL );
     if( FD_LIKELY( child_idx<R-1UL ) ) {
       li = tree[ parent ].left_sum[ child_idx ];
       break;
```
