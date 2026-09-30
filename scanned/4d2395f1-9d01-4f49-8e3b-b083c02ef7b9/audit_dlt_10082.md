# [?] Fix deadlock in tests (#2043)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2019-05-30
Source: https://github.com/nanocurrency/nano-node/commit/41278fa01dbb34289a17403d8bbb35b843d78381
Type: security-commit

## Details
Fix deadlock in tests (#2043)

* Check if node has been stopped already

* Use std::atomic<bool>::exchange (thanks cryptocode)

* Add std::atomic<bool>::exchange to bootstrap_server

## Patch
### nano/node/bootstrap.cpp
```diff
@@ -1913,9 +1913,8 @@ nano::bootstrap_server::~bootstrap_server ()
 
 void nano::bootstrap_server::stop ()
 {
-	if (!stopped)
+	if (!stopped.exchange (true))
 	{
-		stopped = true;
 		std::lock_guard<std::mutex> lock (mutex);
 		if (socket != nullptr)
 		{
```

### nano/node/node.cpp
```diff
@@ -803,25 +803,28 @@ void nano::node::start ()
 
 void nano::node::stop ()
 {
-	logger.always_log ("Node stopping");
-	block_processor.stop ();
-	if (block_processor_thread.joinable ())
+	if (!stopped.exchange (true))
 	{
-		block_processor_thread.join ();
-	}
-	vote_processor.stop ();
-	confirmation_height_processor.stop ();
-	active.stop ();
-	network.stop ();
-	if (websocket_server)
-	{
-		websocket_server->stop ();
+		logger.always_log ("Node stopping");
+		block_processor.stop ();
+		if (block_processor_thread.joinable ())
+		{
+			block_processor_thread.join ();
+		}
+		vote_processor.stop ();
+		confirmation_height_processor.stop ();
+		active.stop ();
+		network.stop ();
+		if (websocket_server)
+		{
+			websocket_server->stop ();
+		}
+		bootstrap_initiator.stop ();
+		bootstrap.stop ();
+		port_mapping.stop ();
+		checker.stop ();
+		wallets.stop ();
 	}
-	bootstrap_initiator.stop ();
-	bootstrap.stop ();
-	port_mapping.stop ();
-	checker.stop ();
-	wallets.stop ();
 }
 
 void nano::node::keepalive_preconfigured (std::vector<std::string> const & peers_a)
```

### nano/node/node.hpp
```diff
@@ -247,6 +247,7 @@ class node final : public std::enable_shared_from_this<nano::node>
 	nano::wallets wallets;
 	const std::chrono::steady_clock::time_point startup_time;
 	std::chrono::seconds unchecked_cutoff = std::chrono::seconds (7 * 24 * 60 * 60); // Week
+	std::atomic<bool> stopped{ false };
 	static double constexpr price_max = 16.0;
 	static double constexpr free_cutoff = 1024.0;
 };
```
