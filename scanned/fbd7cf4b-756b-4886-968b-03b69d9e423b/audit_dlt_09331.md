# [?] Fix reentrancy problem

## Summary
Severity: Unknown
Chain: Tooling
Component: NomicFoundation/hardhat
Published: 2026-04-28
Source: https://github.com/NomicFoundation/hardhat/commit/41c90f173d26fb96db7453bd66e3b119e262433a
Type: security-commit

## Details
Fix reentrancy problem

## Patch
### packages/hardhat-utils/src/synchronization.ts
```diff
@@ -667,17 +667,16 @@ type SharedPromiseCachedResult<ValueT> =
  * original thrown value, so their own `getOrCompute` call site won't
  * necessarily be present in the error stack.
  *
- * Notes on concurrency: For non-reentrant calls, `getOrCompute` stores the
- * in-flight promise in the cache before returning control to the event loop.
- * Subsequent calls with the same key observe that promise and await the same
- * computation instead of invoking their own function.
+ * Notes on concurrency: `getOrCompute` stores the in-flight promise in the
+ * cache before invoking the producer function. Subsequent calls with the same
+ * key, including synchronous same-key reentrant calls from the producer,
+ * observe that promise and await the same computation instead of invoking their
+ * own function. A producer must still not await a same-key reentrant call
+ * before completing, because it would wait on its own in-flight result.
  *
  * This guarantee only applies while the cache entry remains installed. Calling
  * `delete` or `clear` during an in-flight computation lets later callers start
  * a new computation, and the older in-flight result won't repopulate the cache.
- *
- * The producer function is invoked before the in-flight promise is stored, so it
- * should not synchronously call `getOrCompute` with the same key.
  */
 export class SharedPromiseCache<ValueT> {
   readonly #cache = new Map<string, SharedPromiseCachedResult<ValueT>>();
@@ -716,23 +715,28 @@ export class SharedPromiseCache<ValueT> {
       throw cachedResult.error;
     }
 
-    // Don't update `this.#cache` from inside this IIFE — doing so would let a
-    // resolution overwrite a concurrent `delete()`/`clear()`. The cache write
-    // is deferred to `#updateResolvedPromiseCache`, which gates on reference
-    // equality.
-    const promise: Promise<SharedPromiseExecutionResult<ValueT>> =
-      (async () => {
-        try {
-          const value = await fn();
-          return { success: true, value };
-        } catch (error) {
-          return { success: false, error };
-        }
-      })();
+    // Create and cache the in-flight promise before invoking `fn`, because
+    // `fn` can synchronously re-enter `getOrCompute` with the same key. The
+    // reentrant call must observe this promise instead of a cache miss, or it
+    // could start a second computation for the same key.
+    //
+    // `Promise.withResolvers` lets the first caller still await `fn` directly,
+    // preserving the producer async stack.
+    const { promise, resolve } =
+      Promise.withResolvers<SharedPromiseExecutionResult<ValueT>>();
 
     this.#cache.set(key, promise);
 
-    const result = await promise;
+    let result: SharedPromiseExecutionResult<ValueT>;
+
+    try {
+      const value = await fn();
+      result = { success: true, value };
+    } catch (error) {
+      result = { success: false, error };
+    }
+
+    resolve(result);
 
     this.#updateResolvedPromiseCache(key, promise, result);
 
```

### packages/hardhat-utils/test/synchronization.ts
```diff
@@ -1335,6 +1335,29 @@ describe("SharedPromiseCache", () => {
     assert.equal(calls, 1);
   });
 
+  it("should store the in-flight promise before invoking the producer", async () => {
+    const cache = new SharedPromiseCache<string>();
+    let outerCalls = 0;
+    let reentrantCalls = 0;
+    let reentrantResult: Promise<string> | undefined;
+
+    const result = await cache.getOrCompute("key", async () => {
+      outerCalls++;
+      reentrantResult = cache.getOrCompute("key", async () => {
+        reentrantCalls++;
+        return "reentrant";
+      });
+
+      return "outer";
+    });
+
+    assert.equal(result, "outer");
+    assert.ok(reentrantResult !== undefined, "Expected a reentrant result");
+    assert.equal(await reentrantResult, "outer");
+    assert.equal(outerCalls, 1);
+    assert.equal(reentrantCalls, 0);
+  });
+
   it("should ignore later functions for concurrent calls with the same key, only using the first one", async () => {
     const cache = new SharedPromiseCache<string>();
     const deferred = Promise.withResolvers<string>();
```
