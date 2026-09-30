# [?] fuzz: fix funk deadlock in txn harness

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-02-25
Source: https://github.com/firedancer-io/firedancer/commit/931abf68b4ccaff6bb50ed8daed4e84be3fa000d
Type: security-commit

## Details
fuzz: fix funk deadlock in txn harness

## Patch
### src/flamenco/runtime/tests/fd_exec_instr_test.c
```diff
@@ -721,8 +721,10 @@ _txn_context_create_and_exec( fd_exec_instr_test_runner_t *      runner,
       ( rent->exemption_threshold     <      0.0 ) |
       ( rent->exemption_threshold     >    999.0 ) |
       ( rent->lamports_per_uint8_year > UINT_MAX ) |
-      ( rent->burn_percent            >      100 ) )
+      ( rent->burn_percent            >      100 ) ) {
+    fd_funk_end_write( runner->funk );
     return NULL;
+  }
 
   /* Blockhash queue is given in txn message. We need to populate the following two fields:
      - slot_ctx->slot_bank.block_hash_queue
```
