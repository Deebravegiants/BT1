# [?] pack: fix pacing cnt potential overflow

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-08-21
Source: https://github.com/firedancer-io/firedancer/commit/a2adaa63b7fe123c1ff51438502e616456d41377
Type: security-commit

## Details
pack: fix pacing cnt potential overflow

## Patch
### src/disco/pack/fd_pack_tile.c
```diff
@@ -612,10 +612,9 @@ after_credit( fd_pack_ctx_t *     ctx,
 
   long now = fd_tickcount();
 
-  int pacing_execle_cnt = (int)fd_pack_pacing_enabled_bank_cnt( ctx->pacer, now );
-
   ulong execle_cnt = ctx->execle_cnt;
 
+  int pacing_execle_cnt = (int)fd_ulong_min( fd_pack_pacing_enabled_bank_cnt( ctx->pacer, now ), execle_cnt );
 
   /* If any execle are busy, check one of the busy ones see if it is
      still busy. */
```
