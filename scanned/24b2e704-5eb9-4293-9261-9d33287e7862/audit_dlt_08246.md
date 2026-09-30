# [?] accdb: fix reentrant alut lookup

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-06-08
Source: https://github.com/firedancer-io/firedancer/commit/8ab79809d931316fe758fb417c1d52a01fd913d7
Type: security-commit

## Details
accdb: fix reentrant alut lookup

## Patch
### src/discof/replay/fd_sched.c
```diff
@@ -2279,19 +2279,32 @@ fd_sched_parse_txn( fd_sched_t * sched, fd_sched_block_t * block, fd_sched_alut_
       /* test/fuzz: no accdb to query, so treat ALUT txns as serializing. */
       serializing = 1;
     } else {
+      /* Copy the slot hashes sysvar out and release the read BEFORE
+         resolving the ALTs.  fd_runtime_load_txn_address_lookup_tables
+         issues its own fd_accdb_read_one per lookup table, and the accdb
+         acquire state is a single non-nestable flag — holding this read
+         open across that call would trip the IDLE assertion in
+         fd_accdb_acquire.  The slot_hashes view aliases the record data,
+         so it must view the copy, not the released record. */
+      static uchar slot_hashes_buf[ FD_SYSVAR_SLOT_HASHES_BINCODE_SZ ];
+      ulong        slot_hashes_sz = 0UL;
+      int          have_slot_hashes = 0;
       fd_acc_t ro = fd_accdb_read_one( alut_ctx->accdb, alut_ctx->fork_id, fd_sysvar_slot_hashes_id.uc );
-      if( FD_LIKELY( ro.lamports ) ) {
-        fd_slot_hashes_t slot_hashes_view[1];
-        if( FD_LIKELY( fd_sysvar_slot_hashes_view( slot_hashes_view, ro.data, ro.data_len ) ) ) {
-          serializing = !!fd_runtime_load_txn_address_lookup_tables( txn, payload, alut_ctx->accdb, alut_ctx->fork_id, alut_ctx->els, slot_hashes_view, sched->aluts );
-          sched->metrics->alut_success_cnt += (uint)!serializing;
-        } else {
-          serializing = 1;
-        }
+      if( FD_LIKELY( ro.lamports && ro.data_len<=sizeof(slot_hashes_buf) ) ) {
+        fd_memcpy( slot_hashes_buf, ro.data, ro.data_len );
+        slot_hashes_sz   = ro.data_len;
+        have_slot_hashes = 1;
+      }
+      fd_accdb_unread_one( alut_ctx->accdb, &ro );
+
+      fd_slot_hashes_t slot_hashes_view[1];
+      if( FD_LIKELY( have_slot_hashes &&
+                     fd_sysvar_slot_hashes_view( slot_hashes_view, slot_hashes_buf, slot_hashes_sz ) ) ) {
+        serializing = !!fd_runtime_load_txn_address_lookup_tables( txn, payload, alut_ctx->accdb, alut_ctx->fork_id, alut_ctx->els, slot_hashes_view, sched->aluts );
+        sched->metrics->alut_success_cnt += (uint)!serializing;
       } else {
         serializing = 1;
       }
-      fd_accdb_unread_one( alut_ctx->accdb, &ro );
     }
   }
 
```
