# [?] Constructing bulk_pull_client in the background to avoid deadlock on destruction.

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2018-03-28
Source: https://github.com/nanocurrency/nano-node/commit/36e5921b40963e12076a182451d3334b3fc3a883
Type: security-commit

## Details
Constructing bulk_pull_client in the background to avoid deadlock on destruction.

## Patch
### rai/node/bootstrap.cpp
```diff
@@ -478,18 +478,13 @@ connection (connection_a),
 pull (pull_a),
 size (size_a)
 {
-	assert (!connection->attempt->mutex.try_lock ());
+	std::lock_guard<std::mutex> mutex (connection->attempt->mutex);
 	++connection->attempt->pulling;
 	connection->attempt->condition.notify_all ();
 }
 
 rai::bulk_pull_client::~bulk_pull_client ()
 {
-	{
-		std::lock_guard<std::mutex> mutex (connection->attempt->mutex);
-		--connection->attempt->pulling;
-		connection->attempt->condition.notify_all ();
-	}
 	// If received end block is not expected end block
 	if (expected != pull.end)
 	{
@@ -500,6 +495,9 @@ rai::bulk_pull_client::~bulk_pull_client ()
 			BOOST_LOG (connection->node->log) << boost::str (boost::format ("Bulk pull end block is not expected %1% for account %2%") % pull.end.to_string () % pull.account.to_account ());
 		}
 	}
+	std::lock_guard<std::mutex> mutex (connection->attempt->mutex);
+	--connection->attempt->pulling;
+	connection->attempt->condition.notify_all ();
 }
 
 void rai::bulk_pull_client::request ()
@@ -855,10 +853,11 @@ void rai::bootstrap_attempt::request_pull (std::unique_lock<std::mutex> & lock_a
 	{
 		auto pull (pulls.front ());
 		pulls.pop_front ();
-		auto client (std::make_shared<rai::bulk_pull_client> (connection_l, pull, pulls.size ()));
+		auto size (pulls.size ());
 		// The bulk_pull_client destructor attempt to requeue_pull which can cause a deadlock if this is the last reference
 		// Dispatch request in an external thread in case it needs to be destroyed
-		node->background ([client]() {
+		node->background ([connection_l, pull, size]() {
+			auto client (std::make_shared<rai::bulk_pull_client> (connection_l, pull, size));
 			client->request ();
 		});
 	}
@@ -1271,8 +1270,9 @@ void rai::bootstrap_attempt::requeue_pull (rai::pull_info const & pull_a)
 		std::lock_guard<std::mutex> lock (mutex);
 		if (auto connection_shared = connection_frontier_request.lock ())
 		{
-			auto client (std::make_shared<rai::bulk_pull_client> (connection_shared, pull, pulls.size ()));
-			node->background ([client]() {
+			auto size (pulls.size ());
+			node->background ([connection_shared, pull, size]() {
+				auto client (std::make_shared<rai::bulk_pull_client> (connection_shared, pull, size));
 				client->request ();
 			});
 			if (node->config.logging.bulk_pull_logging ())
```
