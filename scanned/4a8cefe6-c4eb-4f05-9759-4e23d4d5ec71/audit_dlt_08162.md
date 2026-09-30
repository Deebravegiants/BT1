# [?] Resolve a race condition on `chainActive.Tip()` in initialization (introduced in #4379).

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2020-03-08
Source: https://github.com/zcash/zcash/commit/74467f8f0273fddb828da0b4559706487fe0b837
Type: security-commit

## Details
Resolve a race condition on `chainActive.Tip()` in initialization (introduced in #4379).

Signed-off-by: Daira Hopwood <daira@jacaranda.org>

## Patch
### src/init.cpp
```diff
@@ -1563,10 +1563,17 @@ bool AppInit2(boost::thread_group& threadGroup, CScheduler& scheduler)
     // original value of chainActive.Tip(), which corresponds with the wallet's
     // view of the chaintip, is passed to ThreadNotifyWallets before the chain
     // tip changes again.
-    boost::function<void()> threadnotifywallets = boost::bind(&ThreadNotifyWallets, chainActive.Tip());
-    threadGroup.create_thread(
-        boost::bind(&TraceThread<boost::function<void()>>, "txnotify", threadnotifywallets)
-    );
+    {
+        CBlockIndex *pindexLastTip;
+        {
+            LOCK(cs_main);
+            pindexLastTip = chainActive.Tip();
+        }
+        boost::function<void()> threadnotifywallets = boost::bind(&ThreadNotifyWallets, pindexLastTip);
+        threadGroup.create_thread(
+            boost::bind(&TraceThread<boost::function<void()>>, "txnotify", threadnotifywallets)
+        );
+    }
 
     // ********************************************************* Step 9: data directory maintenance
 
```
