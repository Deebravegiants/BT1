# [?] graph: Avoid panic in API schema generation

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2023-12-08
Source: https://github.com/graphprotocol/graph-node/commit/6a843af31011a5e5b45836e53d36da68d61bc2de
Type: security-commit

## Details
graph: Avoid panic in API schema generation

## Patch
### graph/src/schema/api.rs
```diff
@@ -597,7 +597,7 @@ fn field_filter_input_values(
             })
         }
         Type::ListType(ref t) => {
-            Ok(field_list_filter_input_values(schema, field, t).unwrap_or_default())
+            Ok(field_list_filter_input_values(schema, field, t)?.unwrap_or_default())
         }
         Type::NonNullType(ref t) => field_filter_input_values(schema, field, t),
     }
@@ -614,7 +614,9 @@ fn id_type_as_scalar(
         TypeDefinition::Interface(intf_type) => match intf_type.implements_interfaces.as_slice() {
             [] => Ok(Some(IdType::String)),
             [obj_type, ..] => {
-                let obj_type = schema.get_object_type_definition(&obj_type).unwrap();
+                let obj_type = schema
+                    .get_object_type_definition(&obj_type)
+                    .ok_or_else(|| APISchemaError::TypeNotFound(obj_type.to_string()))?;
                 IdType::try_from(obj_type)
                     .map(Option::Some)
                     .map_err(|_| APISchemaError::IllegalIdType(obj_type.name.to_owned()))
@@ -735,60 +737,63 @@ fn field_list_filter_input_values(
     schema: &Document,
     field: &Field,
     field_type: &Type,
-) -> Option<Vec<InputValue>> {
+) -> Result<Option<Vec<InputValue>>, APISchemaError> {
     // Only add a filter field if the type of the field exists in the schema
-    ast::get_type_definition_from_type(schema, field_type).map(|typedef| {
-        // Decide what type of values can be passed to the filter. In the case
-        // one-to-many or many-to-many object or interface fields that are not
-        // derived, we allow ID strings to be passed on.
-        // Adds child filter only to object types.
-        let (input_field_type, parent_type_name) = match typedef {
-            TypeDefinition::Object(ObjectType { name, .. })
-            | TypeDefinition::Interface(InterfaceType { name, .. }) => {
-                if ast::get_derived_from_directive(field).is_some() {
-                    (None, Some(name.clone()))
-                } else {
-                    let scalar_type = id_type_as_scalar(schema, typedef).unwrap().unwrap();
-                    let named_type = Type::NamedType(scalar_type.name);
-                    (Some(named_type), Some(name.clone()))
-                }
-            }
-            TypeDefinition::Scalar(ref t) => (Some(Type::NamedType(t.name.clone())), None),
-            TypeDefinition::Enum(ref t) => (Some(Type::NamedType(t.name.clone())), None),
-            TypeDefinition::InputObject(_) | TypeDefinition::Union(_) => (None, None),
-        };
+    let typedef = match ast::get_type_definition_from_type(schema, field_type) {
+        Some(typedef) => typedef,
+        None => return Ok(None),
+    };
 
-        let mut input_values: Vec<InputValue> = match input_field_type {
-            None => {
-                vec![]
+    // Decide what type of values can be passed to the filter. In the case
+    // one-to-many or many-to-many object or interface fields that are not
+    // derived, we allow ID strings to be passed on.
+    // Adds child filter only to object types.
+    let (input_field_type, parent_type_name) = match typedef {
+        TypeDefinition::Object(ObjectType { name, .. })
+        | TypeDefinition::Interface(InterfaceType { name, .. }) => {
+            if ast::get_derived_from_directive(field).is_some() {
+                (None, Some(name.clone()))
+            } else {
+                let scalar_type = id_type_as_scalar(schema, typedef)?.unwrap();
+                let named_type = Type::NamedType(scalar_type.name);
+                (Some(named_type), Some(name.clone()))
             }
-            Some(input_field_type) => vec![
-                "",
-                "not",
-                "contains",
-                "contains_nocase",
-                "not_contains",
-                "not_contains_nocase",
-            ]
-            .into_iter()
-            .map(|filter_type| {
-                input_value(
-                    &field.name,
-                    filter_type,
-                    Type::ListType(Box::new(Type::NonNullType(Box::new(
-                        input_field_type.clone(),
-                    )))),
-                )
-            })
-            .collect(),
-        };
+        }
+        TypeDefinition::Scalar(ref t) => (Some(Type::NamedType(t.name.clone())), None),
+        TypeDefinition::Enum(ref t) => (Some(Type::NamedType(t.name.clone())), None),
+        TypeDefinition::InputObject(_) | TypeDefinition::Union(_) => (None, None),
+    };
 
-        if let Some(parent) = parent_type_name {
-            extend_with_child_filter_input_value(field, &parent, &mut input_values);
+    let mut input_values: Vec<InputValue> = match input_field_type {
+        None => {
+            vec![]
         }
+        Some(input_field_type) => vec![
+            "",
+            "not",
+            "contains",
+            "contains_nocase",
+            "not_contains",
+            "not_contains_nocase",
+        ]
+        .into_iter()
+        .map(|filter_type| {
+            input_value(
+                &field.name,
+                filter_type,
+                Type::ListType(Box::new(Type::NonNullType(Box::new(
+                    input_field_type.clone(),
+                )))),
+            )
+        })
+        .collect(),
+    };
 
-        input_values
-    })
+    if let Some(parent) = parent_type_name {
+        extend_with_child_filter_input_value(field, &parent, &mut input_values);
+    }
+
+    Ok(Some(input_values))
 }
 
 /// Generates a `*_filter` input value for the given field name, suffix and value type.
```
