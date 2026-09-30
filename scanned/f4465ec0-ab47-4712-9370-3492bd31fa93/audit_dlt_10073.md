# [?] Fix data race identified by TSAN where threads terminate after local variables are destroyed. (#4222)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2023-05-03
Source: https://github.com/nanocurrency/nano-node/commit/dafdb0237f0569349d1a68870af8979a308416e0
Type: security-commit

## Details
Fix data race identified by TSAN where threads terminate after local variables are destroyed. (#4222)

This issue is with the test code rather than the thread_pool itself.

## Patch
### nano/core_test/utility.cpp
```diff
@@ -172,10 +172,10 @@ TEST (thread, thread_pool)
 
 TEST (thread_pool_alarm, one)
 {
-	nano::thread_pool workers (1u, nano::thread_role::name::unknown);
 	std::atomic<bool> done (false);
 	nano::mutex mutex;
 	nano::condition_variable condition;
+	nano::thread_pool workers (1u, nano::thread_role::name::unknown);
 	workers.add_timed_task (std::chrono::steady_clock::now (), [&] () {
 		{
 			nano::lock_guard<nano::mutex> lock{ mutex };
@@ -189,10 +189,10 @@ TEST (thread_pool_alarm, one)
 
 TEST (thread_pool_alarm, many)
 {
-	nano::thread_pool workers (50u, nano::thread_role::name::unknown);
 	std::atomic<int> count (0);
 	nano::mutex mutex;
 	nano::condition_variable condition;
+	nano::thread_pool workers (50u, nano::thread_role::name::unknown);
 	for (auto i (0); i < 50; ++i)
 	{
 		workers.add_timed_task (std::chrono::steady_clock::now (), [&] () {
@@ -209,11 +209,11 @@ TEST (thread_pool_alarm, many)
 
 TEST (thread_pool_alarm, top_execution)
 {
-	nano::thread_pool workers (1u, nano::thread_role::name::unknown);
 	int value1 (0);
 	int value2 (0);
 	nano::mutex mutex;
 	std::promise<bool> promise;
+	nano::thread_pool workers (1u, nano::thread_role::name::unknown);
 	workers.add_timed_task (std::chrono::steady_clock::now (), [&] () {
 		nano::lock_guard<nano::mutex> lock{ mutex };
 		value1 = 1;
```
