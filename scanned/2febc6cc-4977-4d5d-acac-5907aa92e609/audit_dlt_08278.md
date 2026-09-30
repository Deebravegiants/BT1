# [?] gui: fix crash when requesting old leader slot

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-10-14
Source: https://github.com/firedancer-io/firedancer/commit/52bf62ef89c215f700efa8df345ec6607f8174cc
Type: security-commit

## Details
gui: fix crash when requesting old leader slot

## Patch
### src/disco/gui/fd_gui.c
```diff
@@ -1338,7 +1338,7 @@ fd_gui_clear_slot( fd_gui_t *      gui,
     lslot->slot                        = _slot;
     lslot->leader_start_time           = LONG_MAX;
     lslot->leader_end_time             = LONG_MAX;
-    lslot->tile_timers_sample_cnt      = ULONG_MAX;
+    lslot->tile_timers_sample_cnt      = 0UL;
     lslot->txs.microblocks_upper_bound = USHORT_MAX;
     lslot->txs.begin_microblocks       = 0U;
     lslot->txs.end_microblocks         = 0U;
```

### src/disco/gui/fd_gui_printf.c
```diff
@@ -1355,8 +1355,10 @@ fd_gui_printf_slot_transactions_request( fd_gui_t * gui,
       jsonp_close_object( gui->http );
 
       fd_gui_leader_slot_t * lslot = fd_gui_get_leader_slot( gui, _slot );
-      int overwritten               = (gui->pack_txn_idx - lslot->txs.start_offset)>FD_GUI_TXN_HISTORY_SZ;
+      int overwritten               = lslot && (gui->pack_txn_idx - lslot->txs.start_offset)>FD_GUI_TXN_HISTORY_SZ;
       int processed_all_microblocks = lslot &&
+                                      lslot->txs.start_offset!=ULONG_MAX &&
+                                      lslot->txs.end_offset!=ULONG_MAX &&
                                       lslot->txs.microblocks_upper_bound!=USHORT_MAX &&
                                       lslot->txs.begin_microblocks==lslot->txs.end_microblocks &&
                                       lslot->txs.begin_microblocks==lslot->txs.microblocks_upper_bound;
```
