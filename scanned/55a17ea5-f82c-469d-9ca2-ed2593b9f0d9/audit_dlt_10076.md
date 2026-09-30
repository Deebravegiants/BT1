# [?] Possible race condition fix in ledger_walker.ladder_geometry test (#3497)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2021-10-12
Source: https://github.com/nanocurrency/nano-node/commit/fb49976f021d9828d3eb4a997d767b66968b59cc
Type: security-commit

## Details
Possible race condition fix in ledger_walker.ladder_geometry test (#3497)

## Patch
### nano/core_test/ledger_walker.cpp
```diff
@@ -151,6 +151,7 @@ TEST (ledger_walker, ladder_geometry)
 	{
 		system.wallet (0)->insert_adhoc (keys[itr].prv);
 		const auto block = system.wallet (0)->send_action (nano::dev::genesis_key.pub, keys[itr].pub, 1000);
+		ASSERT_TRUE (block);
 		ASSERT_TIMELY (3s, 1 + (itr + 1) * 2 == node->ledger.cache.cemented_count);
 	}
 
@@ -166,14 +167,12 @@ TEST (ledger_walker, ladder_geometry)
 
 		const auto send = system.wallet (0)->send_action (keys[source_index].pub, keys[destination_index].pub, amounts_to_send[itr]);
 		ASSERT_TRUE (send);
-
 		ASSERT_TIMELY (3s, 1 + keys.size () * 2 + (itr + 1) * 2 == node->ledger.cache.cemented_count);
 	}
 
 	ASSERT_TRUE (last_destination);
-	const auto transaction = node->ledger.store.tx_begin_read ();
 	nano::account_info last_destination_info{};
-	const auto last_destination_read_error = node->ledger.store.account.get (transaction, *last_destination, last_destination_info);
+	const auto last_destination_read_error = node->ledger.store.account.get (node->ledger.store.tx_begin_read (), *last_destination, last_destination_info);
 	ASSERT_FALSE (last_destination_read_error);
 
 	// This is how we expect chains to look like (for 3 accounts and 10 amounts to be sent)
@@ -192,7 +191,7 @@ TEST (ledger_walker, ladder_geometry)
 			nano::amount previous_balance{};
 			if (!block->previous ().is_zero ())
 			{
-				const auto previous_block = node->ledger.store.block.get_no_sideband (transaction, block->previous ());
+				const auto previous_block = node->ledger.store.block.get_no_sideband (node->ledger.store.tx_begin_read (), block->previous ());
 				previous_balance = previous_block->balance ();
 			}
 
@@ -211,7 +210,7 @@ TEST (ledger_walker, ladder_geometry)
 			nano::amount previous_balance{};
 			if (!block->previous ().is_zero ())
 			{
-				const auto previous_block = node->ledger.store.block.get_no_sideband (transaction, block->previous ());
+				const auto previous_block = node->ledger.store.block.get_no_sideband (node->ledger.store.tx_begin_read (), block->previous ());
 				previous_balance = previous_block->balance ();
 			}
 
```
