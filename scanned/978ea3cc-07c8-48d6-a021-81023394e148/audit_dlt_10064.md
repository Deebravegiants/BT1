# [?] Fix race condition in rpc.online_reps (#5073)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2026-05-20
Source: https://github.com/nanocurrency/nano-node/commit/509d46d4b4422949f37e1145b3e265e364e2a92d
Type: security-commit

## Details
Fix race condition in rpc.online_reps (#5073)

## Patch
### nano/rpc_test/rpc.cpp
```diff
@@ -5272,9 +5272,7 @@ TEST (rpc, online_reps)
 	auto send (system.wallet (0)->send_action (nano::dev::genesis_key.pub, new_rep, node1->config.receive_minimum.number ()));
 	ASSERT_NE (nullptr, send);
 	ASSERT_TIMELY (10s, node2->block (send->hash ()));
-	auto receive (system.wallet (1)->receive_action (send->hash (), new_rep, node1->config.receive_minimum.number (), send->destination ()));
-	ASSERT_NE (nullptr, receive);
-	ASSERT_TIMELY (5s, node2->block (receive->hash ()));
+	ASSERT_TIMELY (5s, !node2->ledger.any.account_head (node2->ledger.tx_begin_read (), new_rep).is_zero ());
 	auto change (system.wallet (0)->change_action (nano::dev::genesis_key.pub, new_rep));
 	ASSERT_NE (nullptr, change);
 	ASSERT_TIMELY (5s, node2->block (change->hash ()));
```
