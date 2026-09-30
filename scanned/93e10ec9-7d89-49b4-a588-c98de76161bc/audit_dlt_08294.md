# [?] replay, hashes: fix EAH deadlock

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-04-07
Source: https://github.com/firedancer-io/firedancer/commit/ee30321ce325c662f58fe50b98f6d6024354774a
Type: security-commit

## Details
replay, hashes: fix EAH deadlock

## Patch
### src/flamenco/runtime/fd_runtime.c
```diff
@@ -3971,6 +3971,8 @@ fd_runtime_publish_old_txns( fd_exec_slot_ctx_t * slot_ctx,
     fd_runtime_checkpt( capture_ctx, slot_ctx, slot_ctx->slot_bank.slot );
   }
 
+  int do_eah = 0;
+
   uint depth = 0;
   for( fd_funk_txn_t * txn = slot_ctx->funk_txn; txn; txn = fd_funk_txn_parent(txn, &txnpool) ) {
     if( ++depth == (FD_RUNTIME_NUM_ROOT_BLOCKS - 1 ) ) {
@@ -4010,7 +4012,7 @@ fd_runtime_publish_old_txns( fd_exec_slot_ctx_t * slot_ctx,
 
       if( txn->xid.ul[0] >= epoch_bank->eah_start_slot ) {
         if( !FD_FEATURE_ACTIVE( slot_ctx->slot_bank.slot, slot_ctx->epoch_ctx->features, accounts_lt_hash ) ) {
-          fd_accounts_hash( slot_ctx->funk, &slot_ctx->slot_bank, tpool, &slot_ctx->slot_bank.epoch_account_hash, runtime_spad, 0, &slot_ctx->epoch_ctx->features );
+          do_eah = 1;
         }
         epoch_bank->eah_start_slot = ULONG_MAX;
       }
@@ -4021,6 +4023,17 @@ fd_runtime_publish_old_txns( fd_exec_slot_ctx_t * slot_ctx,
 
   fd_funk_txn_end_write( slot_ctx->funk );
 
+  /* Do the EAH calculation after we have released the Funk lock, to avoid a deadlock */
+  if( FD_UNLIKELY( do_eah ) ) {
+    fd_accounts_hash( slot_ctx->funk,
+      &slot_ctx->slot_bank,
+      tpool,
+      &slot_ctx->slot_bank.epoch_account_hash,
+      runtime_spad,
+      0,
+      &slot_ctx->epoch_ctx->features );
+  }
+
   return 0;
 }
 
```
