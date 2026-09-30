# [?] Fix race condition in fork_publish unit test (#5074)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2026-05-20
Source: https://github.com/nanocurrency/nano-node/commit/19198626b8e05e9a7ba1d92bea537385485a60e7
Type: security-commit

## Details
Fix race condition in fork_publish unit test (#5074)

## Patch
### nano/core_test/node.cpp
```diff
@@ -563,8 +563,7 @@ TEST (node, fork_publish)
 	node1.work_generate_blocking (*send2);
 	node1.process_active (send1);
 	node1.process_active (send2);
-	ASSERT_TIMELY_EQ (5s, 1, node1.active.size ());
-	ASSERT_TIMELY (5s, node1.active.active (*send2));
+	ASSERT_TIMELY (5s, node1.active.active (*send1) && node1.active.active (*send2));
 	auto election (node1.active.election (send1->qualified_root ()));
 	ASSERT_NE (nullptr, election);
 	// Wait until the genesis rep activated & makes vote
```
