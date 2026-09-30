# [?] Fix race condition identified by TSAN when computing hash

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2023-11-06
Source: https://github.com/nanocurrency/nano-node/commit/906cbbf54169ecc2265f7722c106510fa62f2604
Type: security-commit

## Details
Fix race condition identified by TSAN when computing hash

## Patch
### nano/core_test/node.cpp
```diff
@@ -2143,6 +2143,8 @@ TEST (node, block_confirm)
 	auto send1_copy = builder.make_block ()
 					  .from (*send1)
 					  .build_shared ();
+	auto hash1 = send1->hash ();
+	auto hash2 = send1_copy->hash ();
 	node1.block_processor.add (send1);
 	node2.block_processor.add (send1_copy);
 	ASSERT_TIMELY (5s, node1.ledger.block_or_pruned_exists (send1->hash ()) && node2.ledger.block_or_pruned_exists (send1_copy->hash ()));
```
