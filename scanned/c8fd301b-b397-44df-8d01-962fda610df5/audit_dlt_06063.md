# [?] Avoid tcp channel close deadlock (#5079)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2026-06-08
Source: https://github.com/nanocurrency/nano-node/commit/96aa784aecc0242157985579a937bc7075fa2b59
Type: security-commit

## Details
Avoid tcp channel close deadlock (#5079)

* Avoid tcp channel close deadlock

Swap the channel set out from under tcp_channels::mutex before closing entries. This avoids holding the mutex while close paths block on io_context shutdown.

* Avoid mutex nesting in bootstrap maintenance

Rename the cleanup loop and thread to maintenance since it now handles broader periodic work. Snapshot bootstrap channels without holding the bootstrap mutex before syncing peer scoring, avoiding network mutex nesting under the bootstrap lock.

## Patch
### nano/lib/stats_enums.hpp
```diff
@@ -149,6 +149,7 @@ enum class detail
 	total,
 	loop,
 	loop_cleanup,
+	loop_maintenance,
 	loop_checkup,
 	loop_reps,
 	loop_receivable,
```

### nano/lib/thread_roles.cpp
```diff
@@ -133,8 +133,8 @@ std::string nano::thread_role::get_string (nano::thread_role::name role)
 		case nano::thread_role::name::bootstrap_frontier_scan:
 			thread_role_name_string = "Bootstrap front";
 			break;
-		case nano::thread_role::name::bootstrap_cleanup:
-			thread_role_name_string = "Bootstrap clean";
+		case nano::thread_role::name::bootstrap_maintenance:
+			thread_role_name_string = "Bootstrap maint";
 			break;
 		case nano::thread_role::name::bootstrap_worker:
 			thread_role_name_string = "Bootstrap work";
```

### nano/lib/thread_roles.hpp
```diff
@@ -50,7 +50,7 @@ enum class name
 	bootstrap_dependency_walker,
 	bootstrap_dependency_sync,
 	bootstrap_frontier_scan,
-	bootstrap_cleanup,
+	bootstrap_maintenance,
 	bootstrap_worker,
 	bootstrap_server,
 	scheduler_hinted,
```

### nano/node/bootstrap/bootstrap_context.cpp
```diff
@@ -85,13 +85,13 @@ nano::ledger_notifications & ledger_notifications_a, nano::block_processor & blo
 bootstrap_context::~bootstrap_context ()
 {
 	// All threads must be stopped before destruction
-	debug_assert (!cleanup_thread.joinable ());
+	debug_assert (!maintenance_thread.joinable ());
 	debug_assert (!workers.alive ());
 }
 
 void bootstrap_context::start ()
 {
-	debug_assert (!cleanup_thread.joinable ());
+	debug_assert (!maintenance_thread.joinable ());
 
 	if (!config.enable)
 	{
@@ -121,9 +121,9 @@ void bootstrap_context::start ()
 		frontier_strat.start ();
 	}
 
-	cleanup_thread = std::thread ([this] () {
-		nano::thread_role::set (nano::thread_role::name::bootstrap_cleanup);
-		run_cleanup ();
+	maintenance_thread = std::thread ([this] () {
+		nano::thread_role::set (nano::thread_role::name::bootstrap_maintenance);
+		run_maintenance ();
 	});
 }
 
@@ -139,7 +139,7 @@ void bootstrap_context::stop ()
 	database_strat.stop ();
 	dependency_strat.stop ();
 	frontier_strat.stop ();
-	nano::join_or_pass (cleanup_thread);
+	nano::join_or_pass (maintenance_thread);
 
 	workers.stop ();
 }
@@ -430,11 +430,16 @@ void bootstrap_context::inspect (secure::transaction const & tx, nano::block_sta
 	}
 }
 
-void bootstrap_context::cleanup ()
+void bootstrap_context::maintenance (nano::unique_lock<nano::mutex> & lock)
 {
-	debug_assert (!mutex.try_lock ());
+	debug_assert (lock.owns_lock ());
+
+	// Snapshot peers without the bootstrap mutex held, to avoid nesting the network mutex under it
+	lock.unlock ();
+	auto channels = network.list (/* all */ 0, network_constants.bootstrap_protocol_version_min);
+	lock.lock ();
 
-	scoring.sync (network.list (/* all */ 0, network_constants.bootstrap_protocol_version_min));
+	scoring.sync (channels);
 	scoring.timeout ();
 
 	throttle.resize (compute_throttle_size ());
@@ -457,13 +462,13 @@ void bootstrap_context::cleanup ()
 	}
 }
 
-void bootstrap_context::run_cleanup ()
+void bootstrap_context::run_maintenance ()
 {
 	nano::unique_lock<nano::mutex> lock{ mutex };
 	while (!stopped)
 	{
-		stats.inc (nano::stat::type::bootstrap, nano::stat::detail::loop_cleanup);
-		cleanup ();
+		stats.inc (nano::stat::type::bootstrap, nano::stat::detail::loop_maintenance);
+		maintenance (lock);
 		condition.wait_for (lock, nano::is_dev_run () ? 500ms : 5s, [this] () { return stopped; });
 	}
 }
```

### nano/node/bootstrap/bootstrap_context.hpp
```diff
@@ -120,8 +120,8 @@ class bootstrap_context
 
 	verify_result verify (nano::messages::asc_pull_ack::blocks_payload const & response, async_tag const & tag) const;
 
-	void cleanup ();
-	void run_cleanup ();
+	void maintenance (nano::unique_lock<nano::mutex> & lock);
+	void run_maintenance ();
 
 public: // Dependencies
 	nano::bootstrap_config const & config;
@@ -181,7 +181,7 @@ class bootstrap_context
 	mutable nano::mutex mutex;
 	mutable nano::condition_variable condition;
 
-	std::thread cleanup_thread;
+	std::thread maintenance_thread;
 
 	nano::thread_pool workers;
 	nano::random_generator_mt rng;
```

### nano/node/transport/tcp_channels.cpp
```diff
@@ -44,16 +44,19 @@ void nano::transport::tcp_channels::stop ()
 
 void nano::transport::tcp_channels::close ()
 {
-	nano::lock_guard<nano::mutex> lock{ mutex };
+	// Close outside the lock; close() blocks on an io_context join and can deadlock if held under the mutex
+	decltype (channels) channels_l;
+	{
+		nano::lock_guard<nano::mutex> lock{ mutex };
+		channels_l.swap (channels);
+	}
 
-	for (auto const & entry : channels)
+	for (auto const & entry : channels_l)
 	{
 		entry.socket->close ();
 		entry.server->close ();
 		entry.channel->close ();
 	}
-
-	channels.clear ();
 }
 
 bool nano::transport::tcp_channels::check (const nano::tcp_endpoint & endpoint, const nano::account & node_id) const
```
