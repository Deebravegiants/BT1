# [?] This fixes a race condition in node.node_receive_quorum. Election creation is done after transaction commit so there isn't a guarantee the election wi

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2020-09-24
Source: https://github.com/nanocurrency/nano-node/commit/abf90145689a7fa1d931d68f8bd7befb8191d832
Type: security-commit

## Details
This fixes a race condition in node.node_receive_quorum. Election creation is done after transaction commit so there isn't a guarantee the election will be created as the block is observable in the ledger. (#2971)

## Patch
### nano/core_test/node.cpp
```diff
@@ -256,6 +256,7 @@ TEST (node, node_receive_quorum)
 	            .build_shared ();
 	node1.process_active (send);
 	ASSERT_TIMELY (10s, node1.ledger.block_exists (send->hash ()));
+	ASSERT_TIMELY (10s, node1.active.election (nano::qualified_root (previous, previous)) != nullptr);
 	auto election (node1.active.election (nano::qualified_root (previous, previous)));
 	ASSERT_NE (nullptr, election);
 	ASSERT_FALSE (election->confirmed ());
```
