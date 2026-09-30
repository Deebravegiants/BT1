# [?] fix: unrecoverable reorg crash

## Summary
Severity: Unknown
Chain: Indexer
Component: ponder-sh/ponder
Published: 2025-03-04
Source: https://github.com/ponder-sh/ponder/commit/e601d84bd44c708be9de017fdb393fbf037cebf0
Type: security-commit

## Details
fix: unrecoverable reorg crash

## Patch
### .changeset/cyan-donkeys-impress.md
```diff
@@ -0,0 +1,5 @@
+---
+"ponder": patch
+---
+
+Fixed crash behavior when an unrecoverable reorg occurs.
```

### packages/core/src/sync-realtime/index.test.ts
```diff
@@ -975,13 +975,15 @@ test("handleReorg() throws error for deep reorg", async (context) => {
     blockNumber: 0,
   });
 
+  const spy = vi.fn();
+
   const realtimeSync = createRealtimeSync({
     common,
     network,
     requestQueue,
     sources,
     onEvent: vi.fn(),
-    onFatalError: vi.fn(),
+    onFatalError: spy,
   });
 
   await testClient.mine({ blocks: 3 });
@@ -1007,4 +1009,5 @@ test("handleReorg() throws error for deep reorg", async (context) => {
   });
 
   expect(realtimeSync.unfinalizedBlocks).toHaveLength(0);
+  expect(spy).toHaveBeenCalledWith(expect.any(Error));
 });
```

### packages/core/src/sync-realtime/index.ts
```diff
@@ -116,7 +116,6 @@ export const createRealtimeSync = (
    * `parentHash` => `hash`.
    */
   let unfinalizedBlocks: LightBlock[] = [];
-  // let queue: Queue<void, BlockWithEventData & { endClock?: () => number }>;
   let consecutiveErrors = 0;
   let interval: NodeJS.Timeout | undefined;
 
@@ -529,9 +528,10 @@ export const createRealtimeSync = (
 
         const msg = `Encountered unrecoverable '${args.network.name}' reorg beyond finalized block ${hexToNumber(finalizedBlock.number)}`;
 
-        args.common.logger.warn({ service: "realtime", msg });
-
-        throw new Error(msg);
+        const error = new Error(msg);
+        args.common.logger.error({ service: "realtime", msg });
+        args.onFatalError(error);
+        return;
       } else {
         remoteBlock = await _eth_getBlockByHash(args.requestQueue, {
           hash: remoteBlock.parentHash,
```
