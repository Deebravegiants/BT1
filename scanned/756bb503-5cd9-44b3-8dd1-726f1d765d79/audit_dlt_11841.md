# [?] Crash recovery fix (#1949)

## Summary
Severity: Unknown
Chain: Indexer
Component: ponder-sh/ponder
Published: 2025-08-08
Source: https://github.com/ponder-sh/ponder/commit/922bac364912aa3a268fd07c6e57e3efcffeea43
Type: security-commit

## Details
Crash recovery fix (#1949)

* add finalized_checkpoint

* new finalize algo impl

* crash recovery

* add shutdown to integration test

* syntax fix

* fix sql syntax

* nits

* sync logic

* ordering to finalize

* fix integration test

* nits

* fix integration test restart

* simplify omnichain finalize

* fix crash recovery error

* skip restart for super assessment

* fix shutdown

* crash recovery action

* try sync progress

* bump version

* fix end condition

* chore: changeset

* cleanup

---------

Co-authored-by: Kyle Scott <kyscott@umich.edu>

## Patch
### .changeset/chilly-colts-taste.md
```diff
@@ -0,0 +1,5 @@
+---
+"ponder": patch
+---
+
+Fixed a bug with crash recovery causing missing or duplicate events.
```

### integration-test/README.md
```diff
@@ -36,4 +36,5 @@ b821add56458bb3507f5fdde0a06bd20bb50f4b1cb89e014f6d19d8638438d23
 20ad4bce62c7765e45a045b40f66b97c39017a8e871d9ece7018706b85d3077b
 f9ecd61178de5a6b2fcdee26f836dd23ed8ffd8b3d50f33f72ee62e84acf97ef
 d482923c1a77cdf50ee254ddcc4b677018796fe026a579c49f8cff9f7b9f6f89
-fb0b04ef7e6c4675fdfea6e86ecce4e046dc7af754ec98c3150c717dd23b51f3
\ No newline at end of file
+fb0b04ef7e6c4675fdfea6e86ecce4e046dc7af754ec98c3150c717dd23b51f3
+f6ed9fe614a4e988f7274f566a5a98d61028de8f1de5428b9398b0b195177438
\ No newline at end of file
```

### integration-test/src/index.ts
```diff
@@ -106,22 +106,32 @@ export const SIM_PARAMS = {
   ),
   REALTIME_DELAY_RATE: pick([0, 0.4, 0.8], "realtime-delay-rate"),
   UNFINALIZED_BLOCKS: pick([0, 0, 100, 100, 1000, 1100], "unfinalized-blocks"),
-  // SHUTDOWN_TIMER: pick(
-  //   [
-  //     undefined,
-  //     () => new Promise((resolve) => setTimeout(resolve, 1000)),
-  //     () => new Promise((resolve) => setTimeout(resolve, 5000)),
-  //   ],
-  //   "shutdown",
-  // ),
-  // REALTIME_SHUTDOWN_RATE: pick([0, 0.001, 0.002], "realtime-shutdown-rate"),
+  SHUTDOWN_TIMER:
+    APP_ID === "super-assessment"
+      ? undefined
+      : pick(
+          [
+            undefined,
+            () => new Promise((resolve) => setTimeout(resolve, 500)),
+            () => new Promise((resolve) => setTimeout(resolve, 1000)),
+            () => new Promise((resolve) => setTimeout(resolve, 2000)),
+            () => new Promise((resolve) => setTimeout(resolve, 5000)),
+          ],
+          "shutdown",
+        ),
+  REALTIME_SHUTDOWN_RATE:
+    APP_ID === "super-assessment"
+      ? undefined
+      : pick([0, 0.001, 0.002], "realtime-shutdown-rate"),
   ORDERING: pick(["multichain", "omnichain"], "ordering"),
   REALTIME_BLOCK_HAS_TRANSACTIONS: pick(
     [true, false],
     "realtime-block-has-transactions",
   ),
 };
 
+export let RESTART_COUNT = 0;
+
 export const DB = drizzle(DATABASE_URL!, { casing: "snake_case" });
 export const APP_DB = drizzle(`${DATABASE_URL!}/${UUID}`, {
   casing: "snake_case",
@@ -1256,9 +1266,32 @@ const onBuild = async (app: PonderApp) => {
     const end = intervals[intervals.length - 1]![1];
 
     if (SIM_PARAMS.UNFINALIZED_BLOCKS !== 0) {
-      app.indexingBuild.finalizedBlocks[i] = await _eth_getBlockByNumber(rpc, {
-        blockNumber: end - SIM_PARAMS.UNFINALIZED_BLOCKS,
-      });
+      const { rows } = await APP_DB.execute(`
+SELECT number FROM ponder_sync.blocks WHERE timestamp > (
+  SELECT SUBSTRING(finalized_checkpoint, 1, 10)::numeric as t FROM _ponder_checkpoint WHERE chain_name = '${chain.name}'
+) AND chain_id = ${chain.id} ORDER BY timestamp ASC LIMIT 1`);
+
+      if (rows.length > 0) {
+        app.indexingBuild.finalizedBlocks[i] = await _eth_getBlockByNumber(
+          rpc,
+          {
+            blockNumber: Math.min(
+              Math.max(
+                Number(rows[0]!.number),
+                end - SIM_PARAMS.UNFINALIZED_BLOCKS,
+              ),
+              end - 10,
+            ),
+          },
+        );
+      } else {
+        app.indexingBuild.finalizedBlocks[i] = await _eth_getBlockByNumber(
+          rpc,
+          {
+            blockNumber: end - SIM_PARAMS.UNFINALIZED_BLOCKS,
+          },
+        );
+      }
     }
 
     // TODO(kyle) delete unfinalized data
@@ -1322,6 +1355,8 @@ const onBuild = async (app: PonderApp) => {
           isAccepted = await onBlock(block!);
         }
 
+        await onBlock(block!);
+
         app.common.logger.warn({
           service: "sim",
           msg: `Realtime block subscription for chain '${chain.name}' completed`,
@@ -1354,6 +1389,9 @@ let kill = await start({
 });
 
 export const restart = async () => {
+  if (RESTART_COUNT === 2) return;
+  RESTART_COUNT += 1;
+  console.log("Restarting app");
   await kill!();
   kill = await start({
     cliOptions: {
@@ -1367,10 +1405,10 @@ export const restart = async () => {
   });
 };
 
-// if (SIM_PARAMS.SHUTDOWN_TIMER) {
-//   await SIM_PARAMS.SHUTDOWN_TIMER();
-//   await restart();
-// }
+if (SIM_PARAMS.SHUTDOWN_TIMER) {
+  await SIM_PARAMS.SHUTDOWN_TIMER();
+  await restart();
+}
 
 if (SIM_PARAMS.UNFINALIZED_BLOCKS === 0) {
   while (true) {
```

### integration-test/src/rpc-sim.ts
```diff
@@ -15,7 +15,7 @@ import { zeroLogsBloom } from "../../packages/core/src/sync-realtime/bloom.js";
 import { promiseWithResolvers } from "../../packages/core/src/utils/promiseWithResolvers.js";
 import { createQueue } from "../../packages/core/src/utils/queue.js";
 import * as RPC_SCHEMA from "../schema.js";
-import { DB, SEED, SIM_PARAMS } from "./index.js";
+import { DB, SEED, SIM_PARAMS, restart } from "./index.js";
 
 const PONDER_RPC_METHODS = [
   "eth_getBlockByNumber",
@@ -573,9 +573,9 @@ export const realtimeBlockEngine = async (
 
     const random = seedrandom(SEED + chainId + nextBlock.number);
 
-    // if (random() < SIM_PARAMS.REALTIME_SHUTDOWN_RATE) {
-    //   await restart();
-    // }
+    if (random() < SIM_PARAMS.REALTIME_SHUTDOWN_RATE) {
+      await restart();
+    }
 
     if (random() < SIM_PARAMS.REALTIME_FAST_FORWARD_RATE) {
       return simulate(chainId);
```

### packages/core/src/_test/setup.ts
```diff
@@ -205,7 +205,8 @@ export async function setupDatabaseServices(
 
   await database.migrate({
     buildId: overrides.indexingBuild?.buildId ?? "abc",
-    ordering: "multichain",
+    chains: overrides.indexingBuild?.chains ?? [],
+    finalizedBlocks: overrides.indexingBuild?.finalizedBlocks ?? [],
   });
 
   await database.migrateSync().catch((err) => {
```

### packages/core/src/bin/commands/dev.ts
```diff
@@ -179,7 +179,8 @@ export async function dev({ cliOptions }: { cliOptions: CliOptions }) {
         });
         crashRecoveryCheckpoint = await database.migrate({
           buildId: indexingBuildResult.result.buildId,
-          ordering: preBuild.ordering,
+          chains: indexingBuildResult.result.chains,
+          finalizedBlocks: indexingBuildResult.result.finalizedBlocks,
         });
 
         const apiResult = await build.executeApi({
```

### packages/core/src/bin/commands/start.ts
```diff
@@ -141,7 +141,8 @@ export async function start({
   });
   const crashRecoveryCheckpoint = await database.migrate({
     buildId: indexingBuildResult.result.buildId,
-    ordering: preBuild.ordering,
+    chains: indexingBuildResult.result.chains,
+    finalizedBlocks: indexingBuildResult.result.finalizedBlocks,
   });
 
   const apiResult = await build.executeApi({
```

### packages/core/src/bin/utils/run.ts
```diff
@@ -176,12 +176,14 @@ export async function run({
               chainName: chain.name,
               chainId: chain.id,
               latestCheckpoint: sync.getStartCheckpoint(chain),
+              finalizedCheckpoint: sync.getStartCheckpoint(chain),
               safeCheckpoint: sync.getStartCheckpoint(chain),
             })),
           )
           .onConflictDoUpdate({
             target: PONDER_CHECKPOINT.chainName,
             set: {
+              finalizedCheckpoint: sql`excluded.finalized_checkpoint`,
               safeCheckpoint: sql`excluded.safe_checkpoint`,
               latestCheckpoint: sql`excluded.latest_checkpoint`,
             },
@@ -340,13 +342,15 @@ export async function run({
                     )!.name,
                     chainId,
                     latestCheckpoint: checkpoint,
+                    finalizedCheckpoint: checkpoint,
                     safeCheckpoint: checkpoint,
                   })),
                 )
                 .onConflictDoUpdate({
                   target: PONDER_CHECKPOINT.chainName,
                   set: {
                     safeCheckpoint: sql`excluded.safe_checkpoint`,
+                    finalizedCheckpoint: sql`excluded.finalized_checkpoint`,
                     latestCheckpoint: sql`excluded.latest_checkpoint`,
                   },
                 }),
@@ -605,9 +609,9 @@ EXECUTE PROCEDURE "${namespaceBuild.viewsSchema}".${notification};`),
           await dropTriggers(tx, { tables });
 
           const counts = await revert(tx, {
-            tables,
             checkpoint: event.checkpoint,
-            ordering: preBuild.ordering,
+            tables,
+            preBuild,
           });
 
           for (const [index, table] of tables.entries()) {
@@ -621,35 +625,21 @@ EXECUTE PROCEDURE "${namespaceBuild.viewsSchema}".${notification};`),
         });
 
         break;
-      case "finalize":
-        await database.userQB.transaction(async (tx) => {
-          await tx.wrap((tx) =>
-            tx.update(PONDER_CHECKPOINT).set({
-              safeCheckpoint: event.checkpoint,
-            }),
-          );
-
-          const counts = await finalize(tx, {
-            tables,
-            checkpoint: event.checkpoint,
-          });
-
-          for (const [index, table] of tables.entries()) {
-            common.logger.info({
-              service: "database",
-              msg: `Finalized ${counts[index]} operations from '${getTableName(table)}'`,
-            });
-          }
-
-          const decoded = decodeCheckpoint(event.checkpoint);
+      case "finalize": {
+        const count = await finalize(database.userQB, {
+          checkpoint: event.checkpoint,
+          tables,
+          preBuild,
+          namespaceBuild,
+        });
 
-          common.logger.debug({
-            service: "database",
-            msg: `Updated finalized checkpoint to (timestamp=${decoded.blockTimestamp} chainId=${decoded.chainId} block=${decoded.blockNumber})`,
-          });
+        common.logger.info({
+          service: "database",
+          msg: `Finalized ${count} operations.`,
         });
 
         break;
+      }
       default:
         never(event);
     }
```

### packages/core/src/database/actions.test.ts
```diff
@@ -27,7 +27,7 @@ import {
   finalize,
   revert,
 } from "./actions.js";
-import type { Database } from "./index.js";
+import { type Database, getPonderCheckpointTable } from "./index.js";
 
 beforeEach(setupCommon);
 beforeEach(setupIsolatedDatabase);
@@ -61,6 +61,15 @@ test("finalize()", async (context) => {
   });
 
   // setup tables, reorg tables, and metadata checkpoint
+  await database.userQB.wrap((tx) =>
+    tx.insert(getPonderCheckpointTable()).values({
+      chainName: "mainnet",
+      chainId: 1,
+      safeCheckpoint: createCheckpoint({ chainId: 1n, blockNumber: 0n }),
+      finalizedCheckpoint: createCheckpoint({ chainId: 1n, blockNumber: 0n }),
+      latestCheckpoint: createCheckpoint({ chainId: 1n, blockNumber: 0n }),
+    }),
+  );
 
   await createTriggers(database.userQB, { tables: [account] });
 
@@ -96,6 +105,8 @@ test("finalize()", async (context) => {
   await finalize(database.userQB, {
     checkpoint: createCheckpoint({ chainId: 1n, blockNumber: 10n }),
     tables: [account],
+    preBuild: { ordering: "multichain" },
+    namespaceBuild: { schema: "public", viewsSchema: undefined },
   });
 
   // reorg tables
@@ -260,7 +271,7 @@ test("revert()", async (context) => {
     await revert(tx, {
       checkpoint: createCheckpoint({ chainId: 1n, blockNumber: 9n }),
       tables: [account],
-      ordering: "multichain",
+      preBuild: { ordering: "multichain" },
     });
   });
 
@@ -315,7 +326,7 @@ test("revert() with composite primary key", async (context) => {
     await revert(tx, {
       checkpoint: createCheckpoint({ chainId: 1n, blockNumber: 11n }),
       tables: [test],
-      ordering: "multichain",
+      preBuild: { ordering: "multichain" },
     });
   });
 
```

### packages/core/src/database/actions.ts
```diff
@@ -1,10 +1,15 @@
 import { getPrimaryKeyColumns } from "@/drizzle/index.js";
 import { getTableNames } from "@/drizzle/index.js";
 import { getColumnCasing, getReorgTable } from "@/drizzle/kit/index.js";
-import type { SchemaBuild } from "@/internal/types.js";
+import type {
+  NamespaceBuild,
+  PreBuild,
+  SchemaBuild,
+} from "@/internal/types.js";
 import { MAX_CHECKPOINT_STRING, decodeCheckpoint } from "@/utils/checkpoint.js";
 import { eq, getTableColumns, getTableName } from "drizzle-orm";
 import { type PgTable, getTableConfig } from "drizzle-orm/pg-core";
+import { getPonderCheckpointTable } from "./index.js";
 import type { QB } from "./queryBuilder.js";
 
 export const createIndexes = async (
@@ -94,100 +99,86 @@ export const revert = async (
   {
     checkpoint,
     tables,
-    ordering,
+    preBuild,
   }: {
     checkpoint: string;
     tables: PgTable[];
-    ordering: "multichain" | "omnichain";
+    preBuild: Pick<PreBuild, "ordering">;
   },
 ): Promise<number[]> => {
   return qb.transaction({ label: "revert" }, async (tx) => {
-    let minOperationId: number | undefined;
-    if (ordering === "multichain") {
-      minOperationId = await tx
+    const counts: number[] = [];
+    if (preBuild.ordering === "multichain") {
+      const minOperationId = await tx
         .wrap((tx) =>
           tx.execute(`
-SELECT MIN(min_op_id) AS global_min_op_id FROM (
+SELECT MIN(operation_id) AS operation_id FROM (
 ${tables
   .map(
     (table) => `
-SELECT MIN(operation_id) AS min_op_id FROM "${getTableConfig(table).schema ?? "public"}"."${getTableName(getReorgTable(table))}"
+SELECT MIN(operation_id) AS operation_id FROM "${getTableConfig(table).schema ?? "public"}"."${getTableName(getReorgTable(table))}"
 WHERE SUBSTRING(checkpoint, 11, 16)::numeric = ${String(decodeCheckpoint(checkpoint).chainId)}
-AND checkpoint > '${checkpoint}'
-`,
+AND checkpoint > '${checkpoint}'`,
   )
-  .join(" UNION ALL ")}) AS all_mins             
-`),
+  .join(" UNION ALL ")}) AS all_mins;`),
         )
         .then((result) => {
           // @ts-ignore
-          return result.rows[0]?.global_min_op_id as number | undefined;
+          return result.rows[0]?.operation_id as string | null;
         });
-    }
 
-    const counts: number[] = [];
-    for (const table of tables) {
-      const primaryKeyColumns = getPrimaryKeyColumns(table);
-      const schema = getTableConfig(table).schema ?? "public";
-
-      const baseQuery = `
-    reverted2 AS (
-      SELECT ${primaryKeyColumns.map(({ sql }) => `"${sql}"`).join(", ")}, MIN(operation_id) AS operation_id FROM reverted1
-      GROUP BY ${primaryKeyColumns.map(({ sql }) => `"${sql}"`).join(", ")}
-    ), reverted3 AS (
-      SELECT ${Object.values(getTableColumns(table))
-        .map((column) => `reverted1."${getColumnCasing(column, "snake_case")}"`)
-        .join(", ")}, reverted1.operation FROM reverted2
-      INNER JOIN reverted1
-      ON ${primaryKeyColumns.map(({ sql }) => `reverted2."${sql}" = reverted1."${sql}"`).join("AND ")}
-      AND reverted2.operation_id = reverted1.operation_id
-    ), inserted AS (
-      DELETE FROM "${schema}"."${getTableName(table)}" as t
-      WHERE EXISTS (
-        SELECT * FROM reverted3
-        WHERE ${primaryKeyColumns.map(({ sql }) => `t."${sql}" = reverted3."${sql}"`).join("AND ")}
-        AND OPERATION = 0
-      )
-      RETURNING *
-    ), updated_or_deleted AS (
-      INSERT INTO  "${schema}"."${getTableName(table)}"
-      SELECT ${Object.values(getTableColumns(table))
-        .map((column) => `"${getColumnCasing(column, "snake_case")}"`)
-        .join(", ")} FROM reverted3
-      WHERE operation = 1 OR operation = 2
-      ON CONFLICT (${primaryKeyColumns.map(({ sql }) => `"${sql}"`).join(", ")})
-      DO UPDATE SET
-        ${Object.values(getTableColumns(table))
-          .map(
-            (column) =>
-              `"${getColumnCasing(column, "snake_case")}" = EXCLUDED."${getColumnCasing(column, "snake_case")}"`,
-          )
-          .join(", ")}
-      RETURNING *
-    ) SELECT COUNT(*) FROM reverted1 as count;`;
+      for (const table of tables) {
+        const primaryKeyColumns = getPrimaryKeyColumns(table);
+        const schema = getTableConfig(table).schema ?? "public";
 
-      let result: unknown;
-      if (ordering === "multichain") {
-        result = await tx.wrap((tx) =>
+        const result = await tx.wrap((tx) =>
           tx.execute(`
 WITH reverted1 AS (
-DELETE FROM "${schema}"."${getTableName(getReorgTable(table))}"
-WHERE ${minOperationId!} IS NOT NULL AND operation_id >= ${minOperationId!}
-RETURNING * 
-), ${baseQuery}`),
+  DELETE FROM "${schema}"."${getTableName(getReorgTable(table))}"
+  WHERE ${minOperationId!} IS NOT NULL AND operation_id >= ${minOperationId!}
+  RETURNING * 
+), reverted2 AS (
+  SELECT ${primaryKeyColumns.map(({ sql }) => `"${sql}"`).join(", ")}, MIN(operation_id) AS operation_id FROM reverted1
+  GROUP BY ${primaryKeyColumns.map(({ sql }) => `"${sql}"`).join(", ")}
+), reverted3 AS (
+  SELECT ${Object.values(getTableColumns(table))
+    .map((column) => `reverted1."${getColumnCasing(column, "snake_case")}"`)
+    .join(", ")}, reverted1.operation FROM reverted2
+  INNER JOIN reverted1
+  ON ${primaryKeyColumns.map(({ sql }) => `reverted2."${sql}" = reverted1."${sql}"`).join("AND ")}
+  AND reverted2.operation_id = reverted1.operation_id
+), ${getRevertSql({ table })};`),
         );
