# [?] graph, graphql, store: Added flag to reject any operation using non-deterministic fulltext search

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2020-12-14
Source: https://github.com/graphprotocol/graph-node/commit/484386087c7ecff4bda20c7b2f4d3bcadd915c79
Type: security-commit

## Details
graph, graphql, store: Added flag to reject any operation using non-deterministic fulltext search

## Patch
### graph/src/components/store.rs
```diff
@@ -887,6 +887,8 @@ pub enum StoreError {
         _0
     )]
     UnknownShard(String),
+    #[fail(display = "Fulltext search not yet deterministic")]
+    FulltextSearchNonDeterministic,
 }
 
 // Convenience to report a constraint violation
```

### graph/src/data/graphql/ext.rs
```diff
@@ -1,13 +1,20 @@
+use super::ObjectOrInterface;
 use crate::data::schema::{META_FIELD_TYPE, SCHEMA_TYPE_NAME};
 use graphql_parser::schema::{
     Definition, Directive, Document, EnumType, Field, InterfaceType, Name, ObjectType, Type,
     TypeDefinition, Value,
 };
-
-use super::ObjectOrInterface;
-
+use lazy_static::lazy_static;
 use std::collections::{BTreeMap, HashMap};
 
+lazy_static! {
+    static ref ALLOW_NON_DETERMINISTIC_FULLTEXT_SEARCH: bool = if cfg!(debug_assertions) {
+        true
+    } else {
+        std::env::var("GRAPH_ALLOW_NON_DETERMINISTIC_FULLTEXT_SEARCH").is_ok()
+    };
+}
+
 pub trait ObjectTypeExt {
     fn field(&self, name: &Name) -> Option<&Field>;
     fn is_meta(&self) -> bool;
@@ -44,7 +51,7 @@ pub trait DocumentExt {
 
     fn find_interface(&self, name: &str) -> Option<&InterfaceType>;
 
-    fn get_fulltext_directives<'a>(&'a self) -> Vec<&'a Directive>;
+    fn get_fulltext_directives<'a>(&'a self) -> Result<Vec<&'a Directive>, anyhow::Error>;
 
     fn get_root_query_type(&self) -> Option<&ObjectType>;
 
@@ -102,15 +109,22 @@ impl DocumentExt for Document {
         })
     }
 
-    fn get_fulltext_directives(&self) -> Vec<&Directive> {
-        self.get_object_type_definition(SCHEMA_TYPE_NAME)
-            .map_or(vec![], |subgraph_schema_type| {
+    fn get_fulltext_directives(&self) -> Result<Vec<&Directive>, anyhow::Error> {
+        let directives = self.get_object_type_definition(SCHEMA_TYPE_NAME).map_or(
+            vec![],
+            |subgraph_schema_type| {
                 subgraph_schema_type
                     .directives
                     .iter()
                     .filter(|directives| directives.name.eq("fulltext"))
                     .collect()
-            })
+            },
+        );
+        if !*ALLOW_NON_DETERMINISTIC_FULLTEXT_SEARCH && directives.len() != 0 {
+            Err(anyhow::anyhow!("Fulltext search is not yet deterministic"))
+        } else {
+            Ok(directives)
+        }
     }
 
     /// Returns the root query type (if there is one).
```

### graph/src/data/schema.rs
```diff
@@ -1281,9 +1281,9 @@ impl Schema {
     pub fn entity_fulltext_definitions<'a>(
         entity: &str,
         document: &'a Document,
-    ) -> Vec<FulltextDefinition> {
-        document
-            .get_fulltext_directives()
+    ) -> Result<Vec<FulltextDefinition>, anyhow::Error> {
+        Ok(document
+            .get_fulltext_directives()?
             .into_iter()
             .filter(|directive| match directive.argument("include") {
                 Some(Value::List(includes)) if includes.len() > 0 => includes
@@ -1301,7 +1301,7 @@ impl Schema {
                 _ => false,
             })
             .map(|directive| FulltextDefinition::from(directive))
-            .collect()
+            .collect())
     }
 }
 
```

### graphql/src/schema/api.rs
```diff
@@ -21,6 +21,8 @@ pub enum APISchemaError {
     TypeExists(String),
     #[fail(display = "Type {} not found", _0)]
     TypeNotFound(String),
+    #[fail(display = "Fulltext search is not yet deterministic")]
+    FulltextSearchNonDeterministic,
 }
 
 const BLOCK_HEIGHT: &str = "Block_height";
@@ -520,6 +522,7 @@ fn add_query_type(
         .collect::<Vec<Field>>();
     let mut fulltext_fields = schema
         .get_fulltext_directives()
+        .map_err(|_| APISchemaError::FulltextSearchNonDeterministic)?
         .iter()
         .filter_map(|fulltext| query_field_for_fulltext(fulltext, features))
         .collect();
```

### store/postgres/src/relational.rs
```diff
@@ -297,7 +297,8 @@ impl Layout {
                 Table::new(
                     obj_type,
                     &catalog,
-                    Schema::entity_fulltext_definitions(&obj_type.name, &schema.document),
+                    Schema::entity_fulltext_definitions(&obj_type.name, &schema.document)
+                        .map_err(|_| StoreError::FulltextSearchNonDeterministic)?,
                     &enums,
                     &id_types,
                     i as u32,
```
