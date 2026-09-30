# [?] Fixing a race condition in doing rollbacks where successor blocks wouldn't be attempted to be inserted until the next syncing round.

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2017-12-24
Source: https://github.com/nanocurrency/nano-node/commit/94069786d3c5d1c661b20c7555d0bbb555f3c665
Type: security-commit

## Details
Fixing a race condition in doing rollbacks where successor blocks wouldn't be attempted to be inserted until the next syncing round.

## Patch
### rai/core_test/gap_cache.cpp
```diff
@@ -83,11 +83,11 @@ TEST (gap_cache, two_dependencies)
 	auto send2 (std::make_shared <rai::send_block> (send1->hash (), key.pub, 0, rai::test_genesis_key.prv, rai::test_genesis_key.pub, system.work.generate (send1->hash ())));
 	auto open (std::make_shared <rai::open_block> (send1->hash (), key.pub, key.pub, key.prv, key.pub, system.work.generate (key.pub)));
 	ASSERT_EQ (0, system.nodes [0]->gap_cache.blocks.size ());
-	system.nodes [0]->block_processor.process_receive_many (send2);
+	system.nodes [0]->block_processor.process_receive_many (rai::block_processor_item (send2));
 	ASSERT_EQ (1, system.nodes [0]->gap_cache.blocks.size ());
-	system.nodes [0]->block_processor.process_receive_many (open);
+	system.nodes [0]->block_processor.process_receive_many (rai::block_processor_item (open));
 	ASSERT_EQ (2, system.nodes [0]->gap_cache.blocks.size ());
-	system.nodes [0]->block_processor.process_receive_many (send1);
+	system.nodes [0]->block_processor.process_receive_many (rai::block_processor_item (send1));
 	ASSERT_EQ (0, system.nodes [0]->gap_cache.blocks.size ());
 	rai::transaction transaction (system.nodes [0]->store.environment, nullptr, false);
 	ASSERT_TRUE (system.nodes [0]->store.block_exists (transaction, send1->hash ()));
```

### rai/core_test/node.cpp
```diff
@@ -914,9 +914,9 @@ TEST (node, fork_bootstrap_flip)
 	rai::keypair key2;
 	auto send2 (std::make_shared <rai::send_block> (latest, key2.pub, rai::genesis_amount - rai::Gxrb_ratio, rai::test_genesis_key.prv, rai::test_genesis_key.pub, system0.work.generate (latest)));
 	// Insert but don't rebroadcast, simulating settled blocks
-	node1.block_processor.process_receive_many (send1);
+	node1.block_processor.process_receive_many (rai::block_processor_item (send1));
 	node1.block_processor.flush ();
-	node2.block_processor.process_receive_many (send2);
+	node2.block_processor.process_receive_many (rai::block_processor_item (send2));
 	node2.block_processor.flush ();
 	{
 		rai::transaction transaction (node2.store.environment, nullptr, false);
```

