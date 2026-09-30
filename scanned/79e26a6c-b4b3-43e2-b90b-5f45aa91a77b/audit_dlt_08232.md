# [?] stem: guard fd_stem_advance against credit underflow

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-09-01
Source: https://github.com/firedancer-io/firedancer/commit/3ebe361fc2db053682dd1b8d885fa849b1339a76
Type: security-commit

## Details
stem: guard fd_stem_advance against credit underflow

we are doing this in publish already

## Patch
### src/disco/stem/fd_stem.h
```diff
@@ -71,6 +71,9 @@ fd_stem_advance( fd_stem_context_t * stem,
   ulong * seqp = &stem->seqs[ out_idx ];
   ulong   seq  = *seqp;
   if( FD_LIKELY( stem->out_reliable[ out_idx ] ) ) {
+    if( FD_UNLIKELY( stem->cr_avail[ out_idx ]<stem->cr_decrement_amount ) ) { /* Ensure producer BURST is set correctly */
+      FD_LOG_ERR(( "BURST underprovisioned out_idx=%lu cr_avail=%lu min_cr_avail=%lu cr_decrement_amount=%lu", out_idx, stem->cr_avail[ out_idx ], *stem->min_cr_avail, stem->cr_decrement_amount ));
+    }
     stem->cr_avail[ out_idx ] -= stem->cr_decrement_amount;
     *stem->min_cr_avail        = fd_ulong_min( stem->cr_avail[ out_idx ], *stem->min_cr_avail );
   }
```
