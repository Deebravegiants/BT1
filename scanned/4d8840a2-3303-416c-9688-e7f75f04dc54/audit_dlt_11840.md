# [?] fix race condition

## Summary
Severity: Unknown
Chain: Indexer
Component: ponder-sh/ponder
Published: 2025-08-21
Source: https://github.com/ponder-sh/ponder/commit/72f01e36eb231a9d745df1ce2640d8c27bf37ccd
Type: security-commit

## Details
fix race condition

## Patch
### packages/core/src/indexing-store/cache.ts
```diff
@@ -756,7 +756,9 @@ export const createIndexingCache = ({
       } else {
         isFlushRetry = true;
 
-        await Promise.all(
+        // Note: Must use `Promise.allSettled` to avoid short-circuiting while queries are running.
+
+        const results = await Promise.allSettled(
           Array.from(cache.keys()).map(async (table) => {
             const shouldRecordBytes = cache.get(table)!.isCacheComplete;
             if (
@@ -918,9 +920,15 @@ export const createIndexingCache = ({
               await new Promise(setImmediate);
             }
           }),
-        ).catch((error) => {
-          throw new RetryableError(error.message);
-        });
+        );
+
+        if (results.some((result) => result.status === "rejected")) {
+          const rejected = results.find(
+            (result): result is PromiseRejectedResult =>
+              result.status === "rejected",
+          )!;
+          throw new RetryableError(rejected.reason.message);
+        }
       }
 
       isFlushRetry = false;
```
