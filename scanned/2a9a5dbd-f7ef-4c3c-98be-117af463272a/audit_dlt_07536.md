# [?] This fixes a race condition on stopping where the backlog_population thread might observe that the thread is not stopped but is not yet queued to rece

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2023-01-19
Source: https://github.com/nanocurrency/nano-node/commit/1542e0dee55795924acc317aad9a3072f14c2e0a
Type: security-commit

## Details
This fixes a race condition on stopping where the backlog_population thread might observe that the thread is not stopped but is not yet queued to receive thread notifications and might stall indefinitely.
Moving unlock during slow operation within populate_backlog since this loop also checks if it's been stoped.
Demoting stopped to a plain bool since it's used within locked contexts.
Moving activated container so it survives system destruction.

## Patch
### nano/core_test/backlog.cpp
```diff
@@ -73,11 +73,10 @@ block_list_t setup_independent_blocks (nano::test::system & system, nano::node &
 TEST (backlog, population)
 {
 	nano::mutex mutex;
+	std::unordered_set<nano::account> activated;
 	nano::test::system system{};
 	auto & node = *system.add_node ();
 
-	std::unordered_set<nano::account> activated;
-
 	node.backlog.activate_callback.add ([&] (nano::transaction const & transaction, nano::account const & account, nano::account_info const & account_info, nano::confirmation_height_info const & conf_info) {
 		nano::lock_guard<nano::mutex> lock{ mutex };
 
```

### nano/node/backlog_population.cpp
```diff
@@ -30,7 +30,9 @@ void nano::backlog_population::start ()
 
 void nano::backlog_population::stop ()
 {
+	nano::unique_lock<nano::mutex> lock{ mutex };
 	stopped = true;
+	lock.unlock ();
 	notify ();
 	nano::join_or_pass (thread);
 }
@@ -64,9 +66,7 @@ void nano::backlog_population::run ()
 			stats.inc (nano::stat::type::backlog, nano::stat::detail::loop);
 
 			triggered = false;
-			lock.unlock ();
-			populate_backlog ();
-			lock.lock ();
+			populate_backlog (lock);
 		}
 
 		condition.wait (lock, [this] () {
@@ -75,7 +75,7 @@ void nano::backlog_population::run ()
 	}
 }
 
-void nano::backlog_population::populate_backlog ()
+void nano::backlog_population::populate_backlog (nano::unique_lock<nano::mutex> & lock)
 {
 	debug_assert (config_m.frequency > 0);
 
@@ -85,13 +85,14 @@ void nano::backlog_population::populate_backlog ()
 	uint64_t total = 0;
 	while (!stopped && !done)
 	{
+		lock.unlock ();
 		{
 			auto transaction = store.tx_begin_read ();
 
 			auto count = 0u;
 			auto i = store.account.begin (transaction, next);
-			const auto end = store.account.end ();
-			for (; !stopped && i != end && count < chunk_size; ++i, ++count, ++total)
+			auto const end = store.account.end ();
+			for (; i != end && count < chunk_size; ++i, ++count, ++total)
 			{
 				stats.inc (nano::stat::type::backlog, nano::stat::detail::total);
 
@@ -101,7 +102,7 @@ void nano::backlog_population::populate_backlog ()
 			}
 			done = store.account.begin (transaction, next) == end;
 		}
-
+		lock.lock ();
 		// Give the rest of the node time to progress without holding database lock
 		std::this_thread::sleep_for (std::chrono::milliseconds (1000 / config_m.frequency));
 	}
```

### nano/node/backlog_population.hpp
```diff
@@ -59,14 +59,14 @@ class backlog_population final
 	void run ();
 	bool predicate () const;
 
-	void populate_backlog ();
+	void populate_backlog (nano::unique_lock<nano::mutex> & lock);
 	void activate (nano::transaction const &, nano::account const &);
 
 	/** This is a manual trigger, the ongoing backlog population does not use this.
 	 *  It can be triggered even when backlog population (frontiers confirmation) is disabled. */
 	bool triggered{ false };
 
-	std::atomic<bool> stopped{ false };
+	bool stopped{ false };
 	nano::condition_variable condition;
 	mutable nano::mutex mutex;
 
```
