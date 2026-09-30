# [?] dedup: fix inter-tile oob read

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-04-02
Source: https://github.com/firedancer-io/firedancer/commit/6b9d394d936b9dafd3fffe9bdecccd5ed5b94f64
Type: security-commit

## Details
dedup: fix inter-tile oob read

Reported via the bounty by @eternal_Zellic. This really is not a security bug because the oob read can only be triggered by a compromised tile, and this oob read does not provide any primitive useful towards achieving inter-tile RCE. Still it is could hygiene to move the check before the usage.

## Patch
### src/disco/dedup/fd_dedup_tile.c
```diff
@@ -183,15 +183,16 @@ after_frag( fd_dedup_ctx_t *    ctx,
     /* Make sure bundles don't contain a duplicate transaction inside
        the bundle, which would not be valid. */
 
+    if( FD_UNLIKELY( ctx->bundle_idx>4UL ) ) FD_LOG_ERR(( "bundle_idx %lu > 4", ctx->bundle_idx ));
+
     for( ulong i=0UL; i<ctx->bundle_idx; i++ ) {
       if( !memcmp( ctx->bundle_signatures[ i ], fd_txn_m_payload( txnm )+txn->signature_off, 64UL ) ) {
         is_dup = 1;
         break;
       }
     }
 
-    if( FD_UNLIKELY( ctx->bundle_idx>4UL ) ) FD_LOG_ERR(( "bundle_idx %lu > 4", ctx->bundle_idx ));
-    else if( FD_UNLIKELY( ctx->bundle_idx==4UL ) ) ctx->bundle_idx++;
+    if( FD_UNLIKELY( ctx->bundle_idx==4UL ) ) ctx->bundle_idx++;
     else fd_memcpy( ctx->bundle_signatures[ ctx->bundle_idx++ ], fd_txn_m_payload( txnm )+txn->signature_off, 64UL );
   }
 
```
