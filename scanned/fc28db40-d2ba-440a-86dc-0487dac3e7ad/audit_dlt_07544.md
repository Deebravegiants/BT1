# [?] Prevent adjusted difficulty overflow for extremly high or low difficulty (#2260)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2019-08-31
Source: https://github.com/nanocurrency/nano-node/commit/44d53773addbc9435975a77b55f6f1af1f8ce8ce
Type: security-commit

## Details
Prevent adjusted difficulty overflow for extremly high or low difficulty (#2260)

* Prevent adjusted difficulty overflow for extremly high or low difficulty
* Use lambda function in tests
* Formatting

## Patch
### nano/core_test/active_transactions.cpp
```diff
@@ -48,16 +48,26 @@ TEST (active_transactions, adjusted_difficulty_priority)
 	auto send2 (std::make_shared<nano::state_block> (nano::test_genesis_key.pub, send1->hash (), nano::test_genesis_key.pub, nano::genesis_amount - 20 * nano::xrb_ratio, key2.pub, nano::test_genesis_key.prv, nano::test_genesis_key.pub, system.work.generate (send1->hash ())));
 	auto open1 (std::make_shared<nano::state_block> (key1.pub, 0, key1.pub, 10 * nano::xrb_ratio, send1->hash (), key1.prv, key1.pub, system.work.generate (key1.pub)));
 	auto open2 (std::make_shared<nano::state_block> (key2.pub, 0, key2.pub, 10 * nano::xrb_ratio, send2->hash (), key2.prv, key2.pub, system.work.generate (key2.pub)));
-	node1.process_active (send1);
-	node1.process_active (send2);
-	node1.process_active (open1);
-	node1.process_active (open2);
+	node1.process_active (send1); // genesis
+	node1.process_active (send2); // genesis
+	node1.process_active (open1); // key1
+	node1.process_active (open2); // key2
 	system.deadline_set (10s);
 	while (node1.active.size () != 4)
 	{
 		ASSERT_NO_ERROR (system.poll ());
 	}
 
+	// Check adjusted difficulty
+	{
+		std::lock_guard<std::mutex> active_guard (node1.active.mutex);
+		ASSERT_EQ (node1.active.roots.get<1> ().begin ()->election->status.winner->hash (), send1->hash ());
+		ASSERT_LT (node1.active.roots.find (send2->qualified_root ())->adjusted_difficulty, node1.active.roots.find (send1->qualified_root ())->adjusted_difficulty);
+		ASSERT_LT (node1.active.roots.find (open1->qualified_root ())->adjusted_difficulty, node1.active.roots.find (send1->qualified_root ())->adjusted_difficulty);
+		ASSERT_LT (node1.active.roots.find (open2->qualified_root ())->adjusted_difficulty, node1.active.roots.find (send2->qualified_root ())->adjusted_difficulty);
+	}
+
+	// Confirm elections
 	while (node1.active.size () != 0)
 	{
 		std::lock_guard<std::mutex> active_guard (node1.active.mutex);
@@ -69,7 +79,6 @@ TEST (active_transactions, adjusted_difficulty_priority)
 			it = node1.active.roots.begin ();
 		}
 	}
-
 	{
 		system.deadline_set (10s);
 		std::unique_lock<std::mutex> active_lock (node1.active.mutex);
@@ -90,19 +99,20 @@ TEST (active_transactions, adjusted_difficulty_priority)
 	auto send7 (std::make_shared<nano::state_block> (key2.pub, open2->hash (), key2.pub, 9 * nano::xrb_ratio, key3.pub, key2.prv, key2.pub, system.work.generate (open2->hash (), nano::difficulty::from_multiplier (500, node1.network_params.network.publish_threshold))));
 	auto send8 (std::make_shared<nano::state_block> (key2.pub, send7->hash (), key2.pub, 8 * nano::xrb_ratio, key3.pub, key2.prv, key2.pub, system.work.generate (send7->hash (), nano::difficulty::from_multiplier (500, node1.network_params.network.publish_threshold))));
 
-	node1.process_active (send3); //genesis
-	node1.process_active (send5); //key1
-	node1.process_active (send7); //key2
-	node1.process_active (send4); //genesis
-	node1.process_active (send6); //key1
-	node1.process_active (send8); //key2
+	node1.process_active (send3); // genesis
+	node1.process_active (send5); // key1
+	node1.process_active (send7); // key2
+	node1.process_active (send4); // genesis
+	node1.process_active (send6); // key1
+	node1.process_active (send8); // key2
 
 	system.deadline_set (10s);
 	while (node1.active.size () != 6)
 	{
 		ASSERT_NO_ERROR (system.poll ());
 	}
 
+	// Check adjusted difficulty
 	std::lock_guard<std::mutex> lock (node1.active.mutex);
 	uint64_t last_adjusted (0);
 	for (auto i (node1.active.roots.get<1> ().begin ()), n (node1.active.roots.get<1> ().end ()); i != n; ++i)
@@ -114,6 +124,117 @@ TEST (active_transactions, adjusted_difficulty_priority)
 		}
 		last_adjusted = i->adjusted_difficulty;
 	}
+	ASSERT_LT (node1.active.roots.find (send4->qualified_root ())->adjusted_difficulty, node1.active.roots.find (send3->qualified_root ())->adjusted_difficulty);
+	ASSERT_LT (node1.active.roots.find (send6->qualified_root ())->adjusted_difficulty, node1.active.roots.find (send5->qualified_root ())->adjusted_difficulty);
+	ASSERT_LT (node1.active.roots.find (send8->qualified_root ())->adjusted_difficulty, node1.active.roots.find (send7->qualified_root ())->adjusted_difficulty);
+}
+
+TEST (active_transactions, adjusted_difficulty_overflow_max)
+{
+	nano::system system;
+	nano::node_config node_config (24000, system.logging);
+	node_config.enable_voting = false;
+	node_config.frontiers_confirmation = nano::frontiers_confirmation_mode::disabled;
+	auto & node1 = *system.add_node (node_config);
+	nano::genesis genesis;
+	nano::keypair key1, key2;
+
+	auto send1 (std::make_shared<nano::state_block> (nano::test_genesis_key.pub, genesis.hash (), nano::test_genesis_key.pub, nano::genesis_amount - 10 * nano::xrb_ratio, key1.pub, nano::test_genesis_key.prv, nano::test_genesis_key.pub, system.work.generate (genesis.hash ())));
+	auto send2 (std::make_shared<nano::state_block> (nano::test_genesis_key.pub, send1->hash (), nano::test_genesis_key.pub, nano::genesis_amount - 20 * nano::xrb_ratio, key2.pub, nano::test_genesis_key.prv, nano::test_genesis_key.pub, system.work.generate (send1->hash ())));
+	auto open1 (std::make_shared<nano::state_block> (key1.pub, 0, key1.pub, 10 * nano::xrb_ratio, send1->hash (), key1.prv, key1.pub, system.work.generate (key1.pub)));
+	auto open2 (std::make_shared<nano::state_block> (key2.pub, 0, key2.pub, 10 * nano::xrb_ratio, send2->hash (), key2.prv, key2.pub, system.work.generate (key2.pub)));
+	node1.process_active (send1); // genesis
+	node1.process_active (send2); // genesis
+	node1.process_active (open1); // key1
+	node1.process_active (open2); // key2
+	system.deadline_set (10s);
+	while (node1.active.size () != 4)
+	{
+		ASSERT_NO_ERROR (system.poll ());
+	}
+
+	{
+		std::lock_guard<std::mutex> active_guard (node1.active.mutex);
+		// Update difficulty to maximum
+		auto send1_root (node1.active.roots.find (send1->qualified_root ()));
+		auto send2_root (node1.active.roots.find (send2->qualified_root ()));
+		auto open1_root (node1.active.roots.find (open1->qualified_root ()));
+		auto open2_root (node1.active.roots.find (open2->qualified_root ()));
+		auto modify_difficulty = [& roots = node1.active.roots](auto & existing_root)
+		{
+			roots.modify (existing_root, [](nano::conflict_info & info_a) {
+				info_a.difficulty = std::numeric_limits<std::uint64_t>::max ();
+			});
+		};
+		modify_difficulty (send1_root);
+		modify_difficulty (send2_root);
+		modify_difficulty (open1_root);
+		modify_difficulty (open2_root);
+		node1.active.adjust_difficulty (send2->hash ());
+		// Test overflow
+		ASSERT_EQ (node1.active.roots.get<1> ().begin ()->election->status.winner->hash (), send1->hash ());
+		ASSERT_EQ (send1_root->adjusted_difficulty, std::numeric_limits<std::uint64_t>::max ());
+		ASSERT_LT (send2_root->adjusted_difficulty, send1_root->adjusted_difficulty);
+		ASSERT_LT (open1_root->adjusted_difficulty, send1_root->adjusted_difficulty);
+		ASSERT_LT (open2_root->adjusted_difficulty, send2_root->adjusted_difficulty);
+	}
+}
+
+TEST (active_transactions, adjusted_difficulty_overflow_min)
+{
+	nano::system system;
+	nano::node_config node_config (24000, system.logging);
+	node_config.enable_voting = false;
+	node_config.frontiers_confirmation = nano::frontiers_confirmation_mode::disabled;
+	auto & node1 = *system.add_node (node_config);
+	nano::genesis genesis;
+	nano::keypair key1, key2, key3;
+
+	auto send1 (std::make_shared<nano::state_block> (nano::test_genesis_key.pub, genesis.hash (), nano::test_genesis_key.pub, nano::genesis_amount - 10 * nano::xrb_ratio, key1.pub, nano::test_genesis_key.prv, nano::test_genesis_key.pub, system.work.generate (genesis.hash ())));
+	auto send2 (std::make_shared<nano::state_block> (nano::test_genesis_key.pub, send1->hash (), nano::test_genesis_key.pub, nano::genesis_amount - 20 * nano::xrb_ratio, key2.pub, nano::test_genesis_key.prv, nano::test_genesis_key.pub, system.work.generate (send1->hash ())));
+	auto open1 (std::make_shared<nano::state_block> (key1.pub, 0, key1.pub, 10 * nano::xrb_ratio, send1->hash (), key1.prv, key1.pub, system.work.generate (key1.pub)));
+	auto open2 (std::make_shared<nano::state_block> (key2.pub, 0, key2.pub, 10 * nano::xrb_ratio, send2->hash (), key2.prv, key2.pub, system.work.generate (key2.pub)));
+	auto send3 (std::make_shared<nano::state_block> (key2.pub, open2->hash (), key2.pub, 9 * nano::xrb_ratio, key3.pub, key2.prv, key2.pub, system.work.generate (open2->hash ())));
+	node1.process_active (send1); // genesis
+	node1.process_active (send2); // genesis
+	node1.process_active (open1); // key1
+	node1.process_active (open2); // key2
+	node1.process_active (send3); // key2
+	system.deadline_set (10s);
+	while (node1.active.size () != 5)
+	{
+		ASSERT_NO_ERROR (system.poll ());
+	}
+
+	{
+		std::lock_guard<std::mutex> active_guard (node1.active.mutex);
+		// Update difficulty to minimum
+		auto send1_root (node1.active.roots.find (send1->qualified_root ()));
+		auto send2_root (node1.active.roots.find (send2->qualified_root ()));
+		auto open1_root (node1.active.roots.find (open1->qualified_root ()));
+		auto open2_root (node1.active.roots.find (open2->qualified_root ()));
+		auto send3_root (node1.active.roots.find (send3->qualified_root ()));
+		auto modify_difficulty = [& roots = node1.active.roots](auto & existing_root)
+		{
+			roots.modify (existing_root, [](nano::conflict_info & info_a) {
+				info_a.difficulty = std::numeric_limits<std::uint64_t>::min () + 1;
+			});
+		};
+		modify_difficulty (send1_root);
+		modify_difficulty (send2_root);
+		modify_difficulty (open1_root);
+		modify_difficulty (open2_root);
+		modify_difficulty (send3_root);
+		node1.active.adjust_difficulty (send1->hash ());
+		// Test overflow
+		ASSERT_EQ (node1.active.roots.get<1> ().begin ()->election->status.winner->hash (), send1->hash ());
+		ASSERT_EQ (send1_root->adjusted_difficulty, std::numeric_limits<std::uint64_t>::min () + 3);
+		ASSERT_LT (send2_root->adjusted_difficulty, send1_root->adjusted_difficulty);
+		ASSERT_LT (open1_root->adjusted_difficulty, send1_root->adjusted_difficulty);
+		ASSERT_LT (open2_root->adjusted_difficulty, send2_root->adjusted_difficulty);
+		ASSERT_LT (send3_root->adjusted_difficulty, open2_root->adjusted_difficulty);
+		ASSERT_EQ (send3_root->adjusted_difficulty, std::numeric_limits<std::uint64_t>::min ());
+	}
 }
 
 TEST (active_transactions, keep_local)
```

### nano/node/active_transactions.cpp
```diff
@@ -629,6 +629,8 @@ void nano::active_transactions::adjust_difficulty (nano::block_hash const & hash
 	std::unordered_set<nano::block_hash> processed_blocks;
 	std::vector<std::pair<nano::qualified_root, int64_t>> elections_list;
 	double sum (0.);
+	int64_t highest_level (0);
+	int64_t lowest_level (0);
 	while (!remaining_blocks.empty ())
 	{
 		auto const & item (remaining_blocks.front ());
@@ -665,6 +667,14 @@ void nano::active_transactions::adjust_difficulty (nano::block_hash const & hash
 				{
 					sum += nano::difficulty::to_multiplier (existing_root->difficulty, node.network_params.network.publish_threshold);
 					elections_list.emplace_back (root, level);
+					if (level > highest_level)
+					{
+						highest_level = level;
+					}
+					else if (level < lowest_level)
+					{
+						lowest_level = level;
+					}
 				}
 			}
 		}
@@ -674,19 +684,26 @@ void nano::active_transactions::adjust_difficulty (nano::block_hash const & hash
 	{
 		double multiplier = sum / elections_list.size ();
 		uint64_t average = nano::difficulty::from_multiplier (multiplier, node.network_params.network.publish_threshold);
-		auto highest_level = elections_list.back ().second;
-		uint64_t divider = 1;
-		// Possible overflow check, will not occur for negative levels
-		if ((multiplier + highest_level) > 10000000000)
+		// Prevent overflow
+		int64_t limiter (0);
+		if (std::numeric_limits<std::uint64_t>::max () - average < highest_level)
+		{
+			// Highest adjusted difficulty value should be std::numeric_limits<std::uint64_t>::max ()
+			limiter = std::numeric_limits<std::uint64_t>::max () - average + highest_level;
+			assert (std::numeric_limits<std::uint64_t>::max () == average + highest_level - limiter);
+		}
+		else if (average < std::numeric_limits<std::uint64_t>::min () - lowest_level)
 		{
-			divider = static_cast<uint64_t> (((multiplier + highest_level) / 10000000000) + 1);
+			// Lowest adjusted difficulty value should be std::numeric_limits<std::uint64_t>::min ()
+			limiter = std::numeric_limits<std::uint64_t>::min () - average + lowest_level;
+			assert (std::numeric_limits<std::uint64_t>::min () == average + lowest_level - limiter);
 		}
 
 		// Set adjusted difficulty
 		for (auto & item : elections_list)
 		{
 			auto existing_root (roots.find (item.first));
-			uint64_t difficulty_a = average + item.second / divider;
+			uint64_t difficulty_a = average + item.second - limiter;
 			roots.modify (existing_root, [difficulty_a](nano::conflict_info & info_a) {
 				info_a.adjusted_difficulty = difficulty_a;
 			});
```