-      } else {
-        result = await tx.wrap((tx) =>
+
+        // @ts-ignore
+        counts.push(result.rows[0]!.count);
+      }
+    } else {
+      for (const table of tables) {
+        const primaryKeyColumns = getPrimaryKeyColumns(table);
+        const schema = getTableConfig(table).schema ?? "public";
+
+        const result = await tx.wrap((tx) =>
           tx.execute(`
 WITH reverted1 AS (
-DELETE FROM "${schema}"."${getTableName(getReorgTable(table))}"
-WHERE checkpoint > '${checkpoint}' RETURNING *
-), ${baseQuery}`),
+  DELETE FROM "${schema}"."${getTableName(getReorgTable(table))}"
+  WHERE checkpoint > '${checkpoint}' RETURNING * 
+), reverted2 AS (
+  SELECT ${primaryKeyColumns.map(({ sql }) => `"${sql}"`).join(", ")}, MIN(operation_id) AS operation_id FROM reverted1
+  GROUP BY ${primaryKeyColumns.map(({ sql }) => `"${sql}"`).join(", ")}
+), reverted3 AS (
+  SELECT ${Object.values(getTableColumns(table))
+    .map((column) => `reverted1."${getColumnCasing(column, "snake_case")}"`)
+    .join(", ")}, reverted1.operation FROM reverted2
+  INNER JOIN reverted1
+  ON ${primaryKeyColumns.map(({ sql }) => `reverted2."${sql}" = reverted1."${sql}"`).join("AND ")}
+  AND reverted2.operation_id = reverted1.operation_id
+), ${getRevertSql({ table })};`),
         );
-      }
 
-      // @ts-ignore
-      counts.push(result.rows[0]!.count);
+        // @ts-ignore
+        counts.push(result.rows[0]!.count);
+      }
     }
 
     return counts;
@@ -196,46 +187,113 @@ WHERE checkpoint > '${checkpoint}' RETURNING *
 
 export const finalize = async (
   qb: QB,
-  { checkpoint, tables }: { checkpoint: string; tables: PgTable[] },
-): Promise<number[]> => {
+  {
+    checkpoint,
+    tables,
+    preBuild,
+    namespaceBuild,
+  }: {
+    checkpoint: string;
+    tables: PgTable[];
+    preBuild: Pick<PreBuild, "ordering">;
+    namespaceBuild: NamespaceBuild;
+  },
+): Promise<number> => {
+  const PONDER_CHECKPOINT = getPonderCheckpointTable(namespaceBuild.schema);
+
+  // NOTE: It is invariant that PONDER_CHECKPOINT has a value for each chain.
+
   return qb.transaction({ label: "finalize" }, async (tx) => {
-    const min_op_id = await tx
-      .wrap((tx) =>
-        tx.execute(`
-SELECT MIN(min_op_id) AS global_min_op_id FROM (
+    let count = 0;
+
+    if (preBuild.ordering === "multichain") {
+      await tx.wrap((tx) =>
+        tx
+          .update(PONDER_CHECKPOINT)
+          .set({ finalizedCheckpoint: checkpoint })
+          .where(
+            eq(
+              PONDER_CHECKPOINT.chainId,
+              Number(decodeCheckpoint(checkpoint).chainId),
+            ),
+          ),
+      );
+
+      const minOperationId = await tx
+        .wrap((tx) =>
+          tx.execute(`
+SELECT MIN(operation_id) AS operation_id FROM (
 ${tables
   .map(
     (table) => `
-SELECT MIN(operation_id) AS min_op_id FROM "${getTableConfig(table).schema ?? "public"}"."${getTableName(getReorgTable(table))}"
-WHERE checkpoint > '${checkpoint}'
-`,
+SELECT MIN(operation_id) AS operation_id FROM "${getTableConfig(table).schema ?? "public"}"."${getTableName(getReorgTable(table))}"
+WHERE checkpoint > (
+  SELECT finalized_checkpoint 
+  FROM "${getTableConfig(PONDER_CHECKPOINT).schema ?? "public"}"."${getTableName(PONDER_CHECKPOINT)}" 
+  WHERE chain_id = SUBSTRING(checkpoint, 11, 16)::numeric
+)`,
   )
-  .join(" UNION ALL ")}) AS all_mins            
-`),
-      )
-      .then((result) => {
-        // @ts-ignore
-        return result.rows[0]?.global_min_op_id as number | undefined;
-      });
+  .join(" UNION ALL ")}) AS all_mins;`),
+        )
+        .then((result) => {
+          // @ts-ignore
+          return result.rows[0]?.operation_id as string | null;
+        });
 
-    const counts: number[] = [];
-    for (const table of tables) {
-      const schema = getTableConfig(table).schema ?? "public";
       const result = await tx.wrap((tx) =>
         tx.execute(`
-WITH deleted AS (
-  DELETE FROM "${schema}"."${getTableName(getReorgTable(table))}"
-  WHERE ${min_op_id} IS NULL OR operation_id < ${min_op_id}
-  RETURNING *
-) SELECT COUNT(*) FROM deleted AS count; 
-`),
+    WITH ${tables
+      .map(
+        (table, index) => `
+    deleted_${index} AS (
+      DELETE FROM "${getTableConfig(table).schema ?? "public"}"."${getTableName(getReorgTable(table))}"
+      WHERE ${minOperationId} IS NULL OR operation_id < ${minOperationId}
+      RETURNING *
+    )`,
+      )
+      .join(",\n")},
+    all_deleted AS (
+      ${tables
+        .map((_, index) => `SELECT checkpoint FROM deleted_${index}`)
+        .join(" UNION ALL ")}
+    )
+    SELECT MAX(checkpoint) as safe_checkpoint, SUBSTRING(checkpoint, 11, 16)::numeric as chain_id, COUNT(*) AS deleted_count 
+    FROM all_deleted
+    GROUP BY SUBSTRING(checkpoint, 11, 16)::numeric;`),
       );
 
-      // @ts-ignore
-      counts.push(result.rows[0]!.count);
+      for (const { chain_id, safe_checkpoint, deleted_count } of result.rows) {
+        count += Number(deleted_count);
+
+        await tx.wrap((tx) =>
+          tx
+            .update(PONDER_CHECKPOINT)
+            .set({ safeCheckpoint: safe_checkpoint as string })
+            .where(eq(PONDER_CHECKPOINT.chainId, chain_id as number)),
+        );
+      }
+    } else {
+      await tx.wrap((tx) =>
+        tx
+          .update(PONDER_CHECKPOINT)
+          .set({ finalizedCheckpoint: checkpoint, safeCheckpoint: checkpoint }),
+      );
+
+      for (const table of tables) {
+        count += await tx
+          .wrap((tx) =>
+            tx.execute(`
+WITH deleted AS (
+  DELETE FROM "${getTableConfig(table).schema ?? "public"}"."${getTableName(getReorgTable(table))}"
+  WHERE checkpoint <= '${checkpoint}'
+  RETURNING *
+) SELECT COUNT(*) AS deleted_count FROM deleted;`),
+          )
+          .then((result) => Number(result.rows[0]!.deleted_count));
+      }
     }
 
-    return counts;
+    return count;
   });
 };
 
@@ -251,3 +309,57 @@ export const commitBlock = async (
       .where(eq(reorgTable.checkpoint, MAX_CHECKPOINT_STRING)),
   );
 };
+
+export const crashRecovery = async (qb: QB, { table }: { table: PgTable }) => {
+  const primaryKeyColumns = getPrimaryKeyColumns(table);
+  const schema = getTableConfig(table).schema ?? "public";
+
+  await qb.wrap((db) =>
+    db.execute(`
+WITH reverted1 AS (
+  DELETE FROM "${schema}"."${getTableName(getReorgTable(table))}"
+  RETURNING *
+), reverted2 AS (
+  SELECT ${primaryKeyColumns.map(({ sql }) => `"${sql}"`).join(", ")}, MIN(operation_id) AS operation_id FROM reverted1
+  GROUP BY ${primaryKeyColumns.map(({ sql }) => `"${sql}"`).join(", ")}
+), reverted3 AS (
+  SELECT ${Object.values(getTableColumns(table))
+    .map((column) => `reverted1."${getColumnCasing(column, "snake_case")}"`)
+    .join(", ")}, reverted1.operation FROM reverted2
+  INNER JOIN reverted1
+  ON ${primaryKeyColumns.map(({ sql }) => `reverted2."${sql}" = reverted1."${sql}"`).join("AND ")}
+  AND reverted2.operation_id = reverted1.operation_id
+), ${getRevertSql({ table })}`),
+  );
+};
+
+export const getRevertSql = ({ table }: { table: PgTable }) => {
+  const primaryKeyColumns = getPrimaryKeyColumns(table);
+  const schema = getTableConfig(table).schema ?? "public";
+
+  return `
+inserted AS (
+  DELETE FROM "${schema}"."${getTableName(table)}" as t
+  WHERE EXISTS (
+    SELECT * FROM reverted3
+    WHERE ${primaryKeyColumns.map(({ sql }) => `t."${sql}" = reverted3."${sql}"`).join("AND ")}
+    AND OPERATION = 0
+  )
+  RETURNING *
+), updated_or_deleted AS (
+  INSERT INTO  "${schema}"."${getTableName(table)}"
+  SELECT ${Object.values(getTableColumns(table))
+    .map((column) => `"${getColumnCasing(column, "snake_case")}"`)
+    .join(", ")} FROM reverted3
+  WHERE operation = 1 OR operation = 2
+  ON CONFLICT (${primaryKeyColumns.map(({ sql }) => `"${sql}"`).join(", ")})
+  DO UPDATE SET
+    ${Object.values(getTableColumns(table))
+      .map(
+        (column) =>
+          `"${getColumnCasing(column, "snake_case")}" = EXCLUDED."${getColumnCasing(column, "snake_case")}"`,
+      )
+      .join(", ")}
+  RETURNING *
+) SELECT COUNT(*) FROM reverted1 as count;`;
+};
```

### packages/core/src/database/index.test.ts
```diff
@@ -1,4 +1,5 @@
 import { setupCommon, setupIsolatedDatabase } from "@/_test/setup.js";
+import { getChain } from "@/_test/utils.js";
 import { buildSchema } from "@/build/schema.js";
 import { onchainEnum, onchainTable, primaryKey } from "@/drizzle/onchain.js";
 import { createRealtimeIndexingStore } from "@/indexing-store/realtime.js";
@@ -65,7 +66,11 @@ test("migrate() succeeds with empty schema", async (context) => {
     },
   });
 
-  await database.migrate({ buildId: "abc", ordering: "multichain" });
+  await database.migrate({
+    buildId: "abc",
+    chains: [],
+    finalizedBlocks: [],
+  });
 
   const tableNames = await getUserTableNames(database, "public");
   expect(tableNames).toContain("account");
@@ -117,7 +122,11 @@ test("migrate() with empty schema creates tables and enums", async (context) =>
     },
   });
 
-  await database.migrate({ buildId: "abc", ordering: "multichain" });
+  await database.migrate({
+    buildId: "abc",
+    chains: [],
+    finalizedBlocks: [],
+  });
 
   const tableNames = await getUserTableNames(database, "public");
   expect(tableNames).toContain("account");
@@ -146,7 +155,11 @@ test("migrate() throws with schema used", async (context) => {
       statements: buildSchema({ schema: { account } }).statements,
     },
   });
-  await database.migrate({ buildId: "abc", ordering: "multichain" });
+  await database.migrate({
+    buildId: "abc",
+    chains: [],
+    finalizedBlocks: [],
+  });
   await context.common.shutdown.kill();
 
   context.common.shutdown = createShutdown();
@@ -167,7 +180,11 @@ test("migrate() throws with schema used", async (context) => {
   });
 
   const error = await databaseTwo
-    .migrate({ buildId: "def", ordering: "multichain" })
+    .migrate({
+      buildId: "def",
+      chains: [],
+      finalizedBlocks: [],
+    })
     .catch((err) => err);
 
   expect(error).toBeDefined();
@@ -197,7 +214,11 @@ test("migrate() throws with schema used after waiting for lock", async (context)
       statements: buildSchema({ schema: { account } }).statements,
     },
   });
-  await database.migrate({ buildId: "abc", ordering: "multichain" });
+  await database.migrate({
+    buildId: "abc",
+    chains: [],
+    finalizedBlocks: [],
+  });
 
   const databaseTwo = await createDatabase({
     common: context.common,
@@ -215,7 +236,11 @@ test("migrate() throws with schema used after waiting for lock", async (context)
   });
 
   const error = await databaseTwo
-    .migrate({ buildId: "abc", ordering: "multichain" })
+    .migrate({
+      buildId: "abc",
+      chains: [],
+      finalizedBlocks: [],
+    })
     .catch((err) => err);
 
   expect(error).toBeDefined();
@@ -239,7 +264,11 @@ test("migrate() succeeds with crash recovery", async (context) => {
     },
   });
 
-  await database.migrate({ buildId: "abc", ordering: "multichain" });
+  await database.migrate({
+    buildId: "abc",
+    chains: [],
+    finalizedBlocks: [],
+  });
   await context.common.shutdown.kill();
 
   context.common.shutdown = createShutdown();
@@ -259,7 +288,11 @@ test("migrate() succeeds with crash recovery", async (context) => {
     },
   });
 
-  await databaseTwo.migrate({ buildId: "abc", ordering: "multichain" });
+  await databaseTwo.migrate({
+    buildId: "abc",
+    chains: [],
+    finalizedBlocks: [],
+  });
 
   const metadata = await databaseTwo.userQB.wrap((db) =>
     db.select().from(getPonderMetaTable("public")),
@@ -293,7 +326,11 @@ test("migrate() succeeds with crash recovery after waiting for lock", async (con
       statements: buildSchema({ schema: { account } }).statements,
     },
   });
-  await database.migrate({ buildId: "abc", ordering: "multichain" });
+  await database.migrate({
+    buildId: "abc",
+    chains: [],
+    finalizedBlocks: [],
+  });
 
   const databaseTwo = await createDatabase({
     common: context.common,
@@ -310,7 +347,11 @@ test("migrate() succeeds with crash recovery after waiting for lock", async (con
     },
   });
 
-  await databaseTwo.migrate({ buildId: "abc", ordering: "multichain" });
+  await databaseTwo.migrate({
+    buildId: "abc",
+    chains: [],
+    finalizedBlocks: [],
+  });
 
   await context.common.shutdown.kill();
 });
@@ -389,12 +430,14 @@ test("migrate() with crash recovery reverts rows", async (context) => {
     },
   });
 
-  await database.migrate({ buildId: "abc", ordering: "multichain" });
+  await database.migrate({
+    buildId: "abc",
+    chains: [],
+    finalizedBlocks: [],
+  });
 
   // setup tables, reorg tables, and metadata checkpoint
 
-  await createTriggers(database.userQB, { tables: [account] });
-
   await database.userQB.wrap((db) =>
     db.update(getPonderMetaTable("public")).set({
       value: sql`jsonb_set(value, '{is_ready}', to_jsonb(1))`,
@@ -417,6 +460,8 @@ test("migrate() with crash recovery reverts rows", async (context) => {
     table: account,
   });
 
+  await createTriggers(database.userQB, { tables: [account] });
+
   await indexingStore
     .insert(account)
     .values({ address: "0x0000000000000000000000000000000000000001" });
@@ -431,6 +476,7 @@ test("migrate() with crash recovery reverts rows", async (context) => {
       chainId: 1,
       chainName: "mainnet",
       latestCheckpoint: createCheckpoint({ chainId: 1n, blockNumber: 10n }),
+      finalizedCheckpoint: createCheckpoint({ chainId: 1n, blockNumber: 10n }),
       safeCheckpoint: createCheckpoint({ chainId: 1n, blockNumber: 10n }),
     }),
   );
@@ -456,7 +502,15 @@ test("migrate() with crash recovery reverts rows", async (context) => {
 
   const checkpoint = await databaseTwo.migrate({
     buildId: "abc",
-    ordering: "multichain",
+    chains: [getChain()],
+    finalizedBlocks: [
+      {
+        timestamp: "0x1",
+        number: "0xa",
+        hash: "0x",
+        parentHash: "0x",
+      },
+    ],
   });
 
   expect(checkpoint).toMatchInlineSnapshot(`
@@ -511,7 +565,11 @@ test("migrate() with crash recovery drops indexes and triggers", async (context)
     },
   });
 
-  await database.migrate({ buildId: "abc", ordering: "multichain" });
+  await database.migrate({
+    buildId: "abc",
+    chains: [],
+    finalizedBlocks: [],
+  });
 
   await createIndexes(database.userQB, {
     statements: buildSchema({ schema: { account } }).statements,
@@ -522,6 +580,7 @@ test("migrate() with crash recovery drops indexes and triggers", async (context)
       chainId: 1,
       chainName: "mainnet",
       latestCheckpoint: createCheckpoint({ chainId: 1n, blockNumber: 10n }),
+      finalizedCheckpoint: createCheckpoint({ chainId: 1n, blockNumber: 10n }),
       safeCheckpoint: createCheckpoint({ chainId: 1n, blockNumber: 10n }),
     }),
   );
@@ -551,7 +610,18 @@ test("migrate() with crash recovery drops indexes and triggers", async (context)
     },
   });
 
