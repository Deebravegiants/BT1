# [?] fix: tx result race condition (#3093)

## Summary
Severity: Unknown
Chain: Rabby
Component: RabbyHub/Rabby
Published: 2025-08-07
Source: https://github.com/RabbyHub/Rabby/commit/ca8f8f899320f880e93cc620d70823acca80cbad
Type: security-commit

## Details
fix: tx result race condition (#3093)

## Patch
### src/background/service/rpc.ts
```diff
@@ -31,21 +31,21 @@ async function submitTxWithFallbackRpcs<T>(
   rpcUrls: string[],
   fn: (rpc: string) => Promise<T>
 ): Promise<[T, string]> {
-  const promises = rpcUrls.map((url) =>
-    fn(url)
-      .then((result) => [result, url] as [T, string])
-      .catch((err) => {
-        throw err;
-      })
-  );
-  try {
-    return await Promise.race(promises);
-  } catch (e) {
-    // If all fail, collect errors
-    const errors = await Promise.allSettled(promises);
-    const firstRejected = errors.find((r) => r.status === 'rejected');
-    throw firstRejected ? (firstRejected as PromiseRejectedResult).reason : e;
-  }
+  return new Promise((resolve, reject) => {
+    let errorCount = 0;
+    rpcUrls.forEach((url) => {
+      fn(url)
+        .then((result) => {
+          resolve([result, url]);
+        })
+        .catch((err) => {
+          errorCount++;
+          if (errorCount === rpcUrls.length) {
+            reject(err);
+          }
+        });
+    });
+  });
 }
 
 async function callWithFallbackRpcs<T>(
```
