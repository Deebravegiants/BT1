# [?] Fix historical sync race condition (#241)

## Summary
Severity: Unknown
Chain: Indexer
Component: ponder-sh/ponder
Published: 2023-06-30
Source: https://github.com/ponder-sh/ponder/commit/438813b7221c00bf89eb1ec66cf22f90e3d52ab1
Type: security-commit

## Details
Fix historical sync race condition (#241)

* fix: historical sync race condition

* chore: changeset

* test: fix store tests

* chore: speed up postgres tests by dropping entire schema rather than migrating down (way more SQL queries)

* fix: also emit event

## Patch
### .changeset/metal-boats-protect.md
```diff
@@ -0,0 +1,5 @@
+---
+"@ponder/core": patch
+---
+
+Fixed a race condition bug in the historical sync service
```

### packages/core/src/_test/setup.ts
```diff
@@ -53,17 +53,17 @@ export async function setupEventStore(context: TestContext) {
     const pool = new Pool({ connectionString: process.env.DATABASE_URL });
     const databaseSchema = `vitest_pool_${process.pid}_${poolId}`;
     context.eventStore = new PostgresEventStore({ pool, databaseSchema });
+    await context.eventStore.migrateUp();
+
+    return async () => {
+      await pool.query(`DROP SCHEMA IF EXISTS "${databaseSchema}" CASCADE`);
+    };
   } else {
     const rawSqliteDb = new SqliteDatabase(":memory:");
     const db = patchSqliteDatabase({ db: rawSqliteDb });
     context.eventStore = new SqliteEventStore({ db });
+    await context.eventStore.migrateUp();
   }
-
-  await context.eventStore.migrateUp();
-
-  return async () => {
-    await context.eventStore.migrateDown();
-  };
 }
 
 /**
```

### packages/core/src/event-store/postgres/store.ts
```diff
@@ -199,21 +199,6 @@ export class PostgresEventStore implements EventStore {
     });
   };
 
-  getLogFilterCachedRanges = async ({ filterKey }: { filterKey: string }) => {
-    const results = await this.db
-      .selectFrom("logFilterCachedRanges")
-      .select(["filterKey", "startBlock", "endBlock", "endBlockTimestamp"])
-      .where("filterKey", "=", filterKey)
-      .execute();
-
-    return results.map((range) => ({
-      ...range,
-      startBlock: blobToBigInt(range.startBlock),
-      endBlock: blobToBigInt(range.endBlock),
-      endBlockTimestamp: blobToBigInt(range.endBlockTimestamp),
-    }));
-  };
-
   insertFinalizedLogs = async ({
     chainId,
     logs: rpcLogs,
@@ -247,19 +232,14 @@ export class PostgresEventStore implements EventStore {
     chainId,
     block: rpcBlock,
     transactions: rpcTransactions,
-    logFilterRange: {
-      logFilterKey,
-      blockNumberToCacheFrom,
-      logFilterStartBlockNumber,
-    },
+    logFilterRange: { logFilterKey, blockNumberToCacheFrom },
   }: {
     chainId: number;
     block: RpcBlock;
     transactions: RpcTransaction[];
     logFilterRange: {
       logFilterKey: string;
       blockNumberToCacheFrom: number;
-      logFilterStartBlockNumber: number;
     };
   }) => {
     const block: InsertableBlock = {
@@ -301,10 +281,15 @@ export class PostgresEventStore implements EventStore {
         .values(logFilterCachedRange)
         .execute();
     });
+  };
 
-    // After inserting the new cached range record, execute a transaction to merge
-    // all adjacent cached ranges. Return the end block timestamp of the cached interval
-    // that contains the start block number of the log filter.
+  mergeLogFilterCachedRanges = async ({
+    logFilterKey,
+    logFilterStartBlockNumber,
+  }: {
+    logFilterKey: string;
+    logFilterStartBlockNumber: number;
+  }) => {
     const startingRangeEndTimestamp = await this.db
       .transaction()
       .execute(async (tx) => {
@@ -366,6 +351,21 @@ export class PostgresEventStore implements EventStore {
     return { startingRangeEndTimestamp };
   };
 
+  getLogFilterCachedRanges = async ({ filterKey }: { filterKey: string }) => {
+    const results = await this.db
+      .selectFrom("logFilterCachedRanges")
+      .select(["filterKey", "startBlock", "endBlock", "endBlockTimestamp"])
+      .where("filterKey", "=", filterKey)
+      .execute();
+
+    return results.map((range) => ({
+      ...range,
+      startBlock: blobToBigInt(range.startBlock),
+      endBlock: blobToBigInt(range.endBlock),
+      endBlockTimestamp: blobToBigInt(range.endBlockTimestamp),
+    }));
+  };
+
   insertContractReadResult = async ({
     address,
     blockNumber,
```

### packages/core/src/event-store/sqlite/store.ts
```diff
@@ -173,21 +173,6 @@ export class SqliteEventStore implements EventStore {
     });
   };
 
-  getLogFilterCachedRanges = async ({ filterKey }: { filterKey: string }) => {
-    const results = await this.db
-      .selectFrom("logFilterCachedRanges")
-      .select(["filterKey", "startBlock", "endBlock", "endBlockTimestamp"])
-      .where("filterKey", "=", filterKey)
-      .execute();
-
-    return results.map((range) => ({
-      ...range,
-      startBlock: blobToBigInt(range.startBlock),
-      endBlock: blobToBigInt(range.endBlock),
-      endBlockTimestamp: blobToBigInt(range.endBlockTimestamp),
-    }));
-  };
-
   insertFinalizedLogs = async ({
     chainId,
     logs: rpcLogs,
@@ -216,20 +201,12 @@ export class SqliteEventStore implements EventStore {
     chainId,
     block: rpcBlock,
     transactions: rpcTransactions,
-    logFilterRange: {
-      logFilterKey,
-      blockNumberToCacheFrom,
-      logFilterStartBlockNumber,
-    },
+    logFilterRange: { logFilterKey, blockNumberToCacheFrom },
   }: {
     chainId: number;
     block: RpcBlock;
     transactions: RpcTransaction[];
-    logFilterRange: {
-      logFilterKey: string;
-      blockNumberToCacheFrom: number;
-      logFilterStartBlockNumber: number;
-    };
+    logFilterRange: { logFilterKey: string; blockNumberToCacheFrom: number };
   }) => {
     const block: InsertableBlock = {
       ...rpcToSqliteBlock(rpcBlock),
@@ -272,10 +249,15 @@ export class SqliteEventStore implements EventStore {
           .execute(),
       ]);
     });
+  };
 
-    // After inserting the new cached range record, execute a transaction to merge
-    // all adjacent cached ranges. Return the end block timestamp of the cached interval
-    // that contains the start block number of the log filter.
+  mergeLogFilterCachedRanges = async ({
+    logFilterKey,
+    logFilterStartBlockNumber,
+  }: {
+    logFilterKey: string;
+    logFilterStartBlockNumber: number;
+  }) => {
     const startingRangeEndTimestamp = await this.db
       .transaction()
       .execute(async (tx) => {
@@ -336,6 +318,21 @@ export class SqliteEventStore implements EventStore {
     return { startingRangeEndTimestamp };
   };
 
+  getLogFilterCachedRanges = async ({ filterKey }: { filterKey: string }) => {
+    const results = await this.db
+      .selectFrom("logFilterCachedRanges")
+      .select(["filterKey", "startBlock", "endBlock", "endBlockTimestamp"])
+      .where("filterKey", "=", filterKey)
+      .execute();
+
+    return results.map((range) => ({
+      ...range,
+      startBlock: blobToBigInt(range.startBlock),
+      endBlock: blobToBigInt(range.endBlock),
+      endBlockTimestamp: blobToBigInt(range.endBlockTimestamp),
+    }));
+  };
+
   insertContractReadResult = async ({
     address,
     blockNumber,
```

### packages/core/src/event-store/store.test.ts
```diff
@@ -272,9 +272,8 @@ test("insertFinalizedBlock inserts block as finalized", async (context) => {
     block: blockOne,
     transactions: blockOneTransactions,
     logFilterRange: {
-      blockNumberToCacheFrom: 15131900,
       logFilterKey: "test-filter-key",
-      logFilterStartBlockNumber: 15131900,
+      blockNumberToCacheFrom: 15131900,
     },
   });
 
@@ -301,9 +300,8 @@ test("insertFinalizedBlock inserts transactions as finalized", async (context) =
     block: blockOne,
     transactions: blockOneTransactions,
     logFilterRange: {
-      blockNumberToCacheFrom: 15131900,
       logFilterKey: "test-filter-key",
-      logFilterStartBlockNumber: 15131900,
+      blockNumberToCacheFrom: 15131900,
     },
   });
 
@@ -334,9 +332,8 @@ test("insertFinalizedBlock inserts a log filter cached interval", async (context
     block: blockOne,
     transactions: blockOneTransactions,
     logFilterRange: {
-      blockNumberToCacheFrom: 15131900,
       logFilterKey: "test-filter-key",
-      logFilterStartBlockNumber: 15131900,
+      blockNumberToCacheFrom: 15131900,
     },
   });
 
@@ -353,17 +350,16 @@ test("insertFinalizedBlock inserts a log filter cached interval", async (context
   expect(logFilterCachedRanges).toHaveLength(1);
 });
 
-test("insertFinalizedBlock merges cached intervals", async (context) => {
+test("mergeLogFilterCachedIntervals merges cached intervals", async (context) => {
   const { eventStore } = context;
 
   await eventStore.insertFinalizedBlock({
     chainId: 1,
     block: blockOne,
     transactions: blockOneTransactions,
     logFilterRange: {
-      blockNumberToCacheFrom: 15131900,
       logFilterKey: "test-filter-key",
-      logFilterStartBlockNumber: 15131900,
+      blockNumberToCacheFrom: 15131900,
     },
   });
 
@@ -372,12 +368,16 @@ test("insertFinalizedBlock merges cached intervals", async (context) => {
     block: blockTwo,
     transactions: blockTwoTransactions,
     logFilterRange: {
-      blockNumberToCacheFrom: 15495110,
       logFilterKey: "test-filter-key",
-      logFilterStartBlockNumber: 15131900,
+      blockNumberToCacheFrom: 15495110,
     },
   });
 
+  await eventStore.mergeLogFilterCachedRanges({
+    logFilterKey: "test-filter-key",
+    logFilterStartBlockNumber: 15131900,
+  });
+
   const logFilterCachedRanges = await eventStore.getLogFilterCachedRanges({
     filterKey: "test-filter-key",
   });
@@ -391,32 +391,41 @@ test("insertFinalizedBlock merges cached intervals", async (context) => {
   expect(logFilterCachedRanges).toHaveLength(1);
 });
 
-test("insertFinalizedBlock returns the startingRangeEndTimestamp", async (context) => {
+test("mergeLogFilterCachedIntervals returns the startingRangeEndTimestamp", async (context) => {
   const { eventStore } = context;
 
-  const { startingRangeEndTimestamp } = await eventStore.insertFinalizedBlock({
+  await eventStore.insertFinalizedBlock({
     chainId: 1,
     block: blockOne,
     transactions: blockOneTransactions,
     logFilterRange: {
-      blockNumberToCacheFrom: 15131900,
       logFilterKey: "test-filter-key",
-      logFilterStartBlockNumber: 15131900,
+      blockNumberToCacheFrom: 15131900,
     },
   });
 
+  const { startingRangeEndTimestamp } =
+    await eventStore.mergeLogFilterCachedRanges({
+      logFilterKey: "test-filter-key",
+      logFilterStartBlockNumber: 15131900,
+    });
+
   expect(startingRangeEndTimestamp).toBe(hexToNumber(blockOne.timestamp));
 
+  await eventStore.insertFinalizedBlock({
+    chainId: 1,
+    block: blockTwo,
+    transactions: blockTwoTransactions,
+    logFilterRange: {
+      logFilterKey: "test-filter-key",
+      blockNumberToCacheFrom: 15495110,
+    },
+  });
+
   const { startingRangeEndTimestamp: startingRangeEndTimestamp2 } =
-    await eventStore.insertFinalizedBlock({
-      chainId: 1,
-      block: blockTwo,
-      transactions: blockTwoTransactions,
-      logFilterRange: {
-        blockNumberToCacheFrom: 15495110,
-        logFilterKey: "test-filter-key",
-        logFilterStartBlockNumber: 15131900,
-      },
+    await eventStore.mergeLogFilterCachedRanges({
+      logFilterKey: "test-filter-key",
+      logFilterStartBlockNumber: 15131900,
     });
 
   expect(startingRangeEndTimestamp2).toBe(hexToNumber(blockTwo.timestamp));
```

### packages/core/src/event-store/store.ts
```diff
@@ -46,10 +46,18 @@ export interface EventStore {
     logFilterRange: {
       logFilterKey: string;
       blockNumberToCacheFrom: number;
-      logFilterStartBlockNumber: number;
     };
+  }): Promise<void>;
+
+  mergeLogFilterCachedRanges(options: {
+    logFilterKey: string;
+    logFilterStartBlockNumber: number;
   }): Promise<{ startingRangeEndTimestamp: number }>;
 
+  getLogFilterCachedRanges(options: {
+    filterKey: string;
+  }): Promise<LogFilterCachedRange[]>;
+
   insertUnfinalizedBlock(options: {
     chainId: number;
     block: RpcBlock;
@@ -67,10 +75,6 @@ export interface EventStore {
     toBlockNumber: number;
   }): Promise<void>;
 
-  getLogFilterCachedRanges(options: {
-    filterKey: string;
-  }): Promise<LogFilterCachedRange[]>;
-
   insertContractReadResult(options: {
     address: string;
     blockNumber: bigint;
```

### packages/core/src/historical-sync/service.test.ts
```diff
@@ -11,7 +11,6 @@ import { publicClient, testResources } from "@/_test/utils";
 import { encodeLogFilterKey } from "@/config/logFilterKey";
 import { LogFilter } from "@/config/logFilters";
 import { Network } from "@/config/networks";
-import { wait } from "@/utils/wait";
 
 import { HistoricalSyncService } from "./service";
 
@@ -317,14 +316,6 @@ test("start() emits historicalCheckpoint event", async (context) => {
 
   await service.onIdle();
 
-  // TODO: Remove this. It's just a test to see if there's indeed a
-  // a race condition happening here.
-  await wait(300);
-  const logFilterCachedRanges = await eventStore.getLogFilterCachedRanges({
-    filterKey: logFilters[0].filter.key,
-  });
-  console.log(logFilterCachedRanges);
-
   expect(emitSpy).toHaveBeenCalledWith("historicalCheckpoint", {
     timestamp: 1673275859, // Block timestamp of block 16369955
   });
```

### packages/core/src/historical-sync/service.ts
```diff
@@ -14,7 +14,7 @@ import type { EventStore } from "@/event-store/store";
 import { LoggerService } from "@/logs/service";
 import { MetricsService } from "@/metrics/service";
 import { formatEta, formatPercentage } from "@/utils/format";
-import { type Queue, createQueue } from "@/utils/queue";
+import { type Queue, type Worker, createQueue } from "@/utils/queue";
 import { startClock } from "@/utils/timer";
 
 import { findMissingIntervals } from "./intervals";
@@ -273,18 +273,44 @@ export class HistoricalSyncService extends Emittery<HistoricalSyncEvents> {
   };
 
   private buildQueue = () => {
-    const worker = async ({ task }: { task: LogSyncTask | BlockSyncTask }) => {
-      switch (task.kind) {
-        case "LOG_SYNC": {
-          return this.logTaskWorker({ task });
-        }
-        case "BLOCK_SYNC": {
-          return this.blockTaskWorker({ task });
-        }
+    const worker: Worker<LogSyncTask | BlockSyncTask> = async ({
+      task,
+      queue,
+    }) => {
+      if (task.kind === "LOG_SYNC") {
+        await this.logTaskWorker({ task });
+      } else {
+        await this.blockTaskWorker({ task });
       }
+
+      // If this is not the final task, return.
+      if (queue.size > 0 || queue.pending > 1) return;
+
+      // If this is the final task, run the cleanup/completion logic.
+
+      // It's possible for multiple block sync tasks to run simultaneously,
+      // resulting in a scenario where cached ranges are not fully merged.
+      // Merge all cached ranges once last time before emitting the `syncComplete` event.
+      await Promise.all(
+        this.logFilters.map((logFilter) =>
+          this.updateHistoricalCheckpoint({ logFilter })
+        )
+      );
+
+      this.stats.duration = this.stats.endDuration();
+      this.stats.isComplete = true;
+      this.emit("syncComplete");
+      this.logger.info({
+        service: "historical",
+        msg: `Completed sync in ${formatEta(this.stats.duration)} (network=${
+          this.network.name
+        })`,
+        network: this.network.name,
+        duration: this.stats.duration,
+      });
     };
 
-    const queue = createQueue<LogSyncTask | BlockSyncTask, unknown, any>({
+    const queue = createQueue<LogSyncTask | BlockSyncTask>({
       worker,
       options: { concurrency: 10, autoStart: false },
       onAdd: ({ task }) => {
@@ -471,20 +497,6 @@ export class HistoricalSyncService extends Emittery<HistoricalSyncEvents> {
             : task.blockNumberToCacheFrom);
         queue.addTask(task, { priority, retry: true });
       },
-      onIdle: () => {
-        if (this.stats.isComplete) return;
-        this.stats.duration = this.stats.endDuration();
-        this.stats.isComplete = true;
-        this.emit("syncComplete");
-        this.logger.info({
-          service: "historical",
-          msg: `Completed sync in ${formatEta(this.stats.duration)} (network=${
-            this.network.name
-          })`,
-          network: this.network.name,
-          duration: this.stats.duration,
-        });
-      },
     });
 
     return queue;
@@ -598,16 +610,28 @@ export class HistoricalSyncService extends Emittery<HistoricalSyncEvents> {
       requiredTxHashes.has(tx.hash)
     );
 
+    await this.eventStore.insertFinalizedBlock({
+      chainId: this.network.chainId,
+      block,
+      transactions,
+      logFilterRange: {
+        logFilterKey: logFilter.filter.key,
+        blockNumberToCacheFrom,
+      },
+    });
+
+    await this.updateHistoricalCheckpoint({ logFilter });
+  };
+
+  updateHistoricalCheckpoint = async ({
+    logFilter,
+  }: {
+    logFilter: LogFilter;
+  }) => {
     const { startingRangeEndTimestamp } =
-      await this.eventStore.insertFinalizedBlock({
-        chainId: this.network.chainId,
-        block,
-        transactions,
-        logFilterRange: {
-          logFilterKey: logFilter.filter.key,
-          blockNumberToCacheFrom,
-          logFilterStartBlockNumber: logFilter.filter.startBlock,
-        },
+      await this.eventStore.mergeLogFilterCachedRanges({
+        logFilterKey: logFilter.filter.key,
+        logFilterStartBlockNumber: logFilter.filter.startBlock,
       });
 
     this.logFilterCheckpoints[logFilter.name] = Math.max(
```
