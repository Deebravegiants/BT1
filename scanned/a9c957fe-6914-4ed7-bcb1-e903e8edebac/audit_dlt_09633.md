# [?] fix: potential race condition in ProcessNewChainLock

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2025-10-26
Source: https://github.com/dashpay/dash/commit/696b926504be4ce6ccc5031c605d6d79e37356aa
Type: security-commit

## Details
fix: potential race condition in ProcessNewChainLock

## Patch
### src/chainlock/chainlock.cpp
```diff
@@ -135,7 +135,7 @@ MessageProcessingResult CChainLocksHandler::ProcessNewChainLock(const NodeId fro
         }
 
         if (!bestChainLock.IsNull() && clsig.getHeight() <= bestChainLock.getHeight()) {
-            // no need to process/relay older CLSIGs
+            // no need to process older/same CLSIGs
             return {};
         }
     }
@@ -154,6 +154,11 @@ MessageProcessingResult CChainLocksHandler::ProcessNewChainLock(const NodeId fro
 
     {
         LOCK(cs);
+        // newer chainlock could be processed via another thread while we were not holding the lock, re-verify
+        if (!bestChainLock.IsNull() && clsig.getHeight() <= bestChainLock.getHeight()) {
+            // no need to process older/same CLSIGs
+            return {};
+        }
         bestChainLockHash = hash;
         bestChainLock = clsig;
 
```
