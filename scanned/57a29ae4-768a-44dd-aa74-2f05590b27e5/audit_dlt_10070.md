# [?] Fix race condition in unit test active_transactions.activate_inactive

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2024-04-14
Source: https://github.com/nanocurrency/nano-node/commit/9553d9b7d6f20eb4aafa1ec0f0f0ee8b5d6a4f51
Type: security-commit

## Details
Fix race condition in unit test active_transactions.activate_inactive

The stats counters are updated in a callback called after the block
has been confirmed.

## Patch
### nano/core_test/active_transactions.cpp
```diff
@@ -1248,9 +1248,9 @@ TEST (active_transactions, activate_inactive)
 	ASSERT_TIMELY (5s, node.block_confirmed (send2->hash ()));
 	ASSERT_TIMELY (5s, node.block_confirmed (send->hash ()));
 
-	ASSERT_EQ (1, node.stats.count (nano::stat::type::confirmation_observer, nano::stat::detail::inactive_conf_height, nano::stat::dir::out));
-	ASSERT_EQ (1, node.stats.count (nano::stat::type::confirmation_observer, nano::stat::detail::active_quorum, nano::stat::dir::out));
-	ASSERT_EQ (0, node.stats.count (nano::stat::type::confirmation_observer, nano::stat::detail::active_conf_height, nano::stat::dir::out));
+	ASSERT_TIMELY_EQ (5s, 1, node.stats.count (nano::stat::type::confirmation_observer, nano::stat::detail::inactive_conf_height, nano::stat::dir::out));
+	ASSERT_TIMELY_EQ (5s, 1, node.stats.count (nano::stat::type::confirmation_observer, nano::stat::detail::active_quorum, nano::stat::dir::out));
+	ASSERT_ALWAYS_EQ (50ms, 0, node.stats.count (nano::stat::type::confirmation_observer, nano::stat::detail::active_conf_height, nano::stat::dir::out));
 
 	// The first block was not active so no activation takes place
 	ASSERT_FALSE (node.active.active (open->qualified_root ()) || node.block_confirmed_or_being_confirmed (open->hash ()));
```
