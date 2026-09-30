# [?] Fixed a race condition where fast wallet operations would cause some of them to not take effect.  This was being covered up in testing due to flushing

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2017-12-06
Source: https://github.com/nanocurrency/nano-node/commit/a39c05709e0f550a71a6d25d6726cdbe2406e3e8
Type: security-commit

## Details
Fixed a race condition where fast wallet operations would cause some of them to not take effect.  This was being covered up in testing due to flushing blocks when passed to block_processor.

## Patch
### rai/core_test/network.cpp
```diff
@@ -309,7 +309,9 @@ TEST (receivable_processor, send_with_receive)
 	ASSERT_EQ (amount, system.nodes [1]->balance (rai::test_genesis_key.pub));
 	ASSERT_EQ (0, system.nodes [1]->balance (key2.pub));
     system.nodes [0]->process_active (block1);
+    system.nodes [0]->block_processor.flush ();
     system.nodes [1]->process_active (block1);
+    system.nodes [1]->block_processor.flush ();
 	ASSERT_EQ (amount - system.nodes [0]->config.receive_minimum.number (), system.nodes [0]->balance (rai::test_genesis_key.pub));
 	ASSERT_EQ (0, system.nodes [0]->balance (key2.pub));
 	ASSERT_EQ (amount - system.nodes [0]->config.receive_minimum.number (), system.nodes [1]->balance (rai::test_genesis_key.pub));
```

