# [?] lightningd: fix crash when blocks come it fast.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2023-10-25
Source: https://github.com/ElementsProject/lightning/commit/985d0db1434829ba084ba5a1f269d6996bcb8af7
Type: security-commit

## Details
lightningd: fix crash when blocks come it fast.

This is from the recent rework, as revealed by CI:

```
2023-10-25T00:57:29.1394358Z lightningd-2 2023-10-25T00:27:22.912Z **BROKEN** lightningd: FATAL SIGNAL 6 (version 4ba8a31-modded)
2023-10-25T00:57:29.1395035Z lightningd-2 2023-10-25T00:27:22.912Z **BROKEN** lightningd: backtrace: common/daemon.c:38 (send_backtrace) 0x5574aa3c29dd
2023-10-25T00:57:29.1395670Z lightningd-2 2023-10-25T00:27:22.913Z **BROKEN** lightningd: backtrace: common/daemon.c:75 (crashdump) 0x5574aa3c2b6f
2023-10-25T00:57:29.1396230Z lightningd-2 2023-10-25T00:27:22.913Z **BROKEN** lightningd: backtrace: (null):0 ((null)) 0x7f7cce44251f
2023-10-25T00:57:29.1396768Z lightningd-2 2023-10-25T00:27:22.913Z **BROKEN** lightningd: backtrace: (null):0 ((null)) 0x7f7cce4969fc
2023-10-25T00:57:29.1397297Z lightningd-2 2023-10-25T00:27:22.913Z **BROKEN** lightningd: backtrace: (null):0 ((null)) 0x7f7cce442475
2023-10-25T00:57:29.1397945Z lightningd-2 2023-10-25T00:27:22.913Z **BROKEN** lightningd: backtrace: (null):0 ((null)) 0x7f7cce4287f2
2023-10-25T00:57:29.1398616Z lightningd-2 2023-10-25T00:27:22.913Z **BROKEN** lightningd: backtrace: ccan/ccan/tal/tal.c:95 (call_error) 0x5574aa56d36a
2023-10-25T00:57:29.1399308Z lightningd-2 2023-10-25T00:27:22.913Z **BROKEN** lightningd: backtrace: ccan/ccan/tal/tal.c:169 (check_bounds) 0x5574aa56d565
2023-10-25T00:57:29.1399968Z lightningd-2 2023-10-25T00:27:22.913Z **BROKEN** lightningd: backtrace: ccan/ccan/tal/tal.c:179 (to_tal_hdr) 0x5574aa56d5b7
2023-10-25T00:57:29.1400613Z lightningd-2 2023-10-25T00:27:22.913Z **BROKEN** lightningd: backtrace: ccan/ccan/tal/tal.c:514 (tal_free) 0x5574aa56e058
2023-10-25T00:57:29.1401364Z lightningd-2 2023-10-25T00:27:22.913Z **BROKEN** lightningd: backtrace: lightningd/chaintopology.c:204 (rebroadcast_txs) 0x5574aa313ccc
2023-10-25T00:57:29.1402128Z lightningd-2 2023-10-25T00:27:22.913Z **BROKEN** lightningd: backtrace: lightningd/chaintopology.c:843 (updates_complete) 0x5574aa315a6b
2023-10-25T00:57:29.1402884Z lightningd-2 2023-10-25T00:27:22.913Z **BROKEN** lightningd: backtrace: lightningd/chaintopology.c:1055 (get_new_block) 0x5574aa31659f
```

Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### lightningd/chaintopology.c
```diff
@@ -201,7 +201,7 @@ static void rebroadcast_txs(struct chain_topology *topo)
 	tal_free(cleanup_ctx);
 
 	/* Free explicitly in case we were called because a block came in. */
-	tal_free(topo->rebroadcast_timer);
+	topo->rebroadcast_timer = tal_free(topo->rebroadcast_timer);
 
 	/* Nothing to broadcast?  Reset timer immediately */
 	if (*num_rebroadcast_remaining == 0)
```
