# [?] Fix deadlock in tests (Cont) (#2050)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2019-06-01
Source: https://github.com/nanocurrency/nano-node/commit/44c23e043323831a1ac4d394f49829186f4aa9e8
Type: security-commit

## Details
Fix deadlock in tests (Cont) (#2050)

## Patch
### nano/node/bootstrap.cpp
```diff
@@ -1646,7 +1646,6 @@ thread ([this]() {
 nano::bootstrap_initiator::~bootstrap_initiator ()
 {
 	stop ();
-	thread.join ();
 }
 
 void nano::bootstrap_initiator::bootstrap ()
@@ -1769,15 +1768,22 @@ std::shared_ptr<nano::bootstrap_attempt> nano::bootstrap_initiator::current_atte
 
 void nano::bootstrap_initiator::stop ()
 {
+	if (!stopped.exchange (true))
 	{
-		std::unique_lock<std::mutex> lock (mutex);
-		stopped = true;
-		if (attempt != nullptr)
 		{
-			attempt->stop ();
+			std::lock_guard<std::mutex> guard (mutex);
+			if (attempt != nullptr)
+			{
+				attempt->stop ();
+			}
+		}
+		condition.notify_all ();
+
+		if (thread.joinable ())
+		{
+			thread.join ();
 		}
 	}
-	condition.notify_all ();
 }
 
 void nano::bootstrap_initiator::notify_listeners (bool in_progress_a)
```

### nano/node/bootstrap.hpp
```diff
@@ -251,7 +251,7 @@ class bootstrap_initiator final
 private:
 	nano::node & node;
 	std::shared_ptr<nano::bootstrap_attempt> attempt;
-	bool stopped;
+	std::atomic<bool> stopped;
 	std::mutex mutex;
 	std::condition_variable condition;
 	std::mutex observers_mutex;
```