### rai/core_test/node.cpp
```diff
@@ -264,6 +264,7 @@ TEST (node, receive_gap)
     rai::confirm_req message;
     message.block = block;
     node1.process_message (message, node1.network.endpoint ());
+    node1.block_processor.flush ();
     ASSERT_EQ (1, node1.gap_cache.blocks.size ());
 }
 
@@ -698,110 +699,120 @@ TEST (node, block_replace)
 
 TEST (node, fork_publish)
 {
-    std::weak_ptr <rai::node> node0;
-    {
-        rai::system system (24000, 1);
-        node0 = system.nodes [0];
-        auto & node1 (*system.nodes [0]);
+	std::weak_ptr <rai::node> node0;
+	{
+		rai::system system (24000, 1);
+		node0 = system.nodes [0];
+		auto & node1 (*system.nodes [0]);
 		system.wallet (0)->insert_adhoc (rai::test_genesis_key.prv);
-        rai::keypair key1;
+		rai::keypair key1;
 		rai::genesis genesis;
-        auto send1 (std::make_shared <rai::send_block> (genesis.hash (), key1.pub, rai::genesis_amount - 100, rai::test_genesis_key.prv, rai::test_genesis_key.pub, 0));
-        rai::keypair key2;
-        auto send2 (std::make_shared <rai::send_block> (genesis.hash (), key2.pub, rai::genesis_amount - 100, rai::test_genesis_key.prv, rai::test_genesis_key.pub, 0));
-        node1.process_active (send1);
-        ASSERT_EQ (1, node1.active.roots.size ());
+		auto send1 (std::make_shared <rai::send_block> (genesis.hash (), key1.pub, rai::genesis_amount - 100, rai::test_genesis_key.prv, rai::test_genesis_key.pub, 0));
+		rai::keypair key2;
+		auto send2 (std::make_shared <rai::send_block> (genesis.hash (), key2.pub, rai::genesis_amount - 100, rai::test_genesis_key.prv, rai::test_genesis_key.pub, 0));
+		node1.process_active (send1);
+		node1.block_processor.flush ();
+		ASSERT_EQ (1, node1.active.roots.size ());
 		auto existing (node1.active.roots.find (send1->root ()));
 		ASSERT_NE (node1.active.roots.end (), existing);
 		auto election (existing->election);
 		ASSERT_EQ (2, election->votes.rep_votes.size ());
-        node1.process_active (send2);
-        auto existing1 (election->votes.rep_votes.find (rai::test_genesis_key.pub));
-        ASSERT_NE (election->votes.rep_votes.end (), existing1);
-        ASSERT_EQ (*send1, *existing1->second);
+		node1.process_active (send2);
+		node1.block_processor.flush ();
+		auto existing1 (election->votes.rep_votes.find (rai::test_genesis_key.pub));
+		ASSERT_NE (election->votes.rep_votes.end (), existing1);
+		ASSERT_EQ (*send1, *existing1->second);
 		rai::transaction transaction (node1.store.environment, nullptr, false);
-        auto winner (node1.ledger.winner (transaction, election->votes));
-        ASSERT_EQ (*send1, *winner.second);
-        ASSERT_EQ (rai::genesis_amount - 100, winner.first);
-    }
-    ASSERT_TRUE (node0.expired ());
+		auto winner (node1.ledger.winner (transaction, election->votes));
+		ASSERT_EQ (*send1, *winner.second);
+		ASSERT_EQ (rai::genesis_amount - 100, winner.first);
+	}
+	ASSERT_TRUE (node0.expired ());
 }
 
 TEST (node, fork_keep)
 {
-    rai::system system (24000, 2);
-    auto & node1 (*system.nodes [0]);
-    auto & node2 (*system.nodes [1]);
+	rai::system system (24000, 2);
+	auto & node1 (*system.nodes [0]);
+	auto & node2 (*system.nodes [1]);
 	ASSERT_EQ (1, node1.peers.size ());
 	system.wallet (0)->insert_adhoc (rai::test_genesis_key.prv);
-    rai::keypair key1;
-    rai::keypair key2;
+	rai::keypair key1;
+	rai::keypair key2;
 	rai::genesis genesis;
 	// send1 and send2 fork to different accounts
-    auto send1 (std::make_shared <rai::send_block> (genesis.hash (), key1.pub, rai::genesis_amount - 100, rai::test_genesis_key.prv, rai::test_genesis_key.pub, system.work.generate (genesis.hash ())));
-    auto send2 (std::make_shared <rai::send_block> (genesis.hash (), key2.pub, rai::genesis_amount - 100, rai::test_genesis_key.prv, rai::test_genesis_key.pub, system.work.generate (genesis.hash ())));
-    node1.process_active (send1);
+	auto send1 (std::make_shared <rai::send_block> (genesis.hash (), key1.pub, rai::genesis_amount - 100, rai::test_genesis_key.prv, rai::test_genesis_key.pub, system.work.generate (genesis.hash ())));
+	auto send2 (std::make_shared <rai::send_block> (genesis.hash (), key2.pub, rai::genesis_amount - 100, rai::test_genesis_key.prv, rai::test_genesis_key.pub, system.work.generate (genesis.hash ())));
+	node1.process_active (send1);
+	node1.block_processor.flush ();
 	node2.process_active (send1);
-    ASSERT_EQ (1, node1.active.roots.size ());
-    ASSERT_EQ (1, node2.active.roots.size ());
-    node1.process_active (send2);
+	node2.block_processor.flush ();
+	ASSERT_EQ (1, node1.active.roots.size ());
+	ASSERT_EQ (1, node2.active.roots.size ());
+	node1.process_active (send2);
+	node1.block_processor.flush ();
 	node2.process_active (send2);
-    auto conflict (node2.active.roots.find (genesis.hash ()));
-    ASSERT_NE (node2.active.roots.end (), conflict);
-    auto votes1 (conflict->election);
-    ASSERT_NE (nullptr, votes1);
-    ASSERT_EQ (1, votes1->votes.rep_votes.size ());
+	node2.block_processor.flush ();
+	auto conflict (node2.active.roots.find (genesis.hash ()));
+	ASSERT_NE (node2.active.roots.end (), conflict);
+	auto votes1 (conflict->election);
+	ASSERT_NE (nullptr, votes1);
+	ASSERT_EQ (1, votes1->votes.rep_votes.size ());
 	{
 		rai::transaction transaction0 (system.nodes [0]->store.environment, nullptr, false);
 		rai::transaction transaction1 (system.nodes [1]->store.environment, nullptr, false);
 		ASSERT_TRUE (system.nodes [0]->store.block_exists (transaction0, send1->hash ()));
 		ASSERT_TRUE (system.nodes [1]->store.block_exists (transaction1, send1->hash ()));
 	}
-    auto iterations (0);
+	auto iterations (0);
 	// Wait until the genesis rep makes a vote
-    while (votes1->votes.rep_votes.size () == 1)
+	while (votes1->votes.rep_votes.size () == 1)
 	{
 		system.poll ();
-        ++iterations;
-        ASSERT_LT (iterations, 2000);
+		++iterations;
+		ASSERT_LT (iterations, 2000);
 	}
 	rai::transaction transaction0 (system.nodes [0]->store.environment, nullptr, false);
 	rai::transaction transaction1 (system.nodes [1]->store.environment, nullptr, false);
 	// The vote should be in agreement with what we already have.
-    auto winner (node1.ledger.winner (transaction0, votes1->votes));
-    ASSERT_EQ (*send1, *winner.second);
-    ASSERT_EQ (rai::genesis_amount - 100, winner.first);
+	auto winner (node1.ledger.winner (transaction0, votes1->votes));
+	ASSERT_EQ (*send1, *winner.second);
+	ASSERT_EQ (rai::genesis_amount - 100, winner.first);
 	ASSERT_TRUE (system.nodes [0]->store.block_exists (transaction0, send1->hash ()));
 	ASSERT_TRUE (system.nodes [1]->store.block_exists (transaction1, send1->hash ()));
 }
 
 TEST (node, fork_flip)
 {
-    rai::system system (24000, 2);
-    auto & node1 (*system.nodes [0]);
-    auto & node2 (*system.nodes [1]);
-    ASSERT_EQ (1, node1.peers.size ());
+	rai::system system (24000, 2);
+	auto & node1 (*system.nodes [0]);
+	auto & node2 (*system.nodes [1]);
+	ASSERT_EQ (1, node1.peers.size ());
 	system.wallet (0)->insert_adhoc (rai::test_genesis_key.prv);
-    rai::keypair key1;
+	rai::keypair key1;
 	rai::genesis genesis;
-    std::unique_ptr <rai::send_block> send1 (new rai::send_block (genesis.hash (), key1.pub, rai::genesis_amount - 100, rai::test_genesis_key.prv, rai::test_genesis_key.pub, system.work.generate (genesis.hash ())));
-    rai::publish publish1;
-    publish1.block = std::move (send1);
-    rai::keypair key2;
-    std::unique_ptr <rai::send_block> send2 (new rai::send_block (genesis.hash (), key2.pub, rai::genesis_amount - 100, rai::test_genesis_key.prv, rai::test_genesis_key.pub, system.work.generate (genesis.hash ())));
-    rai::publish publish2;
-    publish2.block = std::move (send2);
-    node1.process_message (publish1, node1.network.endpoint ());
-    node2.process_message (publish2, node1.network.endpoint ());
-    ASSERT_EQ (1, node1.active.roots.size ());
-    ASSERT_EQ (1, node2.active.roots.size ());
-    node1.process_message (publish2, node1.network.endpoint ());
-    node2.process_message (publish1, node2.network.endpoint ());
-    auto conflict (node2.active.roots.find (genesis.hash ()));
-    ASSERT_NE (node2.active.roots.end (), conflict);
-    auto votes1 (conflict->election);
-    ASSERT_NE (nullptr, votes1);
-    ASSERT_EQ (1, votes1->votes.rep_votes.size ());
+	std::unique_ptr <rai::send_block> send1 (new rai::send_block (genesis.hash (), key1.pub, rai::genesis_amount - 100, rai::test_genesis_key.prv, rai::test_genesis_key.pub, system.work.generate (genesis.hash ())));
+	rai::publish publish1;
+	publish1.block = std::move (send1);
+	rai::keypair key2;
+	std::unique_ptr <rai::send_block> send2 (new rai::send_block (genesis.hash (), key2.pub, rai::genesis_amount - 100, rai::test_genesis_key.prv, rai::test_genesis_key.pub, system.work.generate (genesis.hash ())));
+	rai::publish publish2;
+	publish2.block = std::move (send2);
+	node1.process_message (publish1, node1.network.endpoint ());
+	node1.block_processor.flush ();
+	node2.process_message (publish2, node1.network.endpoint ());
+	node2.block_processor.flush ();
+	ASSERT_EQ (1, node1.active.roots.size ());
+	ASSERT_EQ (1, node2.active.roots.size ());
+	node1.process_message (publish2, node1.network.endpoint ());
+	node1.block_processor.flush ();
+	node2.process_message (publish1, node2.network.endpoint ());
+	node2.block_processor.flush ();
+	auto conflict (node2.active.roots.find (genesis.hash ()));
+	ASSERT_NE (node2.active.roots.end (), conflict);
+	auto votes1 (conflict->election);
+	ASSERT_NE (nullptr, votes1);
+	ASSERT_EQ (1, votes1->votes.rep_votes.size ());
 	{
 		rai::transaction transaction (system.nodes [0]->store.environment, nullptr, false);
 		ASSERT_TRUE (node1.store.block_exists (transaction, publish1.block->hash ()));
@@ -810,20 +821,20 @@ TEST (node, fork_flip)
 		rai::transaction transaction (system.nodes [1]->store.environment, nullptr, false);
 		ASSERT_TRUE (node2.store.block_exists (transaction, publish2.block->hash ()));
 	}
-    auto iterations (0);
-    while (votes1->votes.rep_votes.size () == 1)
-    {
-        system.poll ();
-        ++iterations;
-        ASSERT_LT (iterations, 200);
-    }
+	auto iterations (0);
+	while (votes1->votes.rep_votes.size () == 1)
+	{
+		system.poll ();
+		++iterations;
+		ASSERT_LT (iterations, 200);
+	}
 	rai::transaction transaction (system.nodes [0]->store.environment, nullptr, false);
-    auto winner (node2.ledger.winner (transaction, votes1->votes));
-    ASSERT_EQ (*publish1.block, *winner.second);
-    ASSERT_EQ (rai::genesis_amount - 100, winner.first);
-    ASSERT_TRUE (node1.store.block_exists (transaction, publish1.block->hash ()));
-    ASSERT_TRUE (node2.store.block_exists (transaction, publish1.block->hash ()));
-    ASSERT_FALSE (node2.store.block_exists (transaction, publish2.block->hash ()));
+	auto winner (node2.ledger.winner (transaction, votes1->votes));
+	ASSERT_EQ (*publish1.block, *winner.second);
+	ASSERT_EQ (rai::genesis_amount - 100, winner.first);
+	ASSERT_TRUE (node1.store.block_exists (transaction, publish1.block->hash ()));
+	ASSERT_TRUE (node2.store.block_exists (transaction, publish1.block->hash ()));
+	ASSERT_FALSE (node2.store.block_exists (transaction, publish2.block->hash ()));
 }
 
 TEST (node, fork_multi_flip)
@@ -846,13 +857,17 @@ TEST (node, fork_multi_flip)
     rai::publish publish3;
     publish3.block = std::move (send3);
     node1.process_message (publish1, node1.network.endpoint ());
+	node1.block_processor.flush ();
 	node2.process_message (publish2, node2.network.endpoint ());
     node2.process_message (publish3, node2.network.endpoint ());
+	node2.block_processor.flush ();
     ASSERT_EQ (1, node1.active.roots.size ());
     ASSERT_EQ (2, node2.active.roots.size ());
     node1.process_message (publish2, node1.network.endpoint ());
     node1.process_message (publish3, node1.network.endpoint ());
+	node1.block_processor.flush ();
 	node2.process_message (publish1, node2.network.endpoint ());
+	node2.block_processor.flush ();
     auto conflict (node2.active.roots.find (genesis.hash ()));
     ASSERT_NE (node2.active.roots.end (), conflict);
     auto votes1 (conflict->election);
@@ -900,7 +915,9 @@ TEST (node, fork_bootstrap_flip)
 	auto send2 (std::make_shared <rai::send_block> (latest, key2.pub, rai::genesis_amount - rai::Gxrb_ratio, rai::test_genesis_key.prv, rai::test_genesis_key.pub, system0.work.generate (latest)));
 	// Insert but don't rebroadcast, simulating settled blocks
 	node1.block_processor.process_receive_many (send1);
+	node1.block_processor.flush ();
 	node2.block_processor.process_receive_many (send2);
+	node2.block_processor.flush ();
 	{
 		rai::transaction transaction (node2.store.environment, nullptr, false);
 		ASSERT_TRUE (node2.store.block_exists (transaction, send2->hash ()));
@@ -930,76 +947,83 @@ TEST (node, fork_bootstrap_flip)
 
 TEST (node, fork_open)
 {
-    rai::system system (24000, 1);
-    auto & node1 (*system.nodes [0]);
+	rai::system system (24000, 1);
+	auto & node1 (*system.nodes [0]);
 	system.wallet (0)->insert_adhoc ( rai::test_genesis_key.prv);
-    rai::keypair key1;
+	rai::keypair key1;
 	rai::genesis genesis;
-    std::unique_ptr <rai::send_block> send1 (new rai::send_block (genesis.hash (), key1.pub, 0, rai::test_genesis_key.prv, rai::test_genesis_key.pub, system.work.generate (genesis.hash ())));
-    rai::publish publish1;
-    publish1.block = std::move (send1);
-    node1.process_message (publish1, node1.network.endpoint ());
-    std::unique_ptr <rai::open_block> open1 (new rai::open_block (publish1.block->hash (), 1, key1.pub, key1.prv, key1.pub, system.work.generate (key1.pub)));
-    rai::publish publish2;
-    publish2.block = std::move (open1);
-    node1.process_message (publish2, node1.network.endpoint ());
-    std::unique_ptr <rai::open_block> open2 (new rai::open_block (publish1.block->hash (), 2, key1.pub, key1.prv, key1.pub, system.work.generate (key1.pub)));
-    rai::publish publish3;
-    publish3.block = std::move (open2);
-    ASSERT_EQ (2, node1.active.roots.size ());
+	std::unique_ptr <rai::send_block> send1 (new rai::send_block (genesis.hash (), key1.pub, 0, rai::test_genesis_key.prv, rai::test_genesis_key.pub, system.work.generate (genesis.hash ())));
+	rai::publish publish1;
+	publish1.block = std::move (send1);
+	node1.process_message (publish1, node1.network.endpoint ());
+	node1.block_processor.flush ();
+	std::unique_ptr <rai::open_block> open1 (new rai::open_block (publish1.block->hash (), 1, key1.pub, key1.prv, key1.pub, system.work.generate (key1.pub)));
+	rai::publish publish2;
+	publish2.block = std::move (open1);
+	node1.process_message (publish2, node1.network.endpoint ());
+	node1.block_processor.flush ();
+	std::unique_ptr <rai::open_block> open2 (new rai::open_block (publish1.block->hash (), 2, key1.pub, key1.prv, key1.pub, system.work.generate (key1.pub)));
+	rai::publish publish3;
+	publish3.block = std::move (open2);
+	ASSERT_EQ (2, node1.active.roots.size ());
 	node1.process_message (publish3, node1.network.endpoint ());
+	node1.block_processor.flush ();
 }
 
 TEST (node, fork_open_flip)
 {
-    rai::system system (24000, 2);
-    auto & node1 (*system.nodes [0]);
-    auto & node2 (*system.nodes [1]);
-    ASSERT_EQ (1, node1.peers.size ());
+	rai::system system (24000, 2);
+	auto & node1 (*system.nodes [0]);
+	auto & node2 (*system.nodes [1]);
+	ASSERT_EQ (1, node1.peers.size ());
 	system.wallet (0)->insert_adhoc (rai::test_genesis_key.prv);
-    rai::keypair key1;
+	rai::keypair key1;
 	rai::genesis genesis;
 	rai::keypair rep1;
 	rai::keypair rep2;
-    auto send1 (std::make_shared <rai::send_block> (genesis.hash (), key1.pub, rai::genesis_amount - 1, rai::test_genesis_key.prv, rai::test_genesis_key.pub, system.work.generate (genesis.hash ())));
-    node1.process_active (send1);
-    node2.process_active (send1);
+	auto send1 (std::make_shared <rai::send_block> (genesis.hash (), key1.pub, rai::genesis_amount - 1, rai::test_genesis_key.prv, rai::test_genesis_key.pub, system.work.generate (genesis.hash ())));
+	node1.process_active (send1);
+	node2.process_active (send1);
 	// We should be keeping this block
-    auto open1 (std::make_shared <rai::open_block> (send1->hash (), rep1.pub, key1.pub, key1.prv, key1.pub, system.work.generate (key1.pub)));
+	auto open1 (std::make_shared <rai::open_block> (send1->hash (), rep1.pub, key1.pub, key1.prv, key1.pub, system.work.generate (key1.pub)));
 	// This block should be evicted
-    auto open2 (std::make_shared <rai::open_block> (send1->hash (), rep2.pub, key1.pub, key1.prv, key1.pub, system.work.generate (key1.pub)));
+	auto open2 (std::make_shared <rai::open_block> (send1->hash (), rep2.pub, key1.pub, key1.prv, key1.pub, system.work.generate (key1.pub)));
 	ASSERT_FALSE (*open1 == *open2);
 	// node1 gets copy that will remain
-    node1.process_active (open1);
+	node1.process_active (open1);
+	node1.block_processor.flush ();
 	// node2 gets copy that will be evicted
-    node2.process_active (open2);
-    ASSERT_EQ (2, node1.active.roots.size ());
-    ASSERT_EQ (2, node2.active.roots.size ());
+	node2.process_active (open2);
+	node2.block_processor.flush ();
+	ASSERT_EQ (2, node1.active.roots.size ());
+	ASSERT_EQ (2, node2.active.roots.size ());
 	// Notify both nodes that a fork exists
-    node1.process_active (open2);
-    node2.process_active (open1);
-    auto conflict (node2.active.roots.find (open1->root ()));
-    ASSERT_NE (node2.active.roots.end (), conflict);
-    auto votes1 (conflict->election);
-    ASSERT_NE (nullptr, votes1);
-    ASSERT_EQ (1, votes1->votes.rep_votes.size ());
+	node1.process_active (open2);
+	node1.block_processor.flush ();
+	node2.process_active (open1);
+	node2.block_processor.flush ();
+	auto conflict (node2.active.roots.find (open1->root ()));
+	ASSERT_NE (node2.active.roots.end (), conflict);
+	auto votes1 (conflict->election);
+	ASSERT_NE (nullptr, votes1);
+	ASSERT_EQ (1, votes1->votes.rep_votes.size ());
 	ASSERT_TRUE (node1.block (open1->hash ()) != nullptr);
 	ASSERT_TRUE (node2.block (open2->hash ()) != nullptr);
-    auto iterations (0);
+	auto iterations (0);
 	// Node2 should eventually settle on open1
-    while (node2.block (open1->hash ()) == nullptr)
-    {
-        system.poll ();
-        ++iterations;
-        ASSERT_LT (iterations, 200);
-    }
+	while (node2.block (open1->hash ()) == nullptr)
+	{
+		system.poll ();
+		++iterations;
+		ASSERT_LT (iterations, 200);
+	}
 	rai::transaction transaction (system.nodes [0]->store.environment, nullptr, false);
-    auto winner (node2.ledger.winner (transaction, votes1->votes));
-    ASSERT_EQ (*open1, *winner.second);
-    ASSERT_EQ (rai::genesis_amount - 1, winner.first);
-    ASSERT_TRUE (node1.store.block_exists (transaction, open1->hash ()));
-    ASSERT_TRUE (node2.store.block_exists (transaction, open1->hash ()));
-    ASSERT_FALSE (node2.store.block_exists (transaction, open2->hash ()));
+	auto winner (node2.ledger.winner (transaction, votes1->votes));
+	ASSERT_EQ (*open1, *winner.second);
+	ASSERT_EQ (rai::genesis_amount - 1, winner.first);
+	ASSERT_TRUE (node1.store.block_exists (transaction, open1->hash ()));
+	ASSERT_TRUE (node2.store.block_exists (transaction, open1->hash ()));
+	ASSERT_FALSE (node2.store.block_exists (transaction, open2->hash ()));
 }
 
 TEST (node, coherent_observer)
```

