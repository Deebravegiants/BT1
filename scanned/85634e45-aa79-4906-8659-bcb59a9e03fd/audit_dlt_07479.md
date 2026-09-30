# [?] test: Fix use-after-free in scheduler tests

## Summary
Severity: Unknown
Chain: Dogecoin
Component: dogecoin/dogecoin
Published: 2016-11-18
Source: https://github.com/dogecoin/dogecoin/commit/12519bf62b8c49b1c1744eca6ea5b3162a61f962
Type: security-commit

## Details
test: Fix use-after-free in scheduler tests

Make a copy of the boost time-point to wait for, otherwise the head of
the queue may be deleted by another thread while this one is waiting,
while the boost function still has a reference to it.

Although this problem is in non-test code, this is not an actual problem
outside of the tests because we use the thread scheduler with only one
service thread, so there will never be threads fighting at the head of
the queue.

The old boost fallback escapes this problem because it passes a scalar
value to wait_until instead of a const object reference.

Found by running the tests in LLVM-4.0-master asan.

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
