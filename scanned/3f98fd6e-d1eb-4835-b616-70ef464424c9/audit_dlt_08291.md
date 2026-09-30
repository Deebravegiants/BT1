# [?] runtime: fix off-by-one oob write

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-05-06
Source: https://github.com/firedancer-io/firedancer/commit/7cd06e928bff350d93f98986b61ba6b73980c25f
Type: security-commit

## Details
runtime: fix off-by-one oob write

## Patch
### src/flamenco/runtime/program/fd_bpf_program_util.c
```diff
@@ -450,12 +450,8 @@ fd_bpf_scan_and_create_bpf_program_cache_entry_para( fd_exec_slot_ctx_t *    slo
       for( ; NULL != rec; rec = fd_funk_txn_next_rec( funk, rec ) ) {
         if( rec->flags & FD_FUNK_REC_FLAG_ERASE ) continue;
         recs[ rec_cnt ] = rec;
-
-        if( rec_cnt==65536UL ) {
-          break;
-        }
-
         rec_cnt++;
+        if( FD_UNLIKELY( rec_cnt==65536UL ) ) break;
       }
 
       /* Pass in args */
```
