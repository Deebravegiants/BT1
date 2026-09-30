# [?] Fix republish RPC crash on non-send blocks when using the 'destinations' parameter and extend tests (#4972)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2025-12-15
Source: https://github.com/nanocurrency/nano-node/commit/05de81c0331a81b2fdf79541c331ce2fda15aa11
Type: security-commit

## Details
Fix republish RPC crash on non-send blocks when using the 'destinations' parameter and extend tests (#4972)

The republish RPC previously called block_b->destination() unconditionally, which triggers a release_assert(false) when invoked on non-send blocks

## Patch
### nano/node/json_handler.cpp
```diff
@@ -3701,7 +3701,7 @@ void nano::json_handler::republish ()
 				if (destinations != 0) // Republish destination chain
 				{
 					auto block_b = node.ledger.any.block_get (transaction, hash);
-					auto destination = block_b->destination ();
+					auto destination = block_b->is_send () ? block_b->destination () : nano::account (0);
 					if (!destination.is_zero ())
 					{
 						if (!node.ledger.any.pending_get (transaction, nano::pending_key{ destination, hash }))
```

### nano/rpc_test/rpc.cpp
```diff
@@ -2805,6 +2805,32 @@ TEST (rpc, republish)
 	ASSERT_EQ (nano::dev::genesis->hash (), blocks[0]);
 	ASSERT_EQ (send->hash (), blocks[1]);
 	ASSERT_EQ (open->hash (), blocks[2]);
+
+	request.put ("hash", open->hash ().to_string ());
+	request.put ("sources", 0);
+	request.put ("destinations", 2);
+	auto response3 (wait_response (system, rpc_ctx, request));
+	blocks_node = response3.get_child ("blocks");
+	blocks.clear ();
+	for (auto i (blocks_node.begin ()), n (blocks_node.end ()); i != n; ++i)
+	{
+		blocks.push_back (nano::block_hash (i->second.get<std::string> ("")));
+	}
+	ASSERT_EQ (1, blocks.size ());
+
+	request.put ("hash", send->hash ().to_string ());
+	request.put ("sources", 0);
+	request.put ("destinations", 2);
+	auto response4 (wait_response (system, rpc_ctx, request));
+	blocks_node = response4.get_child ("blocks");
+	blocks.clear ();
+	for (auto i (blocks_node.begin ()), n (blocks_node.end ()); i != n; ++i)
+	{
+		blocks.push_back (nano::block_hash (i->second.get<std::string> ("")));
+	}
+	ASSERT_EQ (2, blocks.size ());
+	ASSERT_EQ (send->hash (), blocks[0]);
+	ASSERT_EQ (open->hash (), blocks[1]);
 }
 
 TEST (rpc, deterministic_key)
```
