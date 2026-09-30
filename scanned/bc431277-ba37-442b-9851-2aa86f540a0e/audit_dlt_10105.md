# [?] Fixing possible deadlock between bootstrap_client destructor since connecting holds by weak_ptr.

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2017-03-17
Source: https://github.com/nanocurrency/nano-node/commit/4008c7235900bea4d5318ffdc8bd3d2e069bcfef
Type: security-commit

## Details
Fixing possible deadlock between bootstrap_client destructor since connecting holds by weak_ptr.

## Patch
### rai/node/bootstrap.cpp
```diff
@@ -778,46 +778,54 @@ rai::bootstrap_attempt::~bootstrap_attempt ()
 void rai::bootstrap_attempt::populate_connections ()
 {
 	std::weak_ptr <rai::bootstrap_attempt> this_w (shared_from_this ());
-	std::lock_guard <std::mutex> lock (mutex);
-	if (connecting.size () + active.size () + idle.size () < 1)
-	{
-		start_connection (node->peers.bootstrap_peer ());
-	}
-	switch (state)
+	std::shared_ptr <rai::bootstrap_client> client;
 	{
-		case rai::attempt_state::starting:
-		case rai::attempt_state::requesting_frontiers:
-		case rai::attempt_state::requesting_pulls:
-			node->alarm.add (std::chrono::system_clock::now () + std::chrono::seconds (1), [this_w] ()
-			{
-				if (auto this_l = this_w.lock ())
+		std::lock_guard <std::mutex> lock (mutex);
+		if (connecting.size () + active.size () + idle.size () < 1)
+		{
+			client = start_connection (node->peers.bootstrap_peer ());
+		}
+		switch (state)
+		{
+			case rai::attempt_state::starting:
+			case rai::attempt_state::requesting_frontiers:
+			case rai::attempt_state::requesting_pulls:
+				node->alarm.add (std::chrono::system_clock::now () + std::chrono::seconds (1), [this_w] ()
 				{
-					this_l->populate_connections ();
-				}
-			});
-			break;
-		default:
-			break;
+					if (auto this_l = this_w.lock ())
+					{
+						this_l->populate_connections ();
+					}
+				});
+				break;
+			default:
+				break;
+		}
 	}
 }
 
 void rai::bootstrap_attempt::add_connection (rai::endpoint const & endpoint_a)
 {
-	std::lock_guard <std::mutex> lock (mutex);
-	start_connection (endpoint_a);
+	std::shared_ptr <rai::bootstrap_client> client;
+	{
+		std::lock_guard <std::mutex> lock (mutex);
+		client = start_connection (endpoint_a);
+	}
 }
 
-void rai::bootstrap_attempt::start_connection (rai::endpoint const & endpoint_a)
+std::shared_ptr <rai::bootstrap_client> rai::bootstrap_attempt::start_connection (rai::endpoint const & endpoint_a)
 {
 	assert (!mutex.try_lock ());
+	std::shared_ptr <rai::bootstrap_client> client;
 	if (attempted.find (endpoint_a) == attempted.end ())
 	{
 		attempted.insert (endpoint_a);
 		auto node_l (node->shared ());
-		auto client (std::make_shared <rai::bootstrap_client> (node_l, shared_from_this (), rai::tcp_endpoint (endpoint_a.address (), endpoint_a.port ())));
+		client = std::make_shared <rai::bootstrap_client> (node_l, shared_from_this (), rai::tcp_endpoint (endpoint_a.address (), endpoint_a.port ()));
 		connecting [client.get ()] = client;
 		client->run ();
 	}
+	return client;
 }
 
 void rai::bootstrap_attempt::stop ()
```

### rai/node/bootstrap.hpp
```diff
@@ -113,7 +113,7 @@ class bootstrap_attempt : public std::enable_shared_from_this <bootstrap_attempt
 	rai::attempt_state state;
 	std::unordered_set <rai::endpoint> attempted;
 private:
-	void start_connection (rai::endpoint const &);
+	std::shared_ptr <rai::bootstrap_client> start_connection (rai::endpoint const &);
 	std::mutex mutex;
 };
 class frontier_req_client : public std::enable_shared_from_this <rai::frontier_req_client>
```