-  await databaseTwo.migrate({ buildId: "abc", ordering: "multichain" });
+  await databaseTwo.migrate({
+    buildId: "abc",
+    chains: [getChain()],
+    finalizedBlocks: [
+      {
+        timestamp: "0x1",
+        number: "0xa",
+        hash: "0x",
+        parentHash: "0x",
+      },
+    ],
+  });
 
   const indexNames = await getUserIndexNames(databaseTwo, "public", "account");
 
@@ -579,7 +649,11 @@ test("heartbeat updates the heartbeat_at value", async (context) => {
     },
   });
 
-  await database.migrate({ buildId: "abc", ordering: "multichain" });
+  await database.migrate({
+    buildId: "abc",
+    chains: [],
+    finalizedBlocks: [],
+  });
 
   const row = await database.userQB.wrap((db) =>
     db
```

### packages/core/src/database/index.ts
```diff
@@ -18,7 +18,7 @@ import type {
 } from "@/internal/types.js";
 import { buildMigrationProvider } from "@/sync-store/migrations.js";
 import * as PONDER_SYNC from "@/sync-store/schema.js";
-import { min } from "@/utils/checkpoint.js";
+import { decodeCheckpoint } from "@/utils/checkpoint.js";
 import { formatEta } from "@/utils/format.js";
 import { createPool, createReadonlyPool } from "@/utils/pg.js";
 import { createPglite, createPgliteKyselyDialect } from "@/utils/pglite.js";
@@ -32,7 +32,8 @@ import { drizzle as drizzlePglite } from "drizzle-orm/pglite";
 import { Kysely, Migrator, PostgresDialect, WithSchemaPlugin } from "kysely";
 import type { Pool, PoolClient } from "pg";
 import prometheus from "prom-client";
-import { revert } from "./actions.js";
+import { hexToBigInt } from "viem";
+import { crashRecovery } from "./actions.js";
 import { type QB, createQB, parseDbError } from "./queryBuilder.js";
 
 export type Database = {
@@ -50,10 +51,12 @@ export type Database = {
    */
   migrate({
     buildId,
-    ordering,
-  }: Pick<IndexingBuild, "buildId"> & {
-    ordering: "multichain" | "omnichain";
-  }): Promise<CrashRecoveryCheckpoint>;
+    chains,
+    finalizedBlocks,
+  }: Pick<
+    IndexingBuild,
+    "buildId" | "chains" | "finalizedBlocks"
+  >): Promise<CrashRecoveryCheckpoint>;
 };
 
 export const SCHEMATA = pgSchema("information_schema").table(
@@ -84,7 +87,7 @@ export type PonderApp = {
   heartbeat_at: number;
 };
 
-const VERSION = "3";
+const VERSION = "4";
 
 type PGliteDriver = {
   dialect: "pglite";
@@ -121,6 +124,7 @@ export const getPonderCheckpointTable = (schema?: string) => {
       chainId: t.bigint({ mode: "number" }).notNull(),
       safeCheckpoint: t.varchar({ length: 75 }).notNull(),
       latestCheckpoint: t.varchar({ length: 75 }).notNull(),
+      finalizedCheckpoint: t.varchar({ length: 75 }).notNull(),
     }));
   }
 
