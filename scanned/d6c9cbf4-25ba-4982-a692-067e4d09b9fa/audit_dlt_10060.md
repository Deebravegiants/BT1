# [?] Fix offset overflow in account_history RPC

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2026-07-25
Source: https://github.com/nanocurrency/nano-node/commit/70ef4dabd5d6d0f9bd437be2f9a2f440bb8f862e
Type: security-commit

## Details
Fix offset overflow in account_history RPC

## Patch
### nano/node/json_handler.cpp
```diff
@@ -2960,21 +2960,15 @@ void nano::json_handler::account_history ()
 		auto block = node.ledger.any.block_get (transaction, hash);
 		if (block)
 		{
+			// Saturate on client-supplied offsets; height 0 and heights past the frontier resolve to no block, yielding an empty history
 			uint64_t start_height;
 			if (reverse)
 			{
-				start_height = block->sideband ().height + offset;
+				start_height = nano::add_sat (block->sideband ().height, offset);
 			}
 			else
 			{
-				if (block->sideband ().height > offset)
-				{
-					start_height = block->sideband ().height - offset;
-				}
-				else
-				{
-					start_height = 0;
-				}
+				start_height = nano::sub_sat (block->sideband ().height, offset);
 			}
 			if (auto start_hash = node.ledger.find_block_hash_by_height (transaction, account, start_height))
 			{
```

### nano/rpc_test/rpc.cpp
```diff
@@ -1150,6 +1150,26 @@ TEST (rpc, account_history)
 		ASSERT_EQ ("1", history_node.begin ()->second.get<std::string> ("height"));
 		ASSERT_EQ (change->hash ().to_string (), response.get<std::string> ("next"));
 	}
+	// Overflowing offsets saturate and yield an empty history instead of wrapping to a valid height
+	{
+		boost::property_tree::ptree request;
+		request.put ("action", "account_history");
+		request.put ("account", nano::dev::genesis_key.pub.to_account ());
+		request.put ("reverse", true);
+		request.put ("count", 100);
+		request.put ("offset", "18446744073709551615");
+		auto response (wait_response (system, rpc_ctx, request, 10s));
+		ASSERT_EQ (0, response.get_child ("history").size ());
+	}
+	{
+		boost::property_tree::ptree request;
+		request.put ("action", "account_history");
+		request.put ("account", nano::dev::genesis_key.pub.to_account ());
+		request.put ("count", 100);
+		request.put ("offset", "18446744073709551615");
+		auto response (wait_response (system, rpc_ctx, request, 10s));
+		ASSERT_EQ (0, response.get_child ("history").size ());
+	}
 	// Test include_linked_account
 	{
 		boost::property_tree::ptree request;
```
