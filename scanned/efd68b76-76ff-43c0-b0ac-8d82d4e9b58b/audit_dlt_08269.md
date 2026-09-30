# [?] fix(hfokrk): lamport pct ulong overflow (#7577)

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-12-16
Source: https://github.com/firedancer-io/firedancer/commit/dec00304527de476eea6438bbb83a5fe0403f516
Type: security-commit

## Details
fix(hfokrk): lamport pct ulong overflow (#7577)

## Patch
### src/choreo/hfork/fd_hfork.c
```diff
@@ -9,7 +9,8 @@ check( fd_hfork_t *  hfork,
        fd_hash_t *   our_bank_hash ) {
 
   if( FD_LIKELY( candidate->checked ) ) return; /* already checked this bank hash against our own */
-  if( FD_LIKELY( candidate->stake * 100UL / total_stake < 52UL ) ) return; /* not enough stake to compare */
+  double pct = (double)candidate->stake * 100.0 / (double)total_stake;
+  if( FD_LIKELY( pct < 52.0 ) ) return; /* not enough stake to compare */
 
   if( FD_UNLIKELY( dead ) ) {
     char msg[ 4096UL ];
@@ -19,7 +20,7 @@ check( fd_hfork_t *  hfork,
                                   candidate->slot,
                                   _block_id,
                                   candidate->cnt,
-                                  100.0*(double)candidate->stake/(double)total_stake ) );
+                                  pct ) );
 
     if( FD_UNLIKELY( hfork->fatal ) ) FD_LOG_ERR    (( "%s", msg ));
     else                              FD_LOG_WARNING(( "%s", msg ));
@@ -34,7 +35,7 @@ check( fd_hfork_t *  hfork,
                                   candidate->slot,
                                   _block_id,
                                   candidate->cnt,
-                                  100.0*(double)candidate->stake/(double)total_stake,
+                                  pct,
                                   _bank_hash ) );
 
     if( FD_UNLIKELY( hfork->fatal ) ) FD_LOG_ERR    (( "%s", msg ));
```
