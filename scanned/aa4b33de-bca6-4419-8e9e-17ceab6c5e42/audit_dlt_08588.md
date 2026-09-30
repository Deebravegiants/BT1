# [?] Fix a race condition during shutdown

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2022-07-16
Source: https://github.com/XRPLF/rippled/commit/22b4de2e4445fa56e892ec40db9aa834c1f7511a
Type: security-commit

## Details
Fix a race condition during shutdown

## Patch
### src/ripple/nodestore/impl/Database.cpp
```diff
@@ -68,11 +68,14 @@ Database::Database(
 
                 decltype(read_) read;
 
-                while (!isStopping())
+                while (true)
                 {
                     {
                         std::unique_lock<std::mutex> lock(readLock_);
 
+                        if (isStopping())
+                            break;
+
                         if (read_.empty())
                         {
                             runningThreads_--;
@@ -81,10 +84,10 @@ Database::Database(
                         }
 
                         if (isStopping())
-                            continue;
+                            break;
 
-                        // If configured, extract multiple object at a time to
-                        // minimize the overhead of acquiring the mutex.
+                        // extract multiple object at a time to minimize the
+                        // overhead of acquiring the mutex.
                         for (int cnt = 0;
                              !read_.empty() && cnt != requestBundle_;
                              ++cnt)
@@ -120,6 +123,7 @@ Database::Database(
                     read.clear();
                 }
 
+                --runningThreads_;
                 --readThreads_;
             },
             i);
@@ -160,15 +164,34 @@ Database::maxLedgers(std::uint32_t shardIndex) const noexcept
 void
 Database::stop()
 {
-    if (!readStopping_.exchange(true, std::memory_order_relaxed))
     {
         std::lock_guard lock(readLock_);
-        read_.clear();
-        readCondVar_.notify_all();
+
+        if (!readStopping_.exchange(true, std::memory_order_relaxed))
+        {
+            JLOG(j_.debug()) << "Clearing read queue because of stop request";
+            read_.clear();
+            readCondVar_.notify_all();
+        }
     }
 
+    JLOG(j_.debug()) << "Waiting for stop request to complete...";
+
+    using namespace std::chrono;
+
+    auto const start = steady_clock::now();
+
     while (readThreads_.load() != 0)
+    {
+        assert(steady_clock::now() - start < 30s);
         std::this_thread::yield();
+    }
+
+    JLOG(j_.debug()) << "Stop request completed in "
+                     << duration_cast<std::chrono::milliseconds>(
+                            steady_clock::now() - start)
+                            .count()
+                     << " millseconds";
 }
 
 void
@@ -177,10 +200,13 @@ Database::asyncFetch(
     std::uint32_t ledgerSeq,
     std::function<void(std::shared_ptr<NodeObject> const&)>&& cb)
 {
-    // Post a read
     std::lock_guard lock(readLock_);
-    read_[hash].emplace_back(ledgerSeq, std::move(cb));
-    readCondVar_.notify_one();
+
+    if (!isStopping())
+    {
+        read_[hash].emplace_back(ledgerSeq, std::move(cb));
+        readCondVar_.notify_one();
+    }
 }
 
 void
```
