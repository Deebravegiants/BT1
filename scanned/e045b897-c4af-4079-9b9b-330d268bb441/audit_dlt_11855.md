# [?] Fix realtime error crashing service (#324)

## Summary
Severity: Unknown
Chain: Indexer
Component: ponder-sh/ponder
Published: 2023-08-18
Source: https://github.com/ponder-sh/ponder/commit/ab3d68463fbc6bbc581b2e0fd583f9b71bdb9506
Type: security-commit

## Details
Fix realtime error crashing service (#324)

* add error handling for realtime http errors

* remove lint error

* chore: changeset

## Patch
### .changeset/tender-pandas-eat.md
```diff
@@ -0,0 +1,5 @@
+---
+"@ponder/core": patch
+---
+
+Fixed a bug where the realtime sync service would crash on bad requests. Now, a warning will be logged and the service will wait until the next poll.
```

### examples/token-erc20/src/index.ts
```diff
@@ -72,17 +72,6 @@ ponder.on("AdventureGold:Approval", async ({ event, context }) => {
 ponder.on("AdventureGold:OwnershipTransferred", async ({ event, context }) => {
   const { Account } = context.entities;
 
-  const accounts = await Account.findMany({
-    where: {
-      id: {
-        ends_with: "123",
-      },
-      balance: {
-        equals: 123n,
-      },
-    },
-  });
-
   await Account.upsert({
     id: event.params.previousOwner,
     create: {
```

### packages/core/src/realtime-sync/service.test.ts
```diff
@@ -1,4 +1,5 @@
 /* eslint-disable @typescript-eslint/no-unused-vars */
+import { type EIP1193RequestFn, HttpRequestError } from "viem";
 import { beforeEach, expect, test, vi } from "vitest";
 
 import { accounts, usdcContractConfig, vitalik } from "@/_test/constants";
@@ -25,6 +26,11 @@ const network: Network = {
   maxRpcRequestConcurrency: 10,
 };
 
+const rpcRequestSpy = vi.spyOn(
+  network.client as { request: EIP1193RequestFn },
+  "request"
+);
+
 const logFilters: LogFilter[] = [
   {
     name: "USDC",
@@ -198,6 +204,47 @@ test("handles new blocks", async (context) => {
   await service.kill();
 });
 
+test("handles error while fetching new latest block gracefully", async (context) => {
+  const { common, eventStore } = context;
+
+  const service = new RealtimeSyncService({
+    common,
+    eventStore,
+    logFilters,
+    network,
+  });
+
+  await service.setup();
+  await service.start();
+
+  await sendUsdcTransferTransaction();
+  await testClient.mine({ blocks: 1 });
+
+  // Mock a failed new block request.
+  rpcRequestSpy.mockRejectedValueOnce(
+    new HttpRequestError({ url: "http://test.com" })
+  );
+  await service.addNewLatestBlock();
+
+  // Now, this one should succeed.
+  await service.addNewLatestBlock();
+
+  await service.onIdle();
+
+  const blocks = await eventStore.db.selectFrom("blocks").selectAll().execute();
+  expect(blocks).toHaveLength(6);
+  expect(blocks.map((block) => blobToBigInt(block.number))).toMatchObject([
+    16379996n,
+    16379997n,
+    16379998n,
+    16379999n,
+    16380000n,
+    16380001n,
+  ]);
+
+  await service.kill();
+});
+
 test("emits realtimeCheckpoint events", async (context) => {
   const { common, eventStore } = context;
 
```

### packages/core/src/realtime-sync/service.ts
```diff
@@ -194,9 +194,18 @@ export class RealtimeSyncService extends Emittery<RealtimeSyncEvents> {
 
   // This method is only public for to support the tests.
   addNewLatestBlock = async () => {
-    const block = await this.getLatestBlock();
-    const priority = Number.MAX_SAFE_INTEGER - hexToNumber(block.number);
-    this.queue.addTask(block, { priority });
+    try {
+      const block = await this.getLatestBlock();
+      const priority = Number.MAX_SAFE_INTEGER - hexToNumber(block.number);
+      this.queue.addTask(block, { priority });
+    } catch (error) {
+      // Do nothing, log the error. Might consider a retry limit here after which the service should die.
+      this.common.logger.error({
+        service: "realtime",
+        msg: "Error while fetching latest block",
+        error: error as Error,
+      });
+    }
   };
 
   private buildQueue = () => {
```
