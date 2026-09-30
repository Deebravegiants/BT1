# [?] para_pool_fix: bug fix for race condition in para_pool_acquire

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-03-25
Source: https://github.com/firedancer-io/firedancer/commit/e5440af743ca60374c5cf4a7e992c02ead28d130
Type: security-commit

## Details
para_pool_fix: bug fix for race condition in para_pool_acquire

## Patch
### src/util/tmpl/fd_pool_para.c
```diff
@@ -673,18 +673,27 @@ POOL_(acquire)( POOL_(t) *   join,
 
       ulong ele_nxt = POOL_(private_idx)( ele0[ ele_idx ].POOL_NEXT );
 
-      if( FD_UNLIKELY( (ele_nxt>=ele_max) & (!POOL_(idx_is_null)( ele_nxt )) ) ) { /* opt for not corrupt */
-        err = FD_POOL_ERR_CORRUPT;
-        break;
-      }
-
-      ulong new_ver_top = POOL_(private_vidx)( ver+2UL, ele_nxt );
-
-      if( FD_LIKELY( POOL_(private_cas)( _v, ver_top, new_ver_top )==ver_top ) ) { /* opt for low contention */
-        ele = ele0 + ele_idx;
-        break;
+      if( FD_UNLIKELY( (ele_nxt>=ele_max) & (!POOL_(idx_is_null)( ele_nxt )) ) ) { /* ele_nxt is invalid, opt for valid */
+        /* It is possible that another thread acquired ele_idx and
+           repurposed ele_idx's POOL_NEXT (storing something in it that
+           isn't a valid pool value) between when we read ver_top and
+           when we read ele_idx's POOL_NEXT above.  If so, the pool
+           version would be changed from what we read above.  We thus
+           only signal ERR_CORRUPT if the version number hasn't changed
+           since we read it. */
+
+        if( FD_UNLIKELY( POOL_(private_vidx_ver)( *_v )==ver ) ) {
+          err = FD_POOL_ERR_CORRUPT;
+          break;
+        }
+      } else { /* ele_nxt is valid */
+        ulong new_ver_top = POOL_(private_vidx)( ver+2UL, ele_nxt );
+
+        if( FD_LIKELY( POOL_(private_cas)( _v, ver_top, new_ver_top )==ver_top ) ) { /* opt for low contention */
+          ele = ele0 + ele_idx;
+          break;
+        }
       }
-
     } else if( FD_UNLIKELY( !blocking ) ) { /* opt for blocking */
 
       err = FD_POOL_ERR_AGAIN;
```
