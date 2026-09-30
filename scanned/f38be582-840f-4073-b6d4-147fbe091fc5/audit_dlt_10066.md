# [?] Fix intermittent race condition in `fork_no_vote_quorum` test (#5000)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2026-01-23
Source: https://github.com/nanocurrency/nano-node/commit/74fb09d401465ec23dad343188f4283b91b138ae
Type: security-commit

## Details
Fix intermittent race condition in `fork_no_vote_quorum` test (#5000)

## Patch
### nano/core_test/node.cpp
```diff
@@ -492,7 +492,30 @@ TEST (node, expire)
 	ASSERT_TRUE (node0.expired ());
 }
 
-// This test is racy, there is no guarantee that the election won't be confirmed until all forks are fully processed
+TEST (node, coherent_observer)
+{
+	nano::test::system system (1);
+	auto & node1 (*system.nodes[0]);
+	node1.observers.blocks.add ([&node1] (nano::election_status const & status_a, std::vector<nano::vote_with_weight_info> const &, nano::account const &, nano::uint128_t const &, bool, bool) {
+		ASSERT_TRUE (node1.ledger.any.block_exists (node1.ledger.tx_begin_read (), status_a.winner->hash ()));
+	});
+	system.wallet (0)->insert_adhoc (nano::dev::genesis_key.prv);
+	nano::keypair key;
+	system.wallet (0)->send_action (nano::dev::genesis_key.pub, key.pub, 1);
+}
+
+// FIXME: This test is racy, there is no guarantee that the election won't be confirmed until all forks are fully processed
+/**
+ * Test that two forking blocks processed in quick succession result in a
+ * single election containing both blocks.
+ *
+ * Setup:
+ * - Single node with genesis key in wallet (has voting weight)
+ * - send1 and send2 (forks) are both processed via process_active
+ *
+ * Both blocks enter the same election. Genesis votes for send1 (the block
+ * it saw first) and send1 wins the election.
+ */
 TEST (node, fork_publish)
 {
 	nano::test::system system (1);
@@ -542,6 +565,19 @@ TEST (node, fork_publish)
 // there is a race somewhere and the election might not notice the send2 block.
 // The test case can be made to pass by ensuring the election is started before the send2 is processed.
 // However, is this a problem with the test case or this is a problem with the node handling of forks?
+// FIXME: Investigate, should work without the workaround
+/**
+ * Test that a fork block joins an existing election rather than being rejected.
+ *
+ * Setup:
+ * - Single node without voting weight configured
+ * - send1 is processed, creating an active election
+ * - send2 (a fork of send1) is then processed via process_local
+ *
+ * The fork is detected (process_local returns fork status) and send2 is added
+ * to the existing election. Both blocks are present in the election, with
+ * send1 as the current winner since it was processed first.
+ */
 TEST (node, fork_publish_inactive)
 {
 	nano::test::system system (1);
@@ -588,6 +624,17 @@ TEST (node, fork_publish_inactive)
 	ASSERT_NE (election->winner ()->hash (), send2->hash ());
 }
 
+/**
+ * Test that nodes keep their original block when a fork arrives later.
+ *
+ * Setup:
+ * - Both nodes receive and process send1 first, starting elections
+ * - Both nodes then receive send2 (a fork of send1)
+ * - Genesis key is inserted into node1, giving it voting weight
+ *
+ * Node1 votes for send1 (the block in its ledger), confirming it across the
+ * network. Since both nodes already have send1, no block replacement occurs.
+ */
 TEST (node, fork_keep)
 {
 	nano::test::system system (2);
@@ -639,7 +686,18 @@ TEST (node, fork_keep)
 	ASSERT_TRUE (node2.ledger.any.block_exists (transaction1, send1->hash ()));
 }
 
-// This test is racy, there is no guarantee that the election won't be confirmed until all forks are fully processed
+// FIXME: This test is racy, there is no guarantee that the election won't be confirmed until all forks are fully processed
+/**
+ * Test basic fork resolution between two nodes that each start with a different fork.
+ *
+ * Setup:
+ * - Node1 receives send1 first, node2 receives send2 first (both are forks)
+ * - Both nodes start elections for their respective blocks
+ * - Nodes then exchange forks so both elections contain both blocks
+ * - Node1 votes with genesis key
+ *
+ * Send1 wins the election and node2 replaces send2 with send1 in its ledger.
+ */
 TEST (node, fork_flip)
 {
 	nano::test::system system (2);
@@ -689,7 +747,17 @@ TEST (node, fork_flip)
 	ASSERT_FALSE (node2.block_or_pruned_exists (publish2.block->hash ()));
 }
 
-// Test that more than one block can be rolled back
+/**
+ * Test that fork resolution correctly rolls back multiple dependent blocks.
+ *
+ * Setup:
+ * - Node1 has send1 in its ledger
+ * - Node2 has send2 (a fork of send1) plus send3 (built on top of send2)
+ * - Node1 votes with genesis key and confirms send1
+ *
+ * When the fork is resolved, node2 must roll back both send2 and its
+ * dependent block send3, then accept send1 as the confirmed winner.
+ */
 TEST (node, fork_multi_flip)
 {
 	auto type = nano::transport::transport_type::tcp;
@@ -743,8 +811,19 @@ TEST (node, fork_multi_flip)
 	ASSERT_EQ (nano::dev::constants.genesis_amount - 100, winner.first);
 }
 
-// Blocks that are no longer actively being voted on should be able to be evicted through bootstrapping.
-// This could happen if a fork wasn't resolved before the process previously shut down
+/**
+ * Test that bootstrap can resolve forks by replacing an unconfirmed block
+ * with a confirmed one from a peer. This simulates a scenario where a fork
+ * wasn't resolved before the node previously shut down - blocks that are no
+ * longer actively being voted on should still be evictable through bootstrapping.
+ *
+ * Setup:
+ * - Node1 (with genesis voting weight) has send1 confirmed in its ledger
+ * - Node2 (disconnected) has send2 (a fork of send1) unconfirmed in its ledger
+ *
+ * When the nodes connect, node2 bootstraps from node1 and discovers the
+ * confirmed send1. Node2 replaces send2 with send1, resolving the fork.
+ */
 TEST (node, fork_bootstrap_flip)
 {
 	nano::test::system system;
@@ -786,9 +865,22 @@ TEST (node, fork_bootstrap_flip)
 	// Additionally add new peer to confirm & replace bootstrap block
 	node2.network.merge_peer (node1.network.endpoint ());
 
+	// Node2 should bootstrap from node1 and replace send2 with send1
 	ASSERT_TIMELY (10s, node2.ledger.any.block_exists (node2.ledger.tx_begin_read (), send1->hash ()));
 }
 
+/**
+ * Test fork handling for open blocks when there is no voting weight to reach quorum.
+ *
+ * Setup:
+ * - All genesis balance is sent to key1, leaving no voting weight in the network
+ * - open1 is created and processed first
+ * - open2 (a fork of open1) is created and processed second
+ *
+ * Both blocks enter the same election. With no voting weight available, the
+ * election cannot reach quorum and remains unconfirmed. The first block seen
+ * (open1) is kept in the ledger while open2 is not.
+ */
 TEST (node, fork_open)
 {
 	nano::test::system system (1);
@@ -854,6 +946,18 @@ TEST (node, fork_open)
 	ASSERT_FALSE (node.block (publish3.block->hash ()));
 }
 
+/**
+ * Test that a node can "flip" from one fork to another when consensus resolves
+ * to a different block than what it originally had in its ledger.
+ *
+ * Setup:
+ * - Node1 has open1 in its ledger and starts an election
+ * - Node2 is pre-initialized with open2 (a fork of open1) and starts an election
+ * - Node1 votes with the genesis key (full voting weight) and confirms open1
+ *
+ * After open1 is confirmed on node1, node2 learns about open1 and must replace
+ * open2 with the consensus winner in its ledger.
+ */
 TEST (node, fork_open_flip)
 {
 	nano::test::system system (1);
@@ -942,18 +1046,19 @@ TEST (node, fork_open_flip)
 	ASSERT_FALSE (node2.ledger.any.block_exists (transaction2, open2->hash ()));
 }
 
-TEST (node, coherent_observer)
-{
-	nano::test::system system (1);
-	auto & node1 (*system.nodes[0]);
-	node1.observers.blocks.add ([&node1] (nano::election_status const & status_a, std::vector<nano::vote_with_weight_info> const &, nano::account const &, nano::uint128_t const &, bool, bool) {
-		ASSERT_TRUE (node1.ledger.any.block_exists (node1.ledger.tx_begin_read (), status_a.winner->hash ()));
-	});
-	system.wallet (0)->insert_adhoc (nano::dev::genesis_key.prv);
-	nano::keypair key;
-	system.wallet (0)->send_action (nano::dev::genesis_key.pub, key.pub, 1);
-}
-
+/**
+ * Test that a fork cannot displace an existing block when voted for by a representative
+ * without sufficient weight to reach quorum.
+ *
+ * Setup:
+ * - 3 connected nodes with key1 as a representative holding minimal voting weight
+ * - send1: a valid block processed by all nodes
+ * - send2: a forking block (same previous as send1) sent to a different destination
+ *
+ * The test sends a vote for the forking block (send2) from key1, which lacks
+ * enough weight to reach quorum. It verifies that all nodes retain send1 as
+ * the latest block in the ledger, demonstrating that votes without quorum cannot override consensus.
+ */
 TEST (node, fork_no_vote_quorum)
 {
 	nano::test::system system (3);
@@ -985,9 +1090,9 @@ TEST (node, fork_no_vote_quorum)
 				 .sign (nano::dev::genesis_key.prv, nano::dev::genesis_key.pub)
 				 .work (*system.work.generate (block->hash ()))
 				 .build ();
-	ASSERT_EQ (nano::block_status::progress, node1.process (send1));
-	ASSERT_EQ (nano::block_status::progress, node2.process (send1));
-	ASSERT_EQ (nano::block_status::progress, node3.process (send1));
+	nano::test::process (node1, { send1 });
+	nano::test::process (node2, { send1 });
+	nano::test::process (node3, { send1 });
 	auto key2 (system.wallet (2)->deterministic_insert ());
 	auto send2 = nano::send_block_builder ()
 				 .previous (block->hash ())
@@ -1010,7 +1115,22 @@ TEST (node, fork_no_vote_quorum)
 	ASSERT_EQ (node3.latest (nano::dev::genesis_key.pub), send1->hash ());
 }
 
-// Disabled because it sometimes takes way too long (but still eventually finishes)
+// FIXME: Disabled because it sometimes takes way too long (but still eventually finishes)
+/**
+ * Test fork resolution when voting weight is distributed across multiple representatives
+ * and the fork exists before any block is confirmed.
+ *
+ * Setup:
+ * - 3 nodes, each with a representative key
+ * - Genesis sends 1/3 of balance to key1 (node1's rep) and 1/3 to key2 (node2's rep)
+ * - Voting weight is now split: genesis ~1/3, key1 ~1/3, key2 ~1/3
+ * - block2 and block3 are forking rep-change blocks on the genesis account
+ * - node0 and node1 receive block2, node2 receives block3
+ *
+ * Each node votes for the block it has. With 2/3 voting for block2 (genesis + key1)
+ * and 1/3 for block3 (key2), block2 should win. The test verifies that all nodes
+ * eventually reach consensus on the same block.
+ */
 TEST (node, DISABLED_fork_pre_confirm)
 {
 	nano::test::system system (3);
@@ -1073,7 +1193,24 @@ TEST (node, DISABLED_fork_pre_confirm)
 	}
 }
 
-// Sometimes hangs on the bootstrap_initiator.bootstrap call
+// FIXME: Disabled because it is hanging intermittently
+/**
+ * Test fork resolution between nodes that independently processed different
+ * blocks before discovering each other.
+ *
+ * Setup:
+ * - Two separate test systems with one node each (isolated networks)
+ * - Node1 has genesis key (voting weight), node2 does not
+ * - A TCP channel is established and node2 learns node1 is a representative
+ * - send3 is processed on both nodes (shared base block)
+ * - send1 is written directly to node1's ledger
+ * - send2 (fork of send1) is written directly to node2's ledger
+ * - Both forks are then activated on both nodes via process_active
+ *
+ * The direct ledger writes simulate "stale" blocks that existed before the
+ * nodes connected. When both forks are activated, node1's vote for send1
+ * should cause node2 to accept send1.
+ */
 TEST (node, DISABLED_fork_stale)
 {
 	nano::test::system system1 (1);
```
