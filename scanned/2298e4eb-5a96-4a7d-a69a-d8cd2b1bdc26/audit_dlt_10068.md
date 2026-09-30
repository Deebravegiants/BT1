# [?] Fix race condition in two bootstrap tests (#4978)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2026-01-01
Source: https://github.com/nanocurrency/nano-node/commit/14bdb05f8f7e3633e1207a5d6b9b6f3402a1ed27
Type: security-commit

## Details
Fix race condition in two bootstrap tests (#4978)

## Patch
### nano/rpc_test/rpc.cpp
```diff
@@ -7050,8 +7050,8 @@ TEST (rpc, bootstrap_priorities)
 	nano::test::system system;
 
 	// Test configuration
-	int const chain_count = 5;
-	int const blocks_per_chain = 2;
+	int const chain_count = 10;
+	int const blocks_per_chain = 4;
 
 	nano::node_config config;
 	config.bootstrap.rate_limit = 10; // Add request limits to slow down bootstrap
@@ -7063,15 +7063,15 @@ TEST (rpc, bootstrap_priorities)
 	auto chains = nano::test::setup_chains (system, node_server, chain_count, blocks_per_chain);
 
 	int const total_blocks = node_server.block_count ();
-	int const halfway_blocks = total_blocks / 2;
+	int const target_blocks = total_blocks / 4; // Stop at 25%
 
 	// Start client node to observe bootstrap
 	auto node = add_ipc_enabled_node (system);
 	auto const rpc_ctx = add_rpc (system, node);
 
 	// Wait until bootstrap has started and processed some blocks but not all
-	// Target approximately halfway through
-	ASSERT_TIMELY (15s, node->block_count () >= halfway_blocks);
+	// Target approximately 25% through
+	ASSERT_TIMELY (15s, node->block_count () >= target_blocks);
 
 	boost::property_tree::ptree request;
 	request.put ("action", "bootstrap_priorities");
@@ -7087,11 +7087,11 @@ TEST (rpc, bootstrap_reset)
 	nano::test::system system;
 
 	// Test configuration
-	int const chain_count = 5;
-	int const blocks_per_chain = 2;
+	int const chain_count = 10;
+	int const blocks_per_chain = 4;
 
 	nano::node_config config;
-	config.bootstrap.rate_limit = 10; // Add request limits to slow down bootstrap
+	config.bootstrap.rate_limit = 5; // Add request limits to slow down bootstrap
 
 	// Start server node
 	auto & node_server = *system.add_node (config);
@@ -7100,15 +7100,15 @@ TEST (rpc, bootstrap_reset)
 	auto chains = nano::test::setup_chains (system, node_server, chain_count, blocks_per_chain);
 
 	int const total_blocks = node_server.block_count ();
-	int const halfway_blocks = total_blocks / 2;
+	int const target_blocks = total_blocks / 4; // Stop at 25%
 
 	// Start client node to observe bootstrap
 	auto node = add_ipc_enabled_node (system);
 	auto const rpc_ctx = add_rpc (system, node);
 
 	// Wait until bootstrap has started and processed some blocks but not all
-	// Target approximately halfway through
-	ASSERT_TIMELY (15s, node->block_count () >= halfway_blocks);
+	// Target approximately 25% through
+	ASSERT_TIMELY (15s, node->block_count () >= target_blocks);
 
 	boost::property_tree::ptree request;
 	request.put ("action", "bootstrap_reset");
```
