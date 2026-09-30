# [?] Fixed race condition in fork_publish test (#5086)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2026-06-16
Source: https://github.com/nanocurrency/nano-node/commit/9a392a5b1bbca6423db66a1892c7f493a94c2432
Type: security-commit

## Details
Fixed race condition in fork_publish test (#5086)

* Fixed race condition in fork_publish test

* Assert both forks inserted in fork_publish test

## Patch
### nano/core_test/node.cpp
```diff
@@ -525,14 +525,14 @@ TEST (node, coherent_observer)
 	system.wallet (0)->send_action (nano::dev::genesis_key.pub, key.pub, 1);
 }
 
-// FIXME: This test is racy, there is no guarantee that the election won't be confirmed until all forks are fully processed
 /**
  * Test that two forking blocks processed in quick succession result in a
  * single election containing both blocks.
  *
  * Setup:
- * - Single node with genesis key in wallet (has voting weight)
- * - send1 and send2 (forks) are both processed via process_active
+ * - Single node, send1 and send2 (forks) are both processed via process_active
+ * - The genesis key is inserted into the wallet (giving voting weight) only
+ *   after both forks have joined the election
  *
  * Both blocks enter the same election. Genesis votes for send1 (the block
  * it saw first) and send1 wins the election.
@@ -541,7 +541,6 @@ TEST (node, fork_publish)
 {
 	nano::test::system system (1);
 	auto & node1 (*system.nodes[0]);
-	system.wallet (0)->insert_adhoc (nano::dev::genesis_key.prv);
 	nano::keypair key1;
 	nano::send_block_builder builder;
 	auto send1 = builder.make_block ()
@@ -563,9 +562,14 @@ TEST (node, fork_publish)
 	node1.work_generate_blocking (*send2);
 	node1.process_active (send1);
 	node1.process_active (send2);
-	ASSERT_TIMELY (5s, node1.active.active (*send1) && node1.active.active (*send2));
+	// Wait for the election to start before fetching it
+	ASSERT_TIMELY (5s, node1.active.active (*send1));
 	auto election (node1.active.election (send1->qualified_root ()));
 	ASSERT_NE (nullptr, election);
+	// Ensure both forks have actually joined the same election before the genesis rep starts voting
+	ASSERT_TIMELY_EQ (5s, election->blocks ().size (), 2);
+	// Insert the genesis key so voting only begins once both forks are in the election
+	system.wallet (0)->insert_adhoc (nano::dev::genesis_key.prv);
 	// Wait until the genesis rep activated & makes vote
 	ASSERT_TIMELY_EQ (1s, election->votes ().size (), 2);
 	auto votes1 (election->votes ());
```
