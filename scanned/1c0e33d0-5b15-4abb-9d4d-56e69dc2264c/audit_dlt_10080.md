# [?] Avoid potential deadlock in work watcher (#2887)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2020-08-19
Source: https://github.com/nanocurrency/nano-node/commit/3a73ef9b7fa57385dd334876ebb48a3fbc822acc
Type: security-commit

## Details
Avoid potential deadlock in work watcher (#2887)

* Add test that deadlocks due to a bug in the work watcher

* Unlock mutex before notifying work_cancel observers to avoid the deadlock

## Patch
### nano/core_test/wallet.cpp
```diff
@@ -1216,6 +1216,52 @@ TEST (work_watcher, cancel)
 	}
 }
 
+TEST (work_watcher, confirm_while_generating)
+{
+	// Ensure proper behavior when confirmation happens during work generation
+	nano::system system;
+	nano::node_config node_config (nano::get_available_port (), system.logging);
+	node_config.work_threads = 1;
+	node_config.work_watcher_period = 1s;
+	node_config.max_work_generate_multiplier = 1e6;
+	node_config.enable_voting = false;
+	auto & node = *system.add_node (node_config);
+	auto & wallet (*system.wallet (0));
+	wallet.insert_adhoc (nano::dev_genesis_key.prv, false);
+	nano::keypair key;
+	auto work1 (node.work_generate_blocking (nano::dev_genesis_key.pub));
+	auto const block1 (wallet.send_action (nano::dev_genesis_key.pub, key.pub, 100, *work1, false));
+	{
+		nano::unique_lock<std::mutex> lock (node.active.mutex);
+		// Prevent active difficulty repopulating multipliers
+		node.network_params.network.request_interval_ms = 10000;
+		// Fill multipliers_cb and update active difficulty;
+		for (auto i (0); i < node.active.multipliers_cb.size (); i++)
+		{
+			node.active.multipliers_cb.push_back (node.config.max_work_generate_multiplier);
+		}
+		node.active.update_active_multiplier (lock);
+	}
+	// Wait for work generation to start
+	ASSERT_TIMELY (5s, 0 != node.work.size ());
+	// Attach a callback to work cancellations
+	std::atomic<bool> notified{ false };
+	node.observers.work_cancel.add ([&notified, &block1](nano::root const & root_a) {
+		EXPECT_EQ (root_a, block1->root ());
+		notified = true;
+	});
+	// Confirm the block
+	{
+		nano::lock_guard<std::mutex> guard (node.active.mutex);
+		ASSERT_EQ (1, node.active.roots.size ());
+		node.active.roots.begin ()->election->confirm_once ();
+	}
+	ASSERT_TIMELY (5s, node.block_confirmed (block1->hash ()));
+	ASSERT_EQ (0, node.work.size ());
+	ASSERT_TRUE (notified);
+	ASSERT_FALSE (node.wallets.watcher->is_watched (block1->qualified_root ()));
+}
+
 // Ensure the minimum limited difficulty is enough for the highest threshold
 TEST (wallet, limited_difficulty)
 {
```

### nano/node/wallet.cpp
```diff
@@ -1399,11 +1399,12 @@ void nano::work_watcher::watching (nano::qualified_root const & root_a, std::sha
 
 void nano::work_watcher::remove (nano::block const & block_a)
 {
-	nano::lock_guard<std::mutex> lock (mutex);
+	nano::unique_lock<std::mutex> lock (mutex);
 	auto existing (watched.find (block_a.qualified_root ()));
 	if (existing != watched.end ())
 	{
 		watched.erase (existing);
+		lock.unlock ();
 		node.observers.work_cancel.notify (block_a.root ());
 	}
 }
```
