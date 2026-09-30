# [?] Fix deadlock when shutting down node. Both bootstrap_listener::stop and bootstrap_server::~bootstrap_server try to lock boostrap_listener::mutex.

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2018-04-04
Source: https://github.com/nanocurrency/nano-node/commit/72a14f74b748ad1a90e51f078792e9cd448667be
Type: security-commit

## Details
Fix deadlock when shutting down node. Both bootstrap_listener::stop and bootstrap_server::~bootstrap_server try to lock boostrap_listener::mutex.

## Patch
### rai/node/bootstrap.cpp
```diff
@@ -1417,8 +1417,12 @@ void rai::bootstrap_listener::start ()
 
 void rai::bootstrap_listener::stop ()
 {
-	on = false;
-	std::lock_guard<std::mutex> lock (mutex);
+	decltype(connections) connections_l;
+	{
+		std::lock_guard<std::mutex> lock (mutex);
+		on = false;
+		connections_l.swap (connections);
+	}
 	acceptor.close ();
 	for (auto & i : connections)
 	{
```
