# [?] Fix data race condition found by tsan. (reverted from commit 4c44fbec8c665338929528bdd8fb81eeee4d9e8c) (reverted from commit 1c38267ec932ca8ccc07b49ae

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2017-08-23
Source: https://github.com/nanocurrency/nano-node/commit/cb1ef3a35df53340315563e1d58c9ab674d937ea
Type: security-commit

## Details
Fix data race condition found by tsan. (reverted from commit 4c44fbec8c665338929528bdd8fb81eeee4d9e8c) (reverted from commit 1c38267ec932ca8ccc07b49aef361ab8eac0347a)

## Patch
### rai/node/bootstrap.cpp
```diff
@@ -758,7 +758,6 @@ stopped (false)
 
 rai::bootstrap_attempt::~bootstrap_attempt ()
 {
-	node->bootstrap_initiator.notify_listeners ();
 	BOOST_LOG (node->log) << "Exiting bootstrap attempt";
 }
 
@@ -1007,18 +1006,21 @@ rai::bootstrap_initiator::~bootstrap_initiator ()
 
 void rai::bootstrap_initiator::bootstrap ()
 {
-	std::lock_guard <std::mutex> lock (mutex);
-	if (attempt == nullptr && !stopped)
+	std::unique_lock <std::mutex> lock (mutex);
+	if (!stopped && attempt == nullptr)
 	{
-        stop_attempt ();
+        stop_attempt (lock);
         attempt = std::make_shared <rai::bootstrap_attempt> (node.shared ());
 		attempt_thread.reset (new std::thread ([this] ()
         {
             attempt->run ();
 			node.block_processor.flush ();
-            attempt.reset ();
+			std::lock_guard <std::mutex> lock (mutex);
+			attempt.reset ();
+			condition.notify_all ();
         }));
 	}
+	notify_listeners (attempt != nullptr);
 }
 
 void rai::bootstrap_initiator::bootstrap (rai::endpoint const & endpoint_a)
@@ -1046,30 +1048,35 @@ bool rai::bootstrap_initiator::in_progress ()
 
 void rai::bootstrap_initiator::stop ()
 {
-    std::lock_guard <std::mutex> lock (mutex);
+	std::unique_lock <std::mutex> lock (mutex);
 	stopped = true;
-	stop_attempt ();
+	stop_attempt (lock);
 }
 
-void rai::bootstrap_initiator::stop_attempt ()
+void rai::bootstrap_initiator::stop_attempt (std::unique_lock <std::mutex> & lock_a)
 {
+	assert (!mutex.try_lock ());
 	if (attempt != nullptr)
 	{
 		attempt->stop ();
 	}
+	while (attempt != nullptr)
+	{
+		condition.wait (lock_a);
+	}
 	if (attempt_thread)
 	{
 		attempt_thread->join ();
 		attempt_thread.reset ();
 	}
+	notify_listeners (false);
 }
 
-void rai::bootstrap_initiator::notify_listeners ()
+void rai::bootstrap_initiator::notify_listeners (bool in_progress_a)
 {
-	auto in_progress_l (in_progress ());
 	for (auto & i: observers)
 	{
-		i (in_progress_l);
+		i (in_progress_a);
 	}
 }
 
```

### rai/node/bootstrap.hpp
```diff
@@ -158,17 +158,18 @@ class bootstrap_initiator
 	~bootstrap_initiator ();
     void bootstrap (rai::endpoint const &);
     void bootstrap ();
-	void notify_listeners ();
+	void notify_listeners (bool);
 	void add_observer (std::function <void (bool)> const &);
 	bool in_progress ();
 	void stop ();
-    void stop_attempt ();
+    void stop_attempt (std::unique_lock <std::mutex> &);
 	rai::node & node;
 	std::shared_ptr <rai::bootstrap_attempt> attempt;
 	std::unique_ptr <std::thread> attempt_thread;
 	bool stopped;
 private:
 	std::mutex mutex;
+	std::condition_variable condition;
 	std::vector <std::function <void (bool)>> observers;
 };
 class bootstrap_listener
```