### rai/node/bootstrap.cpp
```diff
@@ -173,7 +173,7 @@ void rai::bootstrap_client::start_timeout ()
 			auto this_l (this_w.lock ());
 			if (this_l != nullptr)
 			{
-                BOOST_LOG (this_l->node->log) << boost::str (boost::format ("Disconnecting from %1% due to timeout") % this_l->endpoint);
+				BOOST_LOG (this_l->node->log) << boost::str (boost::format ("Disconnecting from %1% due to timeout") % this_l->endpoint);
 				this_l->socket.close ();
 			}
 		}
@@ -573,19 +573,19 @@ void rai::bulk_pull_client::received_block (boost::system::error_code const & ec
 		std::shared_ptr <rai::block> block (rai::deserialize_block (stream));
 		if (block != nullptr)
 		{
-            auto hash (block->hash ());
-            if (connection->node->config.logging.bulk_pull_logging ())
-            {
-                std::string block_l;
-                block->serialize_json (block_l);
-                BOOST_LOG (connection->node->log) << boost::str (boost::format ("Pulled block %1% %2%") % hash.to_string () % block_l);
-            }
+			auto hash (block->hash ());
+			if (connection->node->config.logging.bulk_pull_logging ())
+			{
+				std::string block_l;
+				block->serialize_json (block_l);
+				BOOST_LOG (connection->node->log) << boost::str (boost::format ("Pulled block %1% %2%") % hash.to_string () % block_l);
+			}
 			if (hash == expected)
 			{
 				expected = block->previous ();
 			}
 			auto attempt_l (connection->attempt);
-			attempt_l->node->block_processor.add (block, [attempt_l] (MDB_txn * transaction_a, rai::process_return result_a, std::shared_ptr <rai::block> block_a)
+			attempt_l->node->block_processor.add (rai::block_processor_item (block, [attempt_l] (MDB_txn * transaction_a, rai::process_return result_a, std::shared_ptr <rai::block> block_a)
 			{
 				switch (result_a.code)
 				{
@@ -605,13 +605,13 @@ void rai::bulk_pull_client::received_block (boost::system::error_code const & ec
 					default:
 						break;
 				}
-			});
-            receive_block ();
+			}));
+			receive_block ();
+		}
+		else
+		{
+			BOOST_LOG (connection->node->log) << "Error deserializing block received from pull request";
 		}
-        else
-        {
-            BOOST_LOG (connection->node->log) << "Error deserializing block received from pull request";
-        }
 	}
 	else
 	{
@@ -1040,7 +1040,7 @@ void rai::bootstrap_initiator::bootstrap ()
 
 void rai::bootstrap_initiator::bootstrap (rai::endpoint const & endpoint_a)
 {
-    node.peers.insert (endpoint_a, 0);
+    node.peers.insert (endpoint_a, 0x5);
 	bootstrap ();
 	std::lock_guard <std::mutex> lock (mutex);
 	if (attempt != nullptr)
```

