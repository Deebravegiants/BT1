# [?] Merge #9186: test: Fix use-after-free in scheduler tests

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2016-11-19
Source: https://github.com/dogecoin/dogecoin/commit/ce612f17506345527382ec70d6dc398ebe94dbb1
Type: security-commit

## Details
Merge #9186: test: Fix use-after-free in scheduler tests

12519bf test: Fix use-after-free in scheduler tests (Wladimir J. van der Laan)

## Patch
### src/scheduler.cpp
```diff
@@ -54,9 +54,10 @@ void CScheduler::serviceQueue()
 #else
             // Some boost versions have a conflicting overload of wait_until that returns void.
             // Explicitly use a template here to avoid hitting that overload.
-            while (!shouldStop() && !taskQueue.empty() &&
-                   newTaskScheduled.wait_until<>(lock, taskQueue.begin()->first) != boost::cv_status::timeout) {
-                // Keep waiting until timeout
+            while (!shouldStop() && !taskQueue.empty()) {
+                boost::chrono::system_clock::time_point timeToWaitFor = taskQueue.begin()->first;
+                if (newTaskScheduled.wait_until<>(lock, timeToWaitFor) == boost::cv_status::timeout)
+                    break; // Exit loop after timeout, it means we reached the time of the event
             }
 #endif
             // If there are multiple threads, the queue can empty while we're waiting (another
```
