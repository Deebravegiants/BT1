# [?] Fix current accelerations update race condition

## Summary
Severity: Unknown
Chain: Bitcoin
Component: mempool/mempool
Published: 2023-12-06
Source: https://github.com/mempool/mempool/commit/08a35b85a8719ad87ef75fb0eabb1ae3d883d444
Type: security-commit

## Details
Fix current accelerations update race condition

## Patch
### backend/src/api/mempool.ts
```diff
@@ -9,7 +9,7 @@ import loadingIndicators from './loading-indicators';
 import bitcoinClient from './bitcoin/bitcoin-client';
 import bitcoinSecondClient from './bitcoin/bitcoin-second-client';
 import rbfCache from './rbf-cache';
-import accelerationApi, { Acceleration } from './services/acceleration';
+import { Acceleration } from './services/acceleration';
 import redisCache from './redis-cache';
 
 class Mempool {
@@ -185,7 +185,7 @@ class Mempool {
     return txTimes;
   }
 
-  public async $updateMempool(transactions: string[], pollRate: number): Promise<void> {
+  public async $updateMempool(transactions: string[], accelerations: Acceleration[] | null, pollRate: number): Promise<void> {
     logger.debug(`Updating mempool...`);
 
     // warn if this run stalls the main loop for more than 2 minutes
@@ -330,7 +330,7 @@ class Mempool {
     const newTransactionsStripped = newTransactions.map((tx) => Common.stripTransaction(tx));
     this.latestTransactions = newTransactionsStripped.concat(this.latestTransactions).slice(0, 6);
 
-    const accelerationDelta = await this.$updateAccelerations();
+    const accelerationDelta = accelerations != null ? await this.$updateAccelerations(accelerations) : [];
     if (accelerationDelta.length) {
       hasChange = true;
     }
@@ -370,14 +370,12 @@ class Mempool {
     return this.accelerations;
   }
 
-  public async $updateAccelerations(): Promise<string[]> {
+  public $updateAccelerations(newAccelerations: Acceleration[]): string[] {
     if (!config.MEMPOOL_SERVICES.ACCELERATIONS) {
       return [];
     }
 
     try {
-      const newAccelerations = await accelerationApi.$fetchAccelerations();
-
       const changed: string[] = [];
 
       const newAccelerationMap: { [txid: string]: Acceleration } = {};
```

### backend/src/index.ts
```diff
@@ -43,6 +43,7 @@ import { AxiosError } from 'axios';
 import v8 from 'v8';
 import { formatBytes, getBytesUnit } from './utils/format';
 import redisCache from './api/redis-cache';
+import accelerationApi from './api/services/acceleration';
 
 class Server {
   private wss: WebSocket.Server | undefined;
@@ -205,10 +206,11 @@ class Server {
         }
       }
       const newMempool = await bitcoinApi.$getRawMempool();
+      const newAccelerations = await accelerationApi.$fetchAccelerations();
       const numHandledBlocks = await blocks.$updateBlocks();
       const pollRate = config.MEMPOOL.POLL_RATE_MS * (indexer.indexerIsRunning() ? 10 : 1);
       if (numHandledBlocks === 0) {
-        await memPool.$updateMempool(newMempool, pollRate);
+        await memPool.$updateMempool(newMempool, newAccelerations, pollRate);
       }
       indexer.$run();
       priceUpdater.$run();
```
