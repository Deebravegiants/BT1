# [?] lightningd: fix crash in onchaind replay.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2025-03-02
Source: https://github.com/ElementsProject/lightning/commit/1605c13c1a8330e5071cb8e383d860445e270ae1
Type: security-commit

## Details
lightningd: fix crash in onchaind replay.

If a tx has already spent one tx we're watching, and it spends another,
we try to add it to the hash table twice, which isn't allowed:

```
2025-02-28T23:00:32.155Z **BROKEN** lightningd: backtrace: ../sysdeps/unix/sysv/linux/raise.c:51 (__GI_raise) 0x7fab2e363d51
2025-02-28T23:00:32.155Z **BROKEN** lightningd: backtrace: ./stdlib/abort.c:79 (__GI_abort) 0x7fab2e34d536
2025-02-28T23:00:32.155Z **BROKEN** lightningd: backtrace: ./assert/assert.c:92 (__assert_fail_base) 0x7fab2e34d40e
2025-02-28T23:00:32.155Z **BROKEN** lightningd: backtrace: ./assert/assert.c:101 (__GI___assert_fail) 0x7fab2e35c6d1
2025-02-28T23:00:32.155Z **BROKEN** lightningd: backtrace: lightningd/onchain_control.c:48 (replay_tx_hash_add) 0x556928d4e114
2025-02-28T23:00:32.155Z **BROKEN** lightningd: backtrace: lightningd/onchain_control.c:365 (replay_watch_tx) 0x556928d4e114
2025-02-28T23:00:32.155Z **BROKEN** lightningd: backtrace: lightningd/onchain_control.c:419 (replay_block) 0x556928d4e835
2025-02-28T23:00:32.155Z **BROKEN** lightningd: backtrace: lightningd/bitcoind.c:506 (getrawblockbyheight_callback) 0x556928d1c791
```

Fixes: #8131
Reported-by: Vincenzo Palazzo
Changelog-None: introduced this release, when we banned htable dups.
Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### lightningd/onchain_control.c
```diff
@@ -362,7 +362,11 @@ static void replay_watch_tx(struct channel *channel,
 	rtx->blockheight = blockheight;
 	rtx->tx = clone_bitcoin_tx(rtx, tx);
 
-	replay_tx_hash_add(channel->onchaind_replay_watches, rtx);
+	/* We might already be watching, in which case don't re-add! */
+	if (replay_tx_hash_get(channel->onchaind_replay_watches, &rtx->txid))
+		tal_free(rtx);
+	else
+		replay_tx_hash_add(channel->onchaind_replay_watches, rtx);
 }
 
 /* We've finished replaying, turn any txs left into live watches */
```
