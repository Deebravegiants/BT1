# [?] Fix OOB read in test_accounts_resize_delta

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-06-03
Source: https://github.com/firedancer-io/firedancer/commit/4e3dfd8cb469bb0080a77fcd0be86965c3e0bc2c
Type: security-commit

## Details
Fix OOB read in test_accounts_resize_delta

## Patch
### src/flamenco/runtime/tests/test_accounts_resize_delta.c
```diff
@@ -208,6 +208,7 @@ execute_txn( test_env_t *     env,
   ulong sz = txn_serialize( txn_p.payload, num_signers, signatures, num_signers,
                             0UL, num_readonly_unsigned, account_keys_cnt, account_keys,
                             &blockhash, instrs, instr_cnt );
+  txn_p.payload_sz = sz;
   FD_TEST( fd_txn_parse( txn_p.payload, sz, TXN( &txn_p ), NULL ) );
 
   env->txn_in.txn              = &txn_p;
```
