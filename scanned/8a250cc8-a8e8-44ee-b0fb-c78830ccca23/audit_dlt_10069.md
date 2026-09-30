# [?] Check bootstrap status earlier to avoid race condition (#4973)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2025-12-15
Source: https://github.com/nanocurrency/nano-node/commit/63206358955835103ed9ec66a4b951af572d1136
Type: security-commit

## Details
Check bootstrap status earlier to avoid race condition (#4973)

## Patch
### nano/rpc_test/rpc.cpp
```diff
@@ -7107,11 +7107,11 @@ TEST (rpc, bootstrap_status)
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
@@ -7120,15 +7120,15 @@ TEST (rpc, bootstrap_status)
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
 	request.put ("action", "bootstrap_status");
```
