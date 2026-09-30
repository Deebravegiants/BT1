# [?] Fix deadlock issue

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2019-09-06
Source: https://github.com/Zilliqa/zq1/commit/bbabc36ac1d10db264539ec133200315fe4205ec
Type: security-commit

## Details
Fix deadlock issue

## Patch
### src/libDirectoryService/ViewChangePostProcessing.cpp
```diff
@@ -395,29 +395,25 @@ bool DirectoryService::ProcessViewChangeConsensus(const bytes& message,
   // If COLLECTIVESIG also comes in, it's then possible COLLECTIVESIG will be
   // processed before ANNOUNCE! So, ANNOUNCE should acquire a lock here
 
-  {
-    lock_guard<mutex> g(m_mutexConsensus);
-
-    if (!CheckState(PROCESS_VIEWCHANGECONSENSUS)) {
-      std::unique_lock<std::mutex> cv_lk(m_MutexCVViewChangeConsensusObj);
-      if (cv_ViewChangeConsensusObj.wait_for(
-              cv_lk, std::chrono::seconds(CONSENSUS_OBJECT_TIMEOUT),
-              [this] { return CheckState(PROCESS_VIEWCHANGECONSENSUS); })) {
-        LOG_EPOCH(INFO, m_mediator.m_currentEpochNum,
-                  "Successfully transit to viewchange consensus or I "
-                  "am in the "
-                  "correct state.");
-      } else {
-        LOG_EPOCH(WARNING, m_mediator.m_currentEpochNum,
-                  "Time out while waiting for state transition to view "
-                  "change "
-                  "consensus and "
-                  "consensus object creation. Most likely view change "
-                  "didn't "
-                  "occur. A malicious node may be trying to initate view "
-                  "change.");
-        return false;
-      }
+  if (!CheckState(PROCESS_VIEWCHANGECONSENSUS)) {
+    std::unique_lock<std::mutex> cv_lk(m_MutexCVViewChangeConsensusObj);
+    if (cv_ViewChangeConsensusObj.wait_for(
+            cv_lk, std::chrono::seconds(CONSENSUS_OBJECT_TIMEOUT),
+            [this] { return CheckState(PROCESS_VIEWCHANGECONSENSUS); })) {
+      LOG_EPOCH(INFO, m_mediator.m_currentEpochNum,
+                "Successfully transit to viewchange consensus or I "
+                "am in the "
+                "correct state.");
+    } else {
+      LOG_EPOCH(WARNING, m_mediator.m_currentEpochNum,
+                "Time out while waiting for state transition to view "
+                "change "
+                "consensus and "
+                "consensus object creation. Most likely view change "
+                "didn't "
+                "occur. A malicious node may be trying to initate view "
+                "change.");
+      return false;
     }
   }
 
```
