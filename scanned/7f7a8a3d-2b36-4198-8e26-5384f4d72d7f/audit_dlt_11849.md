# [?] fix crash recovery (#1330)

## Summary
Severity: Unknown
Chain: Indexer
Component: ponder-sh/ponder
Published: 2024-12-11
Source: https://github.com/ponder-sh/ponder/commit/0c7395ff2e86ac9f6431e4d702965e2036c35d64
Type: security-commit

## Details
fix crash recovery (#1330)

* fix crash recovery

* drop enums

## Patch
### .changeset/sour-yaks-melt.md
```diff
@@ -0,0 +1,5 @@
+---
+"ponder": patch
+---
+
+Fixed a bug with crash recovery.
```

### packages/core/src/database/index.test.ts
```diff
@@ -87,7 +87,7 @@ test("setup() throws with schema used", async (context) => {
     },
   });
 
-  const error = await databaseTwo.setup({ buildId: "abc" }).catch((err) => err);
+  const error = await databaseTwo.setup({ buildId: "def" }).catch((err) => err);
 
   expect(error).toBeDefined();
 
```

### packages/core/src/database/index.ts
```diff
@@ -672,20 +672,7 @@ export const createDatabase = ({
               ),
             } satisfies PonderApp;
 
-            // If schema is empty, create tables
-            if (previousApp === undefined) {
-              await tx
-                .insertInto("_ponder_meta")
-                .values({ key: "status", value: null })
-                .execute();
-              await tx
-                .insertInto("_ponder_meta")
-                .values({
-                  key: "app",
-                  value: newApp,
-                })
-                .execute();
-
+            const createEnums = async () => {
               for (
                 let i = 0;
                 i < schemaBuild.statements.enums.sql.length;
@@ -704,6 +691,9 @@ export const createDatabase = ({
                     throw e;
                   });
               }
+            };
+
+            const createTables = async () => {
               for (
                 let i = 0;
                 i < schemaBuild.statements.tables.sql.length;
@@ -722,6 +712,47 @@ export const createDatabase = ({
                     throw e;
                   });
               }
+            };
+
+            const dropTables = async () => {
+              for (const tableName of getTableNames(schemaBuild.schema)) {
+                await tx.schema
+                  .dropTable(tableName.sql)
+                  .cascade()
+                  .ifExists()
+                  .execute();
+                await tx.schema
+                  .dropTable(tableName.reorg)
+                  .cascade()
+                  .ifExists()
+                  .execute();
+              }
+            };
+
+            const dropEnums = async () => {
+              for (const enumName of schemaBuild.statements.enums.json) {
+                await tx.schema.dropType(enumName.name).ifExists().execute();
+              }
+            };
+
+            // If schema is empty, create tables
+            // If schema is empty, create tables
+            if (previousApp === undefined) {
+              await tx
+                .insertInto("_ponder_meta")
+                .values({ key: "status", value: null })
+                .execute();
+              await tx
+                .insertInto("_ponder_meta")
+                .values({
+                  key: "app",
+                  value: newApp,
+                })
+                .execute();
+
+              await createEnums();
+              await createTables();
+
               common.logger.info({
                 service: "database",
                 msg: `Created tables [${newApp.table_names.join(", ")}]`,
@@ -748,61 +779,16 @@ export const createDatabase = ({
                 .execute();
               await tx
                 .updateTable("_ponder_meta")
-                .set({
-                  value: newApp,
-                })
+                .set({ value: newApp })
                 .where("key", "=", "app")
                 .execute();
 
-              for (const tableName of getTableNames(schemaBuild.schema)) {
-                await tx.schema
-                  .dropTable(tableName.sql)
-                  .cascade()
-                  .ifExists()
-                  .execute();
-                await tx.schema
-                  .dropTable(tableName.reorg)
-                  .cascade()
-                  .ifExists()
-                  .execute();
-              }
+              await dropTables();
+              await dropEnums();
+
+              await createEnums();
+              await createTables();
 
-              for (
-                let i = 0;
-                i < schemaBuild.statements.enums.sql.length;
-                i++
-              ) {
-                await sql
-                  .raw(schemaBuild.statements.enums.sql[i]!)
-                  .execute(tx)
-                  .catch((_error) => {
-                    const error = _error as Error;
-                    if (!error.message.includes("already exists")) throw error;
-                    const e = new NonRetryableError(
-                      `Unable to create enum '${preBuild.namespace}'.'${schemaBuild.statements.enums.json[i]!.name}' because an enum with that name already exists.`,
-                    );
-                    e.stack = undefined;
-                    throw e;
-                  });
-              }
-              for (
-                let i = 0;
-                i < schemaBuild.statements.tables.sql.length;
-                i++
-              ) {
-                await sql
-                  .raw(schemaBuild.statements.tables.sql[i]!)
-                  .execute(tx)
-                  .catch((_error) => {
-                    const error = _error as Error;
-                    if (!error.message.includes("already exists")) throw error;
-                    const e = new NonRetryableError(
-                      `Unable to create table '${preBuild.namespace}'.'${schemaBuild.statements.tables.json[i]!.tableName}' because a table with that name already exists.`,
-                    );
-                    e.stack = undefined;
-                    throw e;
-                  });
-              }
               common.logger.info({
                 service: "database",
                 msg: `Created tables [${newApp.table_names.join(", ")}]`,
@@ -817,8 +803,7 @@ export const createDatabase = ({
             // If crash recovery is not possible, error
             if (
               common.options.command === "dev" ||
-              previousApp.build_id !== newApp.build_id ||
-              previousApp.checkpoint === encodeCheckpoint(zeroCheckpoint)
+              previousApp.build_id !== newApp.build_id
             ) {
               const error = new NonRetryableError(
                 `Schema '${preBuild.namespace}' was previously used by a different Ponder app. Drop the schema first, or use a different schema. Read more: https://ponder.sh/docs/getting-started/database#database-schema`,
@@ -845,6 +830,35 @@ export const createDatabase = ({
 
             // Crash recovery is possible, recover
 
+            if (previousApp.checkpoint === encodeCheckpoint(zeroCheckpoint)) {
+              await tx
+                .updateTable("_ponder_meta")
+                .set({ value: null })
+                .where("key", "=", "status")
+                .execute();
+              await tx
+                .updateTable("_ponder_meta")
+                .set({ value: newApp })
+                .where("key", "=", "app")
+                .execute();
+
+              await dropTables();
+              await dropEnums();
+
+              await createEnums();
+              await createTables();
+
+              common.logger.info({
+                service: "database",
+                msg: `Created tables [${newApp.table_names.join(", ")}]`,
+              });
+
+              return {
+                status: "success",
+                checkpoint: encodeCheckpoint(zeroCheckpoint),
+              } as const;
+            }
+
             const checkpoint = previousApp.checkpoint;
             newApp.checkpoint = checkpoint;
 
@@ -855,9 +869,7 @@ export const createDatabase = ({
               .execute();
             await tx
               .updateTable("_ponder_meta")
-              .set({
-                value: newApp,
-              })
+              .set({ value: newApp })
               .where("key", "=", "app")
               .execute();
 
```