### rai/core_test/wallet.cpp
```diff
@@ -864,3 +864,22 @@ TEST (wallet, no_work)
     ASSERT_NE (nullptr, block);
     ASSERT_EQ (0, block->block_work ());
 }
+
+TEST (wallet, send_race)
+{
+    rai::system system (24000, 1);
+	system.wallet (0)->insert_adhoc (rai::test_genesis_key.prv);
+    rai::keypair key2;
+    system.nodes [0]->block_processor.stop ();
+    {
+		ASSERT_NE (nullptr, system.wallet (0)->send_action (rai::test_genesis_key.pub, key2.pub, rai::Gxrb_ratio));
+		ASSERT_NE (nullptr, system.wallet (0)->send_action (rai::test_genesis_key.pub, key2.pub, rai::Gxrb_ratio));
+	}
+	auto iterations (0);
+	while (system.nodes [0]->balance (rai::test_genesis_key.pub) != rai::genesis_amount - rai::Gxrb_ratio * 2)
+	{
+		system.poll ();
+		++iterations;
+		ASSERT_LT (iterations, 200);
+	}
+}
```

### rai/node/node.cpp
```diff
@@ -1621,10 +1621,6 @@ void rai::node::process_active (std::shared_ptr <rai::block> incoming)
 {
 	block_arrival.add (incoming->hash ());
 	block_processor.add (incoming);
-	if (rai::rai_network == rai::rai_networks::rai_test_network)
-	{
-		block_processor.flush ();
-	}
 }
 
 rai::process_return rai::node::process (rai::block const & block_a)
@@ -1790,6 +1786,10 @@ void rai::node::stop ()
 	bootstrap_initiator.stop ();
     bootstrap.stop ();
 	port_mapping.stop ();
+    if (block_processor_thread.joinable ())
+    {
+    	block_processor_thread.join ();
+	}
 }
 
 void rai::node::keepalive_preconfigured (std::vector <std::string> const & peers_a)
```