### rai/node/node.cpp
```diff
@@ -1061,6 +1061,28 @@ bool rai::rep_crawler::exists (rai::block_hash const & hash_a)
 	return active.count (hash_a) != 0;
 }
 
+rai::block_processor_item::block_processor_item (std::shared_ptr <rai::block> block_a) :
+block_processor_item (block_a, nullptr, false)
+{
+}
+
+rai::block_processor_item::block_processor_item (std::shared_ptr <rai::block> block_a, bool force_a) :
+block_processor_item (block_a, nullptr, force_a)
+{
+}
+
+rai::block_processor_item::block_processor_item (std::shared_ptr <rai::block> block_a, std::function <void (MDB_txn *, rai::process_return, std::shared_ptr <rai::block>)> callback_a) :
+block_processor_item (block_a, callback_a, false)
+{
+}
+
+rai::block_processor_item::block_processor_item (std::shared_ptr <rai::block> block_a, std::function <void (MDB_txn *, rai::process_return, std::shared_ptr <rai::block>)> callback_a, bool force_a) :
+block (block_a),
+callback (callback_a),
+force (force_a)
+{
+}
+
 rai::block_processor::block_processor (rai::node & node_a) :
 stopped (false),
 idle (true),
@@ -1089,10 +1111,10 @@ void rai::block_processor::flush ()
     }
 }
 
-void rai::block_processor::add (std::shared_ptr <rai::block> block_a, std::function <void (MDB_txn *, rai::process_return, std::shared_ptr <rai::block>)> action_a)
+void rai::block_processor::add (rai::block_processor_item const & item_a)
 {
     std::lock_guard <std::mutex> lock (mutex);
-    blocks.push_back (std::make_pair (block_a, action_a));
+    blocks.push_back (item_a);
     condition.notify_all ();
 }
 
@@ -1103,7 +1125,7 @@ void rai::block_processor::process_blocks ()
 	{
 		if (!blocks.empty ())
 		{
-			std::deque <std::pair <std::shared_ptr <rai::block>, std::function <void (MDB_txn *, rai::process_return, std::shared_ptr <rai::block>)>>> blocks_processing;
+			std::deque <rai::block_processor_item> blocks_processing;
 			std::swap (blocks, blocks_processing);
 			lock.unlock ();
 			process_receive_many (blocks_processing);
@@ -1121,14 +1143,14 @@ void rai::block_processor::process_blocks ()
 	}
 }
 
-void rai::block_processor::process_receive_many (std::shared_ptr <rai::block> block_a, std::function <void (MDB_txn *, rai::process_return, std::shared_ptr <rai::block>)> completed_a)
+void rai::block_processor::process_receive_many (rai::block_processor_item const & item_a)
 {
-	std::deque <std::pair <std::shared_ptr <rai::block>, std::function <void (MDB_txn *, rai::process_return, std::shared_ptr <rai::block>)>>> blocks_processing;
-	blocks_processing.push_back (std::make_pair (block_a, completed_a));
+	std::deque <rai::block_processor_item> blocks_processing;
+	blocks_processing.push_back (item_a);
 	process_receive_many (blocks_processing);
 }
 
-void rai::block_processor::process_receive_many (std::deque <std::pair <std::shared_ptr <rai::block>, std::function <void (MDB_txn *, rai::process_return, std::shared_ptr <rai::block>)>>> & blocks_processing)
+void rai::block_processor::process_receive_many (std::deque <rai::block_processor_item> & blocks_processing)
 {
     while (!blocks_processing.empty ())
 	{
@@ -1140,22 +1162,35 @@ void rai::block_processor::process_receive_many (std::deque <std::pair <std::sha
 			{
 				auto item (blocks_processing.front ());
 				blocks_processing.pop_front ();
-				auto hash (item.first->hash ());
-				auto process_result (process_receive_one (transaction, item.first));
-				item.second (transaction, process_result, item.first);
+				auto hash (item.block->hash ());
+				if (item.force)
+				{
+					auto successor (node.ledger.successor (transaction, item.block->root ()));
+					if (successor != nullptr && successor->hash () != hash)
+					{
+						// Replace our block with the winner and roll back any dependent blocks
+						BOOST_LOG (node.log) << boost::str (boost::format ("Rolling back %1% and replacing with %2%") % successor->hash ().to_string () % hash.to_string ());
+						node.ledger.rollback (transaction, successor->hash ());
+					}
+				}
+				auto process_result (process_receive_one (transaction, item.block));
+				if (item.callback)
+				{
+					item.callback (transaction, process_result, item.block);
+				}
 				switch (process_result.code)
 				{
 					case rai::process_result::progress:
 					{
-						progress.push_back (std::make_pair (item.first, process_result));
+						progress.push_back (std::make_pair (item.block, process_result));
 					}
 					case rai::process_result::old:
 					{
 						auto cached (node.store.unchecked_get (transaction, hash));
 						for (auto i (cached.begin ()), n (cached.end ()); i != n; ++i)
 						{
 							node.store.unchecked_del (transaction, hash, **i);
-							blocks_processing.push_front (std::make_pair (*i, [] (MDB_txn *, rai::process_return, std::shared_ptr <rai::block>) {}));
+							blocks_processing.push_front (rai::block_processor_item (*i));
 						}
 						std::lock_guard <std::mutex> lock (node.gap_cache.mutex);
 						node.gap_cache.blocks.get <1> ().erase (hash);
@@ -1662,14 +1697,22 @@ rai::endpoint rai::peer_container::bootstrap_peer ()
 {
     rai::endpoint result (boost::asio::ip::address_v6::any (), 0);
     std::lock_guard <std::mutex> lock (mutex);
-	auto first (peers.get <4> ().begin ());
-	if (first != peers.get <4> ().end ())
+	;
+	for (auto i (peers.get <4> ().begin ()), n (peers.get <4> ().end ()); i != n;)
 	{
-		result = first->endpoint;
-		peers.get <4> ().modify (first, [] (rai::peer_information & peer_a)
+		if (i->network_version >= 0x5)
 		{
-			peer_a.last_bootstrap_attempt = std::chrono::system_clock::now ();
-		});
+			result = i->endpoint;
+			peers.get <4> ().modify (i, [] (rai::peer_information & peer_a)
+			{
+				peer_a.last_bootstrap_attempt = std::chrono::system_clock::now ();
+			});
+			i = n;
+		}
+		else
+		{
+			++i;
+		}
     }
     return result;
 }
@@ -2684,16 +2727,17 @@ void rai::election::confirm_once (MDB_txn * transaction_a)
 		auto tally_l (node.ledger.tally (transaction_a, votes));
 		assert (tally_l.size () > 0);
 		auto winner (tally_l.begin ());
-		if (!(*winner->second == *last_winner))
+		auto block_l (winner->second);
+		if (!(*block_l == *last_winner))
 		{
 			if (winner->first > minimum_treshold (transaction_a, node.ledger))
 			{
-				BOOST_LOG (node.log) << boost::str (boost::format ("Rolling back %1% and replacing with %2%") % last_winner->hash ().to_string () % winner->second->hash ().to_string ());
-				// Replace our block with the winner and roll back any dependent blocks
-				node.ledger.rollback (transaction_a, last_winner->hash ());
-				node.ledger.process (transaction_a, *winner->second);
-				node.block_processor.add (winner->second);
-				last_winner = std::move (winner->second);
+				auto node_l (node.shared ());
+				node.background ([node_l, block_l] ()
+				{
+					node_l->block_processor.process_receive_many (rai::block_processor_item (block_l, true));
+				});
+				last_winner = block_l;
 			}
 			else
 			{
```

