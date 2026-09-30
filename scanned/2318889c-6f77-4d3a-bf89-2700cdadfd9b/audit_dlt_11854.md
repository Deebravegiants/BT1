# [?] Fix versioning race condition (#508)

## Summary
Severity: Unknown
Chain: Indexer
Component: ponder-sh/ponder
Published: 2023-12-13
Source: https://github.com/ponder-sh/ponder/commit/a40e5e7ddb7efa3385c9fba2dd4ccac584cbf04b
Type: security-commit

## Details
Fix versioning race condition (#508)

* fix bug where ponder would fail if theres a contract with no indexing functions registered

* fix verioning race condition

## Patch
### packages/core/src/build/functions.ts
```diff
@@ -11,8 +11,12 @@ export function validateIndexingFunctions(rawIndexingFunctions: {
   for (const fileFns of Object.values(rawIndexingFunctions)) {
     for (const [eventKey, fn] of Object.entries(fileFns)) {
       const [sourceName, eventName] = eventKey.split(":");
-      if (!sourceName || !eventName)
-        throw new Error(`Invalid event name: ${eventKey}`);
+      if (!sourceName || !eventName) {
+        return {
+          indexingFunctions: null,
+          error: new Error(`Invalid event name: ${eventKey}`),
+        } as const;
+      }
 
       indexingFunctions[sourceName] ||= {};
 
```

### packages/core/src/indexing-store/postgres/store.ts
```diff
@@ -459,28 +459,26 @@ export class PostgresIndexingStore implements IndexingStore {
 
         // If the latest version has an earlier effectiveFromCheckpoint than the update,
         // we need to update the latest version AND insert a new version.
-        const [, row] = await Promise.all([
-          tx
-            .updateTable(table)
-            .where(
-              "id",
-              this.idColumnComparator({ tableName, schema: this.schema }),
-              formattedId,
-            )
-            .where("effectiveToCheckpoint", "=", "latest")
-            .set({ effectiveToCheckpoint: encodedCheckpoint })
-            .execute(),
-          tx
-            .insertInto(table)
-            .values({
-              ...latestRow,
-              ...updateRow,
-              effectiveFromCheckpoint: encodedCheckpoint,
-              effectiveToCheckpoint: "latest",
-            })
-            .returningAll()
-            .executeTakeFirstOrThrow(),
-        ]);
+        await tx
+          .updateTable(table)
+          .where(
+            "id",
+            this.idColumnComparator({ tableName, schema: this.schema }),
+            formattedId,
+          )
+          .where("effectiveToCheckpoint", "=", "latest")
+          .set({ effectiveToCheckpoint: encodedCheckpoint })
+          .execute();
+        const row = await tx
+          .insertInto(table)
+          .values({
+            ...latestRow,
+            ...updateRow,
+            effectiveFromCheckpoint: encodedCheckpoint,
+            effectiveToCheckpoint: "latest",
+          })
+          .returningAll()
+          .executeTakeFirstOrThrow();
 
         return row;
       });
@@ -569,28 +567,26 @@ export class PostgresIndexingStore implements IndexingStore {
 
             // If the latest version has an earlier effectiveFromCheckpoint than the update,
             // we need to update the latest version AND insert a new version.
-            const [, row] = await Promise.all([
-              tx
-                .updateTable(table)
-                .where(
-                  "id",
-                  this.idColumnComparator({ tableName, schema: this.schema }),
-                  formattedId,
-                )
-                .where("effectiveToCheckpoint", "=", "latest")
-                .set({ effectiveToCheckpoint: encodedCheckpoint })
-                .execute(),
-              tx
-                .insertInto(table)
-                .values({
-                  ...latestRow,
-                  ...updateRow,
-                  effectiveFromCheckpoint: encodedCheckpoint,
-                  effectiveToCheckpoint: "latest",
-                })
-                .returningAll()
-                .executeTakeFirstOrThrow(),
-            ]);
+            await tx
+              .updateTable(table)
+              .where(
+                "id",
+                this.idColumnComparator({ tableName, schema: this.schema }),
+                formattedId,
+              )
+              .where("effectiveToCheckpoint", "=", "latest")
+              .set({ effectiveToCheckpoint: encodedCheckpoint })
+              .execute();
+            const row = await tx
+              .insertInto(table)
+              .values({
+                ...latestRow,
+                ...updateRow,
+                effectiveFromCheckpoint: encodedCheckpoint,
+                effectiveToCheckpoint: "latest",
+              })
+              .returningAll()
+              .executeTakeFirstOrThrow();
 
             return row;
           }),
@@ -685,28 +681,26 @@ export class PostgresIndexingStore implements IndexingStore {
 
         // If the latest version has an earlier effectiveFromCheckpoint than the update,
         // we need to update the latest version AND insert a new version.
-        const [, row] = await Promise.all([
-          tx
-            .updateTable(table)
-            .where(
-              "id",
-              this.idColumnComparator({ tableName, schema: this.schema }),
-              formattedId,
-            )
-            .where("effectiveToCheckpoint", "=", "latest")
-            .set({ effectiveToCheckpoint: encodedCheckpoint })
-            .execute(),
-          tx
-            .insertInto(table)
-            .values({
-              ...latestRow,
-              ...updateRow,
-              effectiveFromCheckpoint: encodedCheckpoint,
-              effectiveToCheckpoint: "latest",
-            })
-            .returningAll()
-            .executeTakeFirstOrThrow(),
-        ]);
+        await tx
+          .updateTable(table)
+          .where(
+            "id",
+            this.idColumnComparator({ tableName, schema: this.schema }),
+            formattedId,
+          )
+          .where("effectiveToCheckpoint", "=", "latest")
+          .set({ effectiveToCheckpoint: encodedCheckpoint })
+          .execute();
+        const row = await tx
+          .insertInto(table)
+          .values({
+            ...latestRow,
+            ...updateRow,
+            effectiveFromCheckpoint: encodedCheckpoint,
+            effectiveToCheckpoint: "latest",
+          })
+          .returningAll()
+          .executeTakeFirstOrThrow();
 
         return row;
       });
```

### packages/core/src/indexing-store/sqlite/store.ts
```diff
@@ -439,28 +439,26 @@ export class SqliteIndexingStore implements IndexingStore {
 
         // If the latest version has an earlier effectiveFromCheckpoint than the update,
         // we need to update the latest version AND insert a new version.
-        const [, row] = await Promise.all([
-          tx
-            .updateTable(table)
-            .where(
-              "id",
-              this.idColumnComparator({ tableName, schema: this.schema }),
-              formattedId,
-            )
-            .where("effectiveToCheckpoint", "=", "latest")
-            .set({ effectiveToCheckpoint: encodedCheckpoint })
-            .execute(),
-          tx
-            .insertInto(table)
-            .values({
-              ...latestRow,
-              ...updateRow,
-              effectiveFromCheckpoint: encodedCheckpoint,
-              effectiveToCheckpoint: "latest",
-            })
-            .returningAll()
-            .executeTakeFirstOrThrow(),
-        ]);
+        await tx
+          .updateTable(table)
+          .where(
+            "id",
+            this.idColumnComparator({ tableName, schema: this.schema }),
+            formattedId,
+          )
+          .where("effectiveToCheckpoint", "=", "latest")
+          .set({ effectiveToCheckpoint: encodedCheckpoint })
+          .execute();
+        const row = tx
+          .insertInto(table)
+          .values({
+            ...latestRow,
+            ...updateRow,
+            effectiveFromCheckpoint: encodedCheckpoint,
+            effectiveToCheckpoint: "latest",
+          })
+          .returningAll()
+          .executeTakeFirstOrThrow();
 
         return row;
       });
@@ -549,28 +547,26 @@ export class SqliteIndexingStore implements IndexingStore {
 
             // If the latest version has an earlier effectiveFromCheckpoint than the update,
             // we need to update the latest version AND insert a new version.
-            const [, row] = await Promise.all([
-              tx
-                .updateTable(table)
-                .where(
-                  "id",
-                  this.idColumnComparator({ tableName, schema: this.schema }),
-                  formattedId,
-                )
-                .where("effectiveToCheckpoint", "=", "latest")
-                .set({ effectiveToCheckpoint: encodedCheckpoint })
-                .execute(),
-              tx
-                .insertInto(table)
-                .values({
-                  ...latestRow,
-                  ...updateRow,
-                  effectiveFromCheckpoint: encodedCheckpoint,
-                  effectiveToCheckpoint: "latest",
-                })
-                .returningAll()
-                .executeTakeFirstOrThrow(),
-            ]);
+            await tx
+              .updateTable(table)
+              .where(
+                "id",
+                this.idColumnComparator({ tableName, schema: this.schema }),
+                formattedId,
+              )
+              .where("effectiveToCheckpoint", "=", "latest")
+              .set({ effectiveToCheckpoint: encodedCheckpoint })
+              .execute();
+            const row = tx
+              .insertInto(table)
+              .values({
+                ...latestRow,
+                ...updateRow,
+                effectiveFromCheckpoint: encodedCheckpoint,
+                effectiveToCheckpoint: "latest",
+              })
+              .returningAll()
+              .executeTakeFirstOrThrow();
 
             return row;
           }),
@@ -665,28 +661,26 @@ export class SqliteIndexingStore implements IndexingStore {
 
         // If the latest version has an earlier effectiveFromCheckpoint than the update,
         // we need to update the latest version AND insert a new version.
-        const [, row] = await Promise.all([
-          tx
-            .updateTable(table)
-            .where(
-              "id",
-              this.idColumnComparator({ tableName, schema: this.schema }),
-              formattedId,
-            )
-            .where("effectiveToCheckpoint", "=", "latest")
-            .set({ effectiveToCheckpoint: encodedCheckpoint })
-            .execute(),
-          tx
-            .insertInto(table)
-            .values({
-              ...latestRow,
-              ...updateRow,
-              effectiveFromCheckpoint: encodedCheckpoint,
-              effectiveToCheckpoint: "latest",
-            })
-            .returningAll()
-            .executeTakeFirstOrThrow(),
-        ]);
+        await tx
+          .updateTable(table)
+          .where(
+            "id",
+            this.idColumnComparator({ tableName, schema: this.schema }),
+            formattedId,
+          )
+          .where("effectiveToCheckpoint", "=", "latest")
+          .set({ effectiveToCheckpoint: encodedCheckpoint })
+          .execute();
+        const row = tx
+          .insertInto(table)
+          .values({
+            ...latestRow,
+            ...updateRow,
+            effectiveFromCheckpoint: encodedCheckpoint,
+            effectiveToCheckpoint: "latest",
+          })
+          .returningAll()
+          .executeTakeFirstOrThrow();
 
         return row;
       });
```

### packages/core/src/indexing/service.ts
```diff
@@ -333,18 +333,26 @@ export class IndexingService extends Emittery<IndexingEvents> {
         const registeredSelectorsBySourceId: { [sourceId: string]: Hex[] } = {};
         for (const source of this.sources) {
           sourcesById[source.id] = source;
-          registeredSelectorsBySourceId[source.id] = Object.keys(
-            this.indexingFunctions![source.contractName],
-          )
-            .filter((name) => name !== "setup")
-            .map((safeEventName) => {
-              const abiItemMeta = source.events.bySafeName[safeEventName];
-              if (!abiItemMeta)
-                throw new Error(
-                  `Invariant violation: No abiItemMeta found for ${source.contractName}:${safeEventName}`,
-                );
-              return abiItemMeta.selector;
-            });
+
+          const indexingFunctions =
+            this.indexingFunctions![source.contractName];
+          if (indexingFunctions) {
+            registeredSelectorsBySourceId[source.id] = Object.keys(
+              indexingFunctions,
+            )
+              .filter((name) => name !== "setup")
+              .map((safeEventName) => {
+                const abiItemMeta = source.events.bySafeName[safeEventName];
+                if (!abiItemMeta)
+                  throw new Error(
+                    `Invariant violation: No abiItemMeta found for ${source.contractName}:${safeEventName}`,
+                  );
+                return abiItemMeta.selector;
+              });
+          } else {
+            // It's possible for no indexing functions to be registered for a source.
+            registeredSelectorsBySourceId[source.id] = [];
+          }
         }
 
         const iterator = this.syncGatewayService.getEvents({
```