### rai/node/wallet.cpp
```diff
@@ -1042,11 +1042,12 @@ std::shared_ptr <rai::block> rai::wallet::receive_action (rai::send_block const
 	{
 		assert (block != nullptr);
 		node.process_active (block);
-		auto hash (block->hash ());
-		auto this_l (shared_from_this ());
-		auto source (send_a.hashables.destination);
+		node.block_processor.process_receive_many (block);
 		if (generate_work_a)
 		{
+			auto hash (block->hash ());
+			auto this_l (shared_from_this ());
+			auto source (send_a.hashables.destination);
 			node.wallets.queue_wallet_action (source, rai::wallets::generate_priority, [this_l, source, hash]
 			{
 				this_l->work_generate (source, hash);
@@ -1083,10 +1084,11 @@ std::shared_ptr <rai::block> rai::wallet::change_action (rai::account const & so
 	{
 		assert (block != nullptr);
 		node.process_active (block);
-		auto hash (block->hash ());
-		auto this_l (shared_from_this ());
+		node.block_processor.process_receive_many (block);
 		if (generate_work_a)
 		{
+			auto hash (block->hash ());
+			auto this_l (shared_from_this ());
 			node.wallets.queue_wallet_action (source_a, rai::wallets::generate_priority, [this_l, source_a, hash]
 			{
 				this_l->work_generate (source_a, hash);
@@ -1127,10 +1129,11 @@ std::shared_ptr <rai::block> rai::wallet::send_action (rai::account const & sour
 	{
 		assert (block != nullptr);
 		node.process_active (block);
-		auto hash (block->hash ());
-		auto this_l (shared_from_this ());
+		node.block_processor.process_receive_many (block);
 		if (generate_work_a)
 		{
+			auto hash (block->hash ());
+			auto this_l (shared_from_this ());
 			node.wallets.queue_wallet_action (source_a, rai::wallets::generate_priority, [this_l, source_a, hash]
 			{
 				this_l->work_generate (source_a, hash);
```