### rai/node/node.hpp
```diff
@@ -431,24 +431,35 @@ class rep_crawler
 	std::mutex mutex;
 	std::unordered_set <rai::block_hash> active;
 };
+class block_processor_item
+{
+public:
+	block_processor_item (std::shared_ptr <rai::block>);
+	block_processor_item (std::shared_ptr <rai::block>, bool);
+	block_processor_item (std::shared_ptr <rai::block>, std::function <void (MDB_txn *, rai::process_return, std::shared_ptr <rai::block>)>);
+	block_processor_item (std::shared_ptr <rai::block>, std::function <void (MDB_txn *, rai::process_return, std::shared_ptr <rai::block>)>, bool);
+	std::shared_ptr <rai::block> block;
+	std::function <void (MDB_txn *, rai::process_return, std::shared_ptr <rai::block>)> callback;
+	bool force;
+};
 // Processing blocks is a potentially long IO operation
 // This class isolates block insertion from other operations like servicing network operations
 class block_processor
 {
 public:
 	block_processor (rai::node &);
-    ~block_processor ();
-    void stop ();
-    void flush ();
-	void add (std::shared_ptr <rai::block>, std::function <void (MDB_txn *, rai::process_return, std::shared_ptr <rai::block>)> = [] (MDB_txn *, rai::process_return, std::shared_ptr <rai::block>) {});
-	void process_receive_many (std::shared_ptr <rai::block>, std::function <void (MDB_txn *, rai::process_return, std::shared_ptr <rai::block>)> = [] (MDB_txn *, rai::process_return, std::shared_ptr <rai::block>) {});
-	void process_receive_many (std::deque <std::pair <std::shared_ptr <rai::block>, std::function <void (MDB_txn *, rai::process_return, std::shared_ptr <rai::block>)>>> &);
-    rai::process_return process_receive_one (MDB_txn *, std::shared_ptr <rai::block>);
+	~block_processor ();
+	void stop ();
+	void flush ();
+	void add (rai::block_processor_item const &);
+	void process_receive_many (rai::block_processor_item const &);
+	void process_receive_many (std::deque <rai::block_processor_item> &);
+	rai::process_return process_receive_one (MDB_txn *, std::shared_ptr <rai::block>);
 	void process_blocks ();
 private:
 	bool stopped;
-    bool idle;
-	std::deque <std::pair <std::shared_ptr <rai::block>, std::function <void (MDB_txn *, rai::process_return, std::shared_ptr <rai::block>)>>> blocks;
+	bool idle;
+	std::deque <rai::block_processor_item> blocks;
 	std::mutex mutex;
 	std::condition_variable condition;
 	rai::node & node;
```
