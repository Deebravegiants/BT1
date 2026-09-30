# [?] fix unhandled promise rejection crashes

## Summary
Severity: Unknown
Chain: Indexer
Component: subsquid/squid-sdk
Published: 2023-06-19
Source: https://github.com/subsquid/squid-sdk/commit/3b918f3171067d5894a1aecbefc754f3f0de2866
Type: security-commit

## Details
fix unhandled promise rejection crashes

## Patch
### common/changes/@subsquid/evm-processor/master_2023-06-19-20-35.json
```diff
@@ -0,0 +1,10 @@
+{
+  "changes": [
+    {
+      "packageName": "@subsquid/evm-processor",
+      "comment": "fix unhandled promise rejection crashes",
+      "type": "patch"
+    }
+  ],
+  "packageName": "@subsquid/evm-processor"
+}
\ No newline at end of file
```

### common/changes/@subsquid/util-internal/master_2023-06-19-20-35.json
```diff
@@ -0,0 +1,10 @@
+{
+  "changes": [
+    {
+      "packageName": "@subsquid/util-internal",
+      "comment": "fix unhandled promise rejection crashes",
+      "type": "patch"
+    }
+  ],
+  "packageName": "@subsquid/util-internal"
+}
\ No newline at end of file
```

### evm/evm-processor/src/ds-rpc/client.ts
```diff
@@ -201,15 +201,21 @@ export class EvmRpcDataSource implements HotDataSource<Block, DataRequest> {
         let subtasks = []
 
         if (req.logs && !req.receipts) {
-            subtasks.push(this.fetchLogs(blocks))
+            subtasks.push(catching(
+                this.fetchLogs(blocks)
+            ))
         }
 
         if (req.receipts) {
             let byBlockMethod = await this.getBlockReceiptsMethod()
             if (byBlockMethod) {
-                subtasks.push(this.fetchReceiptsByBlock(blocks, byBlockMethod))
+                subtasks.push(catching(
+                    this.fetchReceiptsByBlock(blocks, byBlockMethod)
+                ))
             } else {
-                subtasks.push(this.fetchReceiptsByTx(blocks))
+                subtasks.push(catching(
+                    this.fetchReceiptsByTx(blocks)
+                ))
             }
         }
 
@@ -327,7 +333,9 @@ export class EvmRpcDataSource implements HotDataSource<Block, DataRequest> {
 
         if (req.stateDiffs) {
             if (finalizedHeight < getBlockHeight(last(blocks)) || this.useDebugApiForStateDiffs) {
-                tasks.push(this.fetchDebugStateDiffs(blocks))
+                tasks.push(catching(
+                    this.fetchDebugStateDiffs(blocks)
+                ))
             } else {
                 replayTracers.push('stateDiff')
             }
@@ -336,17 +344,23 @@ export class EvmRpcDataSource implements HotDataSource<Block, DataRequest> {
         if (req.traces) {
             if (this.preferTraceApi) {
                 if (finalizedHeight < getBlockHeight(last(blocks)) || replayTracers.length == 0) {
-                    tasks.push(this.fetchTraceBlock(blocks))
+                    tasks.push(catching(
+                        this.fetchTraceBlock(blocks)
+                    ))
                 } else {
                     replayTracers.push('trace')
                 }
             } else {
-                tasks.push(this.fetchDebugFrames(blocks))
+                tasks.push(catching(
+                    this.fetchDebugFrames(blocks)
+                ))
             }
         }
 
         if (replayTracers.length) {
-            tasks.push(this.fetchReplays(blocks, replayTracers))
+            tasks.push(catching(
+                this.fetchReplays(blocks, replayTracers)
+            ))
         }
 
         return Promise.all(tasks).then()
@@ -531,3 +545,10 @@ function isConsistencyError(err: unknown): err is Error {
     }
     return false
 }
+
+
+function catching<T>(promise: Promise<T>): Promise<T> {
+    // prevent unhandled promise rejection crashes
+    promise.catch(() => {})
+    return promise
+}
```

### util/util-internal/src/async.ts
```diff
@@ -1,4 +1,5 @@
 import assert from 'assert'
+import {assertNotNull} from './misc'
 
 
 export interface Future<T> {
@@ -9,15 +10,15 @@ export interface Future<T> {
 
 
 export function createFuture<T>(): Future<T> {
-    let future: Future<T>
+    let future: Future<T> | undefined
     let promise = new Promise<T>((resolve, reject) => {
         future = {
             resolve,
             reject,
             promise: () => promise
         }
     })
-    return future!
+    return assertNotNull(future)
 }
 
 
@@ -118,6 +119,7 @@ export async function* concurrentMap<T, R>(
     async function map() {
         for await (let val of stream) {
             let promise = f(val)
+            promise.catch(() => {}) // prevent unhandled rejection crashes
             await queue.put({promise})
         }
     }
```
