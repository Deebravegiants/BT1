# [?] Fixes race condition in debounce (#685)

## Summary
Severity: Unknown
Chain: Indexer
Component: ponder-sh/ponder
Published: 2024-03-02
Source: https://github.com/ponder-sh/ponder/commit/27ba293e402304eb3de50177ecb46a430b8ced9d
Type: security-commit

## Details
Fixes race condition in debounce (#685)

* fix race condition in debounce

* chore: changeset

## Patch
### .changeset/many-worms-study.md
```diff
@@ -0,0 +1,5 @@
+---
+"@ponder/core": patch
+---
+
+Fixed race condition in sync event debounce logic.
```

### packages/core/src/utils/debounce.test.ts
```diff
@@ -1,83 +1,87 @@
-import { expect, test } from "vitest";
+import { expect, test, vi } from "vitest";
 import { debounce } from "./debounce.js";
 import { wait } from "./wait.js";
 
 test("invokes function right away", () => {
-  let i = 0;
-  const set = (_i: number) => {
-    i = _i;
-  };
-  const d = debounce(0, set);
+  const fun = vi.fn(() => {});
+  const d = debounce(0, fun);
 
-  d(1);
-  expect(i).toBe(1);
+  d();
+
+  expect(fun).toHaveBeenCalledTimes(1);
 });
 
-test("invokes function after interval passes", async () => {
-  let i = 0;
-  const set = (_i: number) => {
-    i = _i;
-  };
-  const d = debounce(0, set);
+test("invoke function after timeout", async () => {
+  const fun = vi.fn(() => {});
+  const d = debounce(10, fun);
 
-  d(1);
+  d();
+  d();
 
-  await wait(1);
+  expect(fun).toHaveBeenCalledTimes(1);
 
-  d(2);
-  expect(i).toBe(2);
-});
+  await wait(20);
 
-test("sets timeout to run after interval", async () => {
-  let i = 0;
-  const increment = (_i: number) => {
-    i = _i;
-  };
-  const d = debounce(1, increment);
+  expect(fun).toHaveBeenCalledTimes(2);
+});
 
-  d(1);
+test("skips invocation during timeout", async () => {
+  const fun = vi.fn(() => {});
+  const d = debounce(10, fun);
 
-  d(2);
+  d();
+  d();
+  d();
+  d();
+  d();
 
-  await wait(1);
+  await wait(20);
 
-  expect(i).toBe(2);
+  expect(fun).toHaveBeenCalledTimes(2);
 });
 
 test("updates arguments during timeout", async () => {
-  let i = 0;
-  const set = (_i: number) => {
-    i = _i;
-  };
-  const d = debounce(1, set);
+  const fun = vi.fn((n: number) => {
+    n;
+  });
+  const d = debounce(10, fun);
 
   d(1);
-
   d(2);
   d(3);
   d(4);
-  d(1);
+  d(5);
 
-  await wait(1);
+  await wait(20);
 
-  expect(i).toBe(1);
+  expect(fun).toHaveBeenCalledTimes(2);
+  expect(fun).toHaveBeenCalledWith(1);
+  expect(fun).toHaveBeenCalledWith(5);
 });
 
-test("invokes function once per interval", async () => {
-  let i = 0;
-  const increment = () => {
-    i++;
-  };
-  const d = debounce(1, increment);
+test("sets last timestamp after immediate invocation", async () => {
+  const fun = vi.fn(() => {});
+  const d = debounce(10, fun);
 
   d();
 
+  await wait(20);
+
   d();
+
+  expect(fun).toHaveBeenCalledTimes(2);
+});
+
+test("sets last timestamp after timeout", async () => {
+  const fun = vi.fn(() => {});
+  const d = debounce(10, fun);
+
   d();
   d();
-  d();
 
-  await wait(1);
+  await wait(25);
+
+  d();
 
-  expect(i).toBe(2);
+  expect(fun).toHaveBeenCalledTimes(3);
 });
```

### packages/core/src/utils/debounce.ts
```diff
@@ -10,28 +10,27 @@ export function debounce<param extends unknown[], returnType>(
   fun: (...x: param) => returnType,
 ) {
   let lastTimestamp = 0;
-  let args: param | undefined;
+  let args: param;
+  let timeoutSet = false;
 
   return (..._args: param) => {
-    if (Date.now() > lastTimestamp + ms) {
+    if (timeoutSet) {
+      args = _args;
+    } else if (Date.now() >= lastTimestamp + ms) {
       lastTimestamp = Date.now();
-
       fun(..._args);
-      args = undefined;
     } else {
-      if (args === undefined) {
-        // No timeout is set
-        setTimeout(
-          () => {
-            fun(...args!);
-            args = undefined;
-          },
-          lastTimestamp + ms - Date.now(),
-        );
-      }
-
       args = _args;
-      lastTimestamp = Date.now();
+      timeoutSet = true;
+
+      setTimeout(
+        () => {
+          lastTimestamp = Date.now();
+          fun(...args);
+          timeoutSet = false;
+        },
+        lastTimestamp + ms - Date.now(),
+      );
     }
   };
 }
```
