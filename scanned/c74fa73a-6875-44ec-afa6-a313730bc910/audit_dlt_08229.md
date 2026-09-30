# [?] repair: fix one bit OOB

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-09-11
Source: https://github.com/firedancer-io/firedancer/commit/4b55d07316ef8be892e64622a3e767d77062b407
Type: security-commit

## Details
repair: fix one bit OOB

## Patch
### src/discof/repair/fd_policy.c
```diff
@@ -289,7 +289,7 @@ fd_policy_next( fd_policy_t * policy, fd_reqlim_t * dedup, fd_forest_t * forest,
       uint nonce = fd_rnonce_ss_compute( policy->rnonce_ss, 0, ele->slot, 0U, now );
       out = fd_repair_highest_shred( repair, fd_policy_peer_select( policy ), now_ms, nonce, ele->slot, 0 );
       ele->req_highest_cnt++;
-    } else if( FD_LIKELY( ele->slot == highest_known_slot ) ) {
+    } else if( FD_LIKELY( ele->slot == highest_known_slot && (ulong)cand_idx < forest->shred_max ) ) {
       ulong key = fd_reqlim_key( FD_REPAIR_KIND_SHRED, ele->slot, cand_idx );
       if( FD_UNLIKELY( fd_reqlim_query( dedup, key, now ) ) ) {
         policy->skip.slot      = ele->slot;
```
