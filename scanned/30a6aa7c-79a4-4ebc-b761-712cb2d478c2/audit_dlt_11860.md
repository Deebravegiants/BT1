# [?] Configure hasura in single bulk request - attempt to fix a race condition (#770)

## Summary
Severity: Unknown
Chain: Indexer
Component: enviodev/hyperindex
Published: 2025-10-02
Source: https://github.com/enviodev/hyperindex/commit/fd3fad7f4d0eb871df39538216f912d7cc9e7e11
Type: security-commit

## Details
Configure hasura in single bulk request - attempt to fix a race condition (#770)

* Fix is progress at head metric

* Fix test compilation

* Configure hasura using single bulk request

## Patch
### codegenerator/cli/npm/envio/src/Hasura.res
```diff
@@ -71,12 +71,43 @@ let rawBodyRoute = Rest.route(() => {
   responses,
 })
 
+let bulkKeepGoingRoute = Rest.route(() => {
+  method: Post,
+  path: "",
+  input: s => {
+    let _ = s.field("type", S.literal("bulk_keep_going"))
+    {
+      "args": s.field("args", S.json(~validate=false)),
+      "auth": s->auth,
+    }
+  },
+  responses: [
+    (s: Rest.Response.s) => {
+      s.status(200)
+      s.data(S.json(~validate=false))
+    },
+  ],
+})
+let bulkKeepGoingErrorsSchema = S.array(
+  S.union([
+    S.object(s => {
+      s.tag("message", "success")
+      None
+    }),
+    S.object(s => {
+      Some(s.field("error", S.string))
+    }),
+  ]),
+)->S.transform(_ => {
+  parser: a => Belt.Array.keepMapU(a, a => a),
+})
+
 let clearHasuraMetadata = async (~endpoint, ~auth) => {
   try {
     let result = await clearMetadataRoute->Rest.fetch(auth, ~client=Rest.client(endpoint))
     let msg = switch result {
-    | QuerySucceeded => "Metadata Cleared"
-    | AlreadyDone => "Metadata Already Cleared"
+    | QuerySucceeded => "Hasura metadata cleared"
+    | AlreadyDone => "Hasura metadata already cleared"
     }
     Logging.trace(msg)
   } catch {
@@ -113,8 +144,8 @@ let trackTables = async (~endpoint, ~auth, ~pgSchema, ~tableNames: array<string>
       ~client=Rest.client(endpoint),
     )
     let msg = switch result {
-    | QuerySucceeded => "Tables Tracked"
-    | AlreadyDone => "Table Already Tracked"
+    | QuerySucceeded => "Hasura finished tracking tables"
+    | AlreadyDone => "Hasura tables already tracked"
     }
     Logging.trace({
       "msg": msg,
@@ -130,91 +161,110 @@ let trackTables = async (~endpoint, ~auth, ~pgSchema, ~tableNames: array<string>
   }
 }
 
-let createSelectPermissions = async (
-  ~auth,
-  ~endpoint,
+type bulkOperation = {
+  \"type": string,
+  args: Js.Json.t,
+}
+
+let createSelectPermissionOperation = (
   ~tableName: string,
   ~pgSchema,
   ~responseLimit,
   ~aggregateEntities,
-) => {
-  try {
-    let result = await createSelectPermissionRoute->Rest.fetch(
-      {
-        "auth": auth,
-        "args": {
-          "table": {
-            "schema": pgSchema,
-            "name": tableName,
-          },
-          "role": "public",
-          "source": "default",
-          "permission": {
-            "columns": "*",
-            "filter": Js.Obj.empty(),
-            "limit": responseLimit,
-            "allow_aggregations": aggregateEntities->Js.Array2.includes(tableName),
-          },
-        }->(Utils.magic: 'a => Js.Json.t),
+): bulkOperation => {
+  {
+    \"type": "pg_create_select_permission",
+    args: {
+      "table": {
+        "schema": pgSchema,
+        "name": tableName,
       },
-      ~client=Rest.client(endpoint),
-    )
-    let msg = switch result {
-    | QuerySucceeded => "Hasura select permissions created"
-    | AlreadyDone => "Hasura select permissions already created"
-    }
-    Logging.trace({
-      "msg": msg,
-      "tableName": tableName,
-    })
-  } catch {
-  | exn =>
-    Logging.error({
-      "msg": `EE808: There was an issue setting up view permissions for the ${tableName} table in hasura - indexing may still work - but you may have issues querying the data in hasura.`,
-      "tableName": tableName,
-      "err": exn->Utils.prettifyExn,
-    })
+      "role": "public",
+      "source": "default",
+      "permission": {
+        "columns": "*",
+        "filter": Js.Obj.empty(),
+        "limit": responseLimit,
+        "allow_aggregations": aggregateEntities->Js.Array2.includes(tableName),
+      },
+    }->(Utils.magic: 'a => Js.Json.t),
   }
 }
 
-let createEntityRelationship = async (
+let createEntityRelationshipOperation = (
   ~pgSchema,
-  ~endpoint,
-  ~auth,
   ~tableName: string,
   ~relationshipType: string,
   ~relationalKey: string,
   ~objectName: string,
   ~mappedEntity: string,
   ~isDerivedFrom: bool,
-) => {
+): bulkOperation => {
   let derivedFromTo = isDerivedFrom ? `"id": "${relationalKey}"` : `"${relationalKey}_id" : "id"`
 
-  let bodyString = `{"type": "pg_create_${relationshipType}_relationship","args": {"table": {"schema": "${pgSchema}", "name": "${tableName}"},"name": "${objectName}","source": "default","using": {"manual_configuration": {"remote_table": {"schema": "${pgSchema}", "name": "${mappedEntity}"},"column_mapping": {${derivedFromTo}}}}}}`
-
-  try {
-    let result = await rawBodyRoute->Rest.fetch(
-      {
-        "auth": auth,
-        "bodyString": bodyString,
+  {
+    \"type": `pg_create_${relationshipType}_relationship`,
+    args: {
+      "table": {
+        "schema": pgSchema,
+        "name": tableName,
       },
-      ~client=Rest.client(endpoint),
-    )
-    let msg = switch result {
-    | QuerySucceeded => `Hasura ${relationshipType} relationship created`
-    | AlreadyDone => `Hasura ${relationshipType} relationship already created`
+      "name": objectName,
+      "source": "default",
+      "using": {
+        "manual_configuration": {
+          "remote_table": {
+            "schema": pgSchema,
+            "name": mappedEntity,
+          },
+          "column_mapping": Js.Json.parseExn(`{${derivedFromTo}}`),
+        },
+      },
+    }->(Utils.magic: 'a => Js.Json.t),
+  }
+}
+
+let executeBulkKeepGoing = async (~endpoint, ~auth, ~operations: array<bulkOperation>) => {
+  if operations->Js.Array2.length === 0 {
+    Logging.trace("No hasura bulk configuration operations to execute")
+  } else {
+    try {
+      let result = await bulkKeepGoingRoute->Rest.fetch(
+        {
+          "auth": auth,
+          "args": operations->(Utils.magic: 'a => Js.Json.t),
+        },
+        ~client=Rest.client(endpoint),
+      )
+
+      let errors = try {
+        result->S.parseJsonOrThrow(bulkKeepGoingErrorsSchema)
+      } catch {
+      | S.Raised(error) => [error->S.Error.message]
+      | exn => [exn->Utils.prettifyExn->Utils.magic]
+      }
+
+      switch errors {
+      | [] =>
+        Logging.trace({
+          "msg": "Hasura configuration completed",
+          "operations": operations->Js.Array2.length,
+        })
+      | _ =>
+        Logging.warn({
+          "msg": "Hasura configuration completed with errors. Indexing will still work - but you may have issues querying data via GraphQL.",
+          "errors": errors,
+          "operations": operations->Js.Array2.length,
+        })
+      }
+    } catch {
+    | exn =>
+      Logging.error({
+        "msg": `EE809: There was an issue executing bulk operations in hasura - indexing may still work - but you may have issues querying the data in hasura.`,
+        "operations": operations->Js.Array2.length,
+        "err": exn->Utils.prettifyExn,
+      })
     }
-    Logging.trace({
-      "msg": msg,
-      "tableName": tableName,
-    })
-  } catch {
-  | exn =>
-    Logging.error({
-      "msg": `EE808: There was an issue setting up ${relationshipType} relationship for the ${tableName} table in hasura - indexing may still work - but you may have issues querying the data in hasura.`,
-      "tableName": tableName,
-      "err": exn->Utils.prettifyExn,
-    })
   }
 }
 
@@ -241,60 +291,64 @@ let trackDatabase = async (
 
   await trackTables(~endpoint, ~auth, ~pgSchema, ~tableNames)
 
-  let _ =
-    await tableNames
-    ->Js.Array2.map(tableName =>
-      createSelectPermissions(
-        ~endpoint,
-        ~auth,
-        ~tableName,
-        ~pgSchema,
-        ~responseLimit,
-        ~aggregateEntities,
-      )
-    )
-    ->Js.Array2.concatMany(
-      userEntities->Js.Array2.map(entityConfig => {
-        let {tableName} = entityConfig.table
-        [
-          //Set array relationships
-          entityConfig.table
-          ->Table.getDerivedFromFields
-          ->Js.Array2.map(derivedFromField => {
-            //determines the actual name of the underlying relational field (if it's an entity mapping then suffixes _id for eg.)
-            let relationalFieldName =
-              schema->Schema.getDerivedFromFieldName(derivedFromField)->Utils.unwrapResultExn
+  // Collect all operations for bulk execution
+  let allOperations = []
 
-            createEntityRelationship(
-              ~endpoint,
-              ~auth,
-              ~pgSchema,
-              ~tableName,
-              ~relationshipType="array",
-              ~isDerivedFrom=true,
-              ~objectName=derivedFromField.fieldName,
-              ~relationalKey=relationalFieldName,
-              ~mappedEntity=derivedFromField.derivedFromEntity,
-            )
-          }),
-          //Set object relationships
-          entityConfig.table
-          ->Table.getLinkedEntityFields
-          ->Js.Array2.map(((field, linkedEntityName)) => {
-            createEntityRelationship(
-              ~endpoint,
-              ~auth,
-              ~pgSchema,
-              ~tableName,
-              ~relationshipType="object",
-              ~isDerivedFrom=false,
-              ~objectName=field.fieldName,
-              ~relationalKey=field.fieldName,
-              ~mappedEntity=linkedEntityName,
-            )
-          }),
-        ]->Utils.Array.flatten
-      }),
+  // Add select permission operations
+  tableNames->Js.Array2.forEach(tableName => {
+    allOperations
+    ->Js.Array2.push(
+      createSelectPermissionOperation(~tableName, ~pgSchema, ~responseLimit, ~aggregateEntities),
     )
-    ->Promise.all
+    ->ignore
+  })
+
+  // Add relationship operations
+  userEntities->Js.Array2.forEach(entityConfig => {
+    let {tableName} = entityConfig.table
+
+    //Set array relationships
+    entityConfig.table
+    ->Table.getDerivedFromFields
+    ->Js.Array2.forEach(derivedFromField => {
+      //determines the actual name of the underlying relational field (if it's an entity mapping then suffixes _id for eg.)
+      let relationalFieldName =
+        schema->Schema.getDerivedFromFieldName(derivedFromField)->Utils.unwrapResultExn
+
+      allOperations
+      ->Js.Array2.push(
+        createEntityRelationshipOperation(
+          ~pgSchema,
+          ~tableName,
+          ~relationshipType="array",
+          ~isDerivedFrom=true,
+          ~objectName=derivedFromField.fieldName,
+          ~relationalKey=relationalFieldName,
+          ~mappedEntity=derivedFromField.derivedFromEntity,
+        ),
+      )
+      ->ignore
+    })
+
+    //Set object relationships
+    entityConfig.table
+    ->Table.getLinkedEntityFields
+    ->Js.Array2.forEach(((field, linkedEntityName)) => {
+      allOperations
+      ->Js.Array2.push(
+        createEntityRelationshipOperation(
+          ~pgSchema,
+          ~tableName,
+          ~relationshipType="object",
+          ~isDerivedFrom=false,
+          ~objectName=field.fieldName,
+          ~relationalKey=field.fieldName,
+          ~mappedEntity=linkedEntityName,
+        ),
+      )
+      ->ignore
+    })
+  })
+
+  await executeBulkKeepGoing(~endpoint, ~auth, ~operations=allOperations)
 }
```
