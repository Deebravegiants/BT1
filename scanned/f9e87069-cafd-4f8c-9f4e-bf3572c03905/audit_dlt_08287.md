# [?] flamenco: fix stack out-of-bounds when using the precompile feature offset

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-07-15
Source: https://github.com/firedancer-io/firedancer/commit/8dfe4e58935ff57fe86b2590340ca0b9b80e26d2
Type: security-commit

## Details
flamenco: fix stack out-of-bounds when using the precompile feature offset

## Patch
### src/flamenco/runtime/fd_runtime.c
```diff
@@ -2129,7 +2129,7 @@ fd_apply_builtin_program_feature_transitions( fd_exec_slot_ctx_t * slot_ctx,
   /* https://github.com/anza-xyz/agave/blob/c1080de464cfb578c301e975f498964b5d5313db/runtime/src/bank.rs#L6795-L6805 */
   fd_precompile_program_t const * precompiles = fd_precompiles();
   for( ulong i=0UL; i<fd_num_precompiles(); i++ ) {
-    if( FD_FEATURE_JUST_ACTIVATED_OFFSET( slot_ctx, precompiles[i].feature_offset ) ) {
+    if( precompiles[i].feature_offset != NO_ENABLE_FEATURE_ID && FD_FEATURE_JUST_ACTIVATED_OFFSET( slot_ctx, precompiles[i].feature_offset ) ) {
       fd_write_builtin_account( slot_ctx, *precompiles[i].pubkey, "", 0 );
     }
   }
```
