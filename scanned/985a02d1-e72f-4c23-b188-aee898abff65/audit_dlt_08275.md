# [?] solcap: fix oob write check off-by-one

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-10-24
Source: https://github.com/firedancer-io/firedancer/commit/39fd8eef2785f61eb93c8102ec332b3d8d348632
Type: security-commit

## Details
solcap: fix oob write check off-by-one

## Patch
### src/flamenco/runtime/fd_runtime.c
```diff
@@ -931,7 +931,7 @@ fd_runtime_buffer_solcap_account_update( fd_txn_account_t *        account,
   fd_hashes_account_lthash( account->pubkey, meta, data, lthash );
 
   /* Calculate message size */
-  if( FD_UNLIKELY( capture_ctx->account_updates_len > FD_CAPTURE_CTX_MAX_ACCOUNT_UPDATES ) ) {
+  if( FD_UNLIKELY( capture_ctx->account_updates_len >= FD_CAPTURE_CTX_MAX_ACCOUNT_UPDATES ) ) {
     FD_LOG_CRIT(( "cannot buffer solcap account update. this should never happen" ));
     return;
   }
```
