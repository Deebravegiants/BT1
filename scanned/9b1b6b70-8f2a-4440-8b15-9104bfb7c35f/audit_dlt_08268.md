# [?] runtime: fix crash if fee collector is missing

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-01-12
Source: https://github.com/firedancer-io/firedancer/commit/b03a1dd6f842a6dd309b6acd9472d7698ad8f766
Type: security-commit

## Details
runtime: fix crash if fee collector is missing

Fixes a recent regression

## Patch
### src/flamenco/runtime/fd_runtime.c
```diff
@@ -257,7 +257,7 @@ fd_runtime_settle_fees( fd_bank_t *               bank,
 
   /* Credit fee collector, creating it if necessary */
   fd_accdb_rw_t rw[1];
-  fd_accdb_open_rw( accdb, rw, xid, leader, 0UL, 0 );
+  fd_accdb_open_rw( accdb, rw, xid, leader, 0UL, FD_ACCDB_FLAG_CREATE );
   fd_lthash_value_t prev_hash[1];
   fd_hashes_account_lthash( leader, rw->meta, fd_accdb_ref_data_const( rw->ro ), prev_hash );
 
```
