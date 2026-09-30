# [?] Fix crash when setting entity with omitted nullable FK after getWhere (#1208)

## Summary
Severity: Unknown
Chain: Indexer
Component: enviodev/hyperindex
Published: 2026-05-15
Source: https://github.com/enviodev/hyperindex/commit/9a278ca44253cc073946bf6ef2e74973a57bbe3f
Type: security-commit

## Details
Fix crash when setting entity with omitted nullable FK after getWhere (#1208)

* test: reproduce UndefinedKey crash on nullable indexed FK set

Adds a failing TestIndexer case where a handler runs
`context.User.getWhere({ gravatar_id: { _eq: ... } })` and then
`context.User.set({ ..., gravatar_id: undefined })`. The getWhere
registers an InMemoryTable index keyed by `gravatar_id`, and the
following set crashes inside `updateIndices` with
`UndefinedKey("gravatar_id")` because the entity object simply omits
the FK key.

PgStorage stores the column as NULL, so the bug only surfaces on the
in-memory path that getWhere installs.

https://claude.ai/code/session_01EGs1UWHZJ1xvP2wo9uiRbA

* fix(in-memory-table): tolerate missing nullable FK field on set

InMemoryTable.Entity.updateIndices threw UndefinedKey when a `getWhere`
had registered an index on a nullable FK column (e.g. `optionalEntity_id`
for `optionalEntity: OptionalEntity @index`) and a later set on the same
entity table omitted the key. PgStorage stores the column as NULL in
that case, so the bug only surfaced for handlers that mix getWhere with
sets that don't set the FK.

Match the existing `addEmptyIndex` semantics: read the field with
`Dict.getUnsafe` so a missing key flows through as `None` for
`FieldValue.t = option<...>` and the equality/range operators reject
the entity instead of crashing.

https://claude.ai/code/session_01EGs1UWHZJ1xvP2wo9uiRbA

---------

Co-authored-by: Claude <noreply@anthropic.com>

## Patch
### packages/envio/src/InMemoryTable.res
```diff
@@ -71,7 +71,6 @@ module Entity = {
     fieldNameIndices: make(~hash=TableIndices.Index.getFieldName),
   }
 
-  exception UndefinedKey(string)
   let updateIndices = (
     self: t<'entity>,
     ~entity: 'entity,
@@ -83,8 +82,7 @@ module Entity = {
       let fieldValue =
         entity
         ->(Utils.magic: 'entity => dict<TableIndices.FieldValue.t>)
-        ->Dict.get(fieldName)
-        ->Option.getUnsafe
+        ->Dict.getUnsafe(fieldName)
       if !(index->TableIndices.Index.evaluate(~fieldName, ~fieldValue)) {
         entityIndices->Utils.Set.delete(index)->ignore
       }
@@ -93,27 +91,25 @@ module Entity = {
     self.fieldNameIndices.dict
     ->Dict.keysToArray
     ->Array.forEach(fieldName => {
-      switch (
-        entity->(Utils.magic: 'entity => dict<TableIndices.FieldValue.t>)->Dict.get(fieldName),
-        self.fieldNameIndices.dict->Dict.get(fieldName),
-      ) {
-      | (Some(fieldValue), Some(indices)) =>
-        indices
-        ->values
-        ->Array.forEach(((index, relatedEntityIds)) => {
-          if index->TableIndices.Index.evaluate(~fieldName, ~fieldValue) {
-            //Add entity id to indices and add index to entity indicies
-            relatedEntityIds->Utils.Set.add(getEntityIdUnsafe(entity))->ignore
-            entityIndices->Utils.Set.add(index)->ignore
-          } else {
-            relatedEntityIds->Utils.Set.delete(getEntityIdUnsafe(entity))->ignore
-          }
-        })
-      | _ =>
-        UndefinedKey(fieldName)->ErrorHandling.mkLogAndRaise(
-          ~msg="Expected field name to exist on the referenced index and the provided entity",
-        )
-      }
+      let indices = self.fieldNameIndices.dict->Dict.getUnsafe(fieldName)
+      // A missing key reads as `undefined`, which matches the `None` arm of
+      // `FieldValue.t` (`option<...>`). Mirror `addEmptyIndex` so nullable
+      // FK columns that were omitted on the set entity don't crash.
+      let fieldValue =
+        entity
+        ->(Utils.magic: 'entity => dict<TableIndices.FieldValue.t>)
+        ->Dict.getUnsafe(fieldName)
+      indices
+      ->values
+      ->Array.forEach(((index, relatedEntityIds)) => {
+        if index->TableIndices.Index.evaluate(~fieldName, ~fieldValue) {
+          //Add entity id to indices and add index to entity indicies
+          relatedEntityIds->Utils.Set.add(getEntityIdUnsafe(entity))->ignore
+          entityIndices->Utils.Set.add(index)->ignore
+        } else {
+          relatedEntityIds->Utils.Set.delete(getEntityIdUnsafe(entity))->ignore
+        }
+      })
     })
   }
 
```

### scenarios/test_codegen/src/handlers/EventHandlers.ts
```diff
@@ -807,6 +807,27 @@ indexer.onEvent({ contract: "Gravatar", event: "FactoryEvent" }, async ({ event,
       });
       break;
     }
+
+    // getWhere on a nullable linkedEntity column registers an InMemoryTable
+    // index for that field. A subsequent set whose entity omits the FK key
+    // (the common shape for nullable relations) used to crash inside
+    // updateIndices with `UndefinedKey("gravatar_id")`.
+    case "getWhereThenSetNullableFk": {
+      await context.User.getWhere({
+        gravatar_id: { _eq: "non-existent-gravatar" },
+      });
+      context.User.set({
+        id: "user-with-null-gravatar",
+        address: "0x1111111111111111111111111111111111111111",
+        updatesCountOnUserForTesting: 0,
+        gravatar_id: undefined,
+        accountType: "USER",
+      });
+      context.CustomSelectionTestPass.set({
+        id: "getWhereThenSetNullableFk:ok",
+      });
+      break;
+    }
   }
 });
 
```

### scenarios/test_codegen/test/EventHandler.test.ts
```diff
@@ -648,6 +648,51 @@ describe("Use Envio test framework to test event handlers", () => {
     });
   });
 
+  // Regression: a `getWhere` on a nullable linkedEntity column (db column
+  // `<field>_id`) registers an in-memory index keyed by that column name.
+  // The next `set` of an entity whose JS object simply omits the FK (the
+  // natural shape for `nullableField === undefined`) used to throw
+  // `UndefinedKey("gravatar_id")` deep inside InMemoryTable.updateIndices.
+  // PgStorage stores the column as NULL, so the bug only surfaced for
+  // handlers that mix the two operations on the same entity table.
+  it("getWhere followed by set with omitted nullable FK does not crash", async () => {
+    const indexer = createTestIndexer();
+
+    const result = await indexer.process({
+      chains: {
+        1337: {
+          startBlock: 1,
+          endBlock: 100,
+          simulate: [
+            {
+              contract: "Gravatar",
+              event: "FactoryEvent",
+              params: {
+                contract: "0x1234567890123456789012345678901234567890",
+                testCase: "getWhereThenSetNullableFk",
+              },
+            },
+          ],
+        },
+      },
+    });
+
+    assert.deepEqual(result.changes[0]?.User, {
+      sets: [
+        {
+          id: "user-with-null-gravatar",
+          address: "0x1111111111111111111111111111111111111111",
+          updatesCountOnUserForTesting: 0,
+          gravatar_id: undefined,
+          accountType: "USER",
+        },
+      ],
+    });
+    assert.deepEqual(result.changes[0]?.CustomSelectionTestPass, {
+      sets: [{ id: "getWhereThenSetNullableFk:ok" }],
+    });
+  });
+
   it("Throws when contract registered with invalid address", async () => {
     const indexer = createTestIndexer();
 
```
