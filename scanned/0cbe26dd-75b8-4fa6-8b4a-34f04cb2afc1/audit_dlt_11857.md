# [?] initialize stats object in logqueue to avoid silent crash

## Summary
Severity: Unknown
Chain: Indexer
Component: ponder-sh/ponder
Published: 2022-10-22
Source: https://github.com/ponder-sh/ponder/commit/7791c851293f3855e5eeb6d1b75165d10797e46d
Type: security-commit

## Details
initialize stats object in logqueue to avoid silent crash

## Patch
### packages/ponder/src/core/indexer/logQueue.ts
```diff
@@ -66,7 +66,12 @@ export const createLogQueue = ({
       );
       return;
     }
-
+    if (!stats.sourceStats[source.name]) {
+      stats.sourceStats[source.name] = {
+        matchedLogCount: 0,
+        handledLogCount: 0,
+      };
+    }
     stats.sourceStats[source.name].matchedLogCount += 1;
 
     const sourceHandlers = userHandlers[source.name];
```
