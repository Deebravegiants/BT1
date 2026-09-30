# [?] Fixing shutdown deadlock.

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2017-03-11
Source: https://github.com/nanocurrency/nano-node/commit/d12b7e02f4814bba7e6139b588727f0d8c7a6e78
Type: security-commit

## Details
Fixing shutdown deadlock.

## Patch
### rai/node/bootstrap.cpp
```diff
@@ -730,7 +730,8 @@ rai::bootstrap_attempt::bootstrap_attempt (std::shared_ptr <rai::node> node_a) :
 node (node_a),
 connected (false),
 requested (false),
-completed (false)
+completed (false),
+stopped (false)
 {
 }
 
@@ -742,7 +743,7 @@ rai::bootstrap_attempt::~bootstrap_attempt ()
 
 void rai::bootstrap_attempt::attempt (rai::endpoint const & endpoint_a)
 {
-	assert (!node->bootstrap_initiator.mutex.try_lock ());
+	std::lock_guard <std::mutex> lock (mutex);
 	if (!connected)
 	{
 		BOOST_LOG (node->log) << boost::str (boost::format ("Initiating bootstrap to: %1%") % endpoint_a);
@@ -753,7 +754,6 @@ void rai::bootstrap_attempt::attempt (rai::endpoint const & endpoint_a)
 		processor->run (rai::tcp_endpoint (endpoint_a.address (), endpoint_a.port ()));
 		node->alarm.add (std::chrono::system_clock::now () + std::chrono::milliseconds (250), [this_l] ()
 		{
-			std::lock_guard <std::mutex> lock (this_l->node->bootstrap_initiator.mutex);
 			this_l->attempt ();
 		});
 	}
@@ -766,7 +766,8 @@ void rai::bootstrap_attempt::attempt ()
 
 void rai::bootstrap_attempt::stop ()
 {
-	assert (!node->bootstrap_initiator.mutex.try_lock ());
+	stopped = true;
+	std::lock_guard <std::mutex> lock (mutex);
 	for (auto i: connecting)
 	{
 		auto attempt (i.second.lock ());
@@ -789,7 +790,7 @@ void rai::bootstrap_attempt::stop ()
 void rai::bootstrap_attempt::pool_connection (std::shared_ptr <rai::bootstrap_client> client_a)
 {
 	{
-		std::lock_guard <std::mutex> lock (node->bootstrap_initiator.mutex);
+		std::lock_guard <std::mutex> lock (mutex);
 		auto erased_active (active.erase (client_a.get ()));
 		auto erased_connecting (connecting.erase (client_a.get ()));
 		assert (erased_active == 1 || erased_connecting == 1);
@@ -803,20 +804,23 @@ void rai::bootstrap_attempt::pool_connection (std::shared_ptr <rai::bootstrap_cl
 
 void rai::bootstrap_attempt::connection_ending (rai::bootstrap_client * client_a)
 {
-	std::lock_guard <std::mutex> lock (node->bootstrap_initiator.mutex);
-	if (!client_a->pull_client.request_account.is_zero ())
+	if (!stopped)
 	{
-		// If this connection is ending and request_account hasn't been cleared it didn't finish, requeue
-		pulls.push_back (std::make_pair (client_a->pull_client.request_account, client_a->pull_client.request_hash));
+		std::lock_guard <std::mutex> lock (mutex);
+		if (!client_a->pull_client.request_account.is_zero ())
+		{
+			// If this connection is ending and request_account hasn't been cleared it didn't finish, requeue
+			pulls.push_back (std::make_pair (client_a->pull_client.request_account, client_a->pull_client.request_hash));
+		}
+		auto erased_connecting (connecting.erase (client_a));
+		auto erased_active (active.erase (client_a));
 	}
-	auto erased_connecting (connecting.erase (client_a));
-	auto erased_active (active.erase (client_a));
 }
 
 void rai::bootstrap_attempt::completed_requests (std::shared_ptr <rai::bootstrap_client> client_a)
 {
 	{
-		std::lock_guard <std::mutex> lock (node->bootstrap_initiator.mutex);
+		std::lock_guard <std::mutex> lock (mutex);
 		if (node->config.logging.network_logging ())
 		{
 			BOOST_LOG (node->log) << boost::str (boost::format ("Completed frontier request, %1% out of sync accounts") % pulls.size ());
@@ -842,7 +846,7 @@ void rai::bootstrap_attempt::completed_pulls (std::shared_ptr <rai::bootstrap_cl
 void rai::bootstrap_attempt::completed_pushes (std::shared_ptr <rai::bootstrap_client> client_a)
 {
 	std::vector <std::shared_ptr <rai::bootstrap_client>> discard;
-	std::lock_guard <std::mutex> lock (node->bootstrap_initiator.mutex);
+	std::lock_guard <std::mutex> lock (mutex);
 	completed = true;
 	discard.swap (idle);
 }
@@ -851,7 +855,7 @@ void rai::bootstrap_attempt::dispatch_work ()
 {
 	std::function <void ()> action;
 	{
-		std::lock_guard <std::mutex> lock (node->bootstrap_initiator.mutex);
+		std::lock_guard <std::mutex> lock (mutex);
 		if (!idle.empty ())
 		{
 			assert (!completed);
```

### rai/node/bootstrap.hpp
```diff
@@ -81,6 +81,9 @@ class bootstrap_attempt : public std::enable_shared_from_this <bootstrap_attempt
 	bool connected;
 	bool requested;
 	bool completed;
+	bool stopped;
+private:
+	std::mutex mutex;
 };
 class frontier_req_client : public std::enable_shared_from_this <rai::frontier_req_client>
 {
@@ -153,12 +156,12 @@ class bootstrap_initiator
 	void add_observer (std::function <void (bool)> const &);
 	bool in_progress ();
 	void stop ();
-	std::mutex mutex;
 	rai::node & node;
 	std::weak_ptr <rai::bootstrap_attempt> attempt;
 	unsigned warmed_up;
 	bool stopped;
 private:
+	std::mutex mutex;
 	std::vector <std::function <void (bool)>> observers;
 };
 class bootstrap_listener
```
