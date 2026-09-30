# [?] fix: use atomic in `BLS_Verify_BatchedParallel` to avoid data race

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2025-07-15
Source: https://github.com/dashpay/dash/commit/2ad60b351e0ecdff7f741a9f8771f28d5c823a8f
Type: security-commit

## Details
fix: use atomic in `BLS_Verify_BatchedParallel` to avoid data race

## Patch
### src/bench/bls.cpp
```diff
@@ -7,6 +7,7 @@
 #include <random.h>
 #include <util/time.h>
 
+#include <atomic>
 #include <iostream>
 
 static void BuildTestVectors(size_t count, size_t invalidCount,
@@ -314,9 +315,9 @@ static void BLS_Verify_BatchedParallel(benchmark::Bench& bench)
 
     std::list<std::pair<size_t, std::future<bool>>> futures;
 
-    volatile bool cancel = false;
-    auto cancelCond = [&]() {
-        return cancel;
+    std::atomic<bool> cancel{false};
+    auto cancelCond = [&]() -> bool {
+        return cancel.load();
     };
 
     CBLSWorker blsWorker;
@@ -348,7 +349,7 @@ static void BLS_Verify_BatchedParallel(benchmark::Bench& bench)
         }
     });
 
-    cancel = true;
+    cancel.store(true);
     while (blsWorker.IsAsyncVerifyInProgress())
     {
         UninterruptibleSleep(std::chrono::milliseconds{100});
```