@@ -129,6 +133,7 @@ export const getPonderCheckpointTable = (schema?: string) => {
     chainId: t.bigint({ mode: "number" }).notNull(),
     safeCheckpoint: t.varchar({ length: 75 }).notNull(),
     latestCheckpoint: t.varchar({ length: 75 }).notNull(),
+    finalizedCheckpoint: t.varchar({ length: 75 }).notNull(),
   }));
 };
 
@@ -459,7 +464,7 @@ export const createDatabase = async ({
         }
       }
     },
-    async migrate({ buildId, ordering }) {
+    async migrate({ buildId, chains, finalizedBlocks }) {
       const createTables = async (tx: QB) => {
         for (let i = 0; i < schemaBuild.statements.tables.sql.length; i++) {
           await tx
@@ -511,7 +516,8 @@ CREATE TABLE IF NOT EXISTS "${namespace.schema}"."_ponder_checkpoint" (
   "chain_name" TEXT PRIMARY KEY,
   "chain_id" BIGINT NOT NULL,
   "safe_checkpoint" VARCHAR(75) NOT NULL,
-  "latest_checkpoint" VARCHAR(75) NOT NULL
+  "latest_checkpoint" VARCHAR(75) NOT NULL,
+  "finalized_checkpoint" VARCHAR(75) NOT NULL
 )`,
             ),
           );
@@ -673,13 +679,36 @@ EXECUTE PROCEDURE "${namespace.schema}".${notification};`,
           const checkpoints = await tx.wrap((tx) =>
             tx.select().from(PONDER_CHECKPOINT),
           );
-          const crashRecoveryCheckpoint =
-            checkpoints.length === 0
-              ? undefined
-              : checkpoints.map((c) => ({
-                  chainId: c.chainId,
-                  checkpoint: c.safeCheckpoint,
-                }));
+
+          // Note: The previous app can be in three possible states:
+          // 1. Has no checkpoints, hasn't made it past the setup events
+          // 2. Has checkpoints but hasn't made it past the historical backfill
+          // 3. Has checkpoints and has made it past the historical backfill
+
+          if (checkpoints.length === 0) {
+            return {
+              status: "success",
+              crashRecoveryCheckpoint: undefined,
+            } as const;
+          }
+
+          for (const { chainId, finalizedCheckpoint } of checkpoints) {
+            const finalizedBlock =
+              finalizedBlocks[chains.findIndex((c) => c.id === chainId)]!;
+            if (
+              hexToBigInt(finalizedBlock.timestamp) <
+              decodeCheckpoint(finalizedCheckpoint).blockTimestamp
+            ) {
+              throw new MigrationError(
+                `Finalized block for chain '${chainId}' cannot move backwards`,
+              );
+            }
+          }
+
+          const crashRecoveryCheckpoint = checkpoints.map((c) => ({
+            chainId: c.chainId,
+            checkpoint: c.safeCheckpoint,
+          }));
 
           if (previousApp.is_ready === 0) {
             await tx.wrap((tx) =>
@@ -712,12 +741,9 @@ EXECUTE PROCEDURE "${namespace.schema}".${notification};`,
             });
           }
 
-          // Note: it is an invariant that checkpoints.length > 0;
-          const revertCheckpoint = min(
-            ...checkpoints.map((c) => c.safeCheckpoint),
-          );
-
-          await revert(tx, { checkpoint: revertCheckpoint, tables, ordering });
+          for (const table of tables) {
+            await crashRecovery(tx, { table });
+          }
 
           // Note: We don't update the `_ponder_checkpoint` table here, instead we wait for it to be updated
           // in the runtime script.
```
