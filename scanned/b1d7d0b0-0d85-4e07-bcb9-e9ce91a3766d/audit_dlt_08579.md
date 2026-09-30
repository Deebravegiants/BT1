# [?] fix crash on shutdown (as to get the proper error message)

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2020-08-04
Source: https://github.com/stellar/stellar-core/commit/7c74acf1c8b38df4e5ec55fc44142becdfeba6ff
Type: security-commit

## Details
fix crash on shutdown (as to get the proper error message)

## Patch
### src/main/ApplicationImpl.cpp
```diff
@@ -348,14 +348,21 @@ ApplicationImpl::getNetworkID() const
 ApplicationImpl::~ApplicationImpl()
 {
     LOG(INFO) << "Application destructing";
-    shutdownWorkScheduler();
-    if (mProcessManager)
+    try
     {
-        mProcessManager->shutdown();
+        shutdownWorkScheduler();
+        if (mProcessManager)
+        {
+            mProcessManager->shutdown();
+        }
+        if (mBucketManager)
+        {
+            mBucketManager->shutdown();
+        }
     }
-    if (mBucketManager)
+    catch (std::exception const& e)
     {
-        mBucketManager->shutdown();
+        LOG(ERROR) << "While shutting down " << e.what();
     }
     reportCfgMetrics();
     shutdownMainIOContext();
```
