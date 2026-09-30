# [?] Log when bootstrap starts and don't clear sessions when shutting down to avoid a deadlock.

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2017-06-21
Source: https://github.com/nanocurrency/nano-node/commit/7fb29911ae6045261fc619bdf79f66e15280ad00
Type: security-commit

## Details
Log when bootstrap starts and don't clear sessions when shutting down to avoid a deadlock.

## Patch
### rai/node/bootstrap.cpp
```diff
@@ -683,6 +683,7 @@ rai::bootstrap_attempt::bootstrap_attempt (std::shared_ptr <rai::node> node_a) :
 node (node_a),
 state (rai::attempt_state::starting)
 {
+	BOOST_LOG (node->log) << "Starting bootstrap attempt";
 }
 
 rai::bootstrap_attempt::~bootstrap_attempt ()
@@ -785,14 +786,21 @@ void rai::bootstrap_attempt::pool_connection (std::shared_ptr <rai::bootstrap_cl
 
 void rai::bootstrap_attempt::connection_ending (rai::bootstrap_client * client_a)
 {
-	std::lock_guard <std::mutex> lock (mutex);
-	if (!client_a->pull_client.pull.account.is_zero ())
+	if (client_a->node->network.on)
+	{
+		std::lock_guard <std::mutex> lock (mutex);
+		if (!client_a->pull_client.pull.account.is_zero ())
+		{
+			// If this connection is ending and request_account hasn't been cleared it didn't finish, requeue
+			requeue_pull (client_a->pull_client.pull);
+		}
+		auto erased_connecting (connecting.erase (client_a));
+		auto erased_active (active.erase (client_a));
+	}
+	else
 	{
-		// If this connection is ending and request_account hasn't been cleared it didn't finish, requeue
-		requeue_pull (client_a->pull_client.pull);
+		// If we're stopping, just exit
 	}
-	auto erased_connecting (connecting.erase (client_a));
-	auto erased_active (active.erase (client_a));
 }
 
 void rai::bootstrap_attempt::completed_requests (std::shared_ptr <rai::bootstrap_client> client_a)
```
