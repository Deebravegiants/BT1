# [?] graphql: handle empty lists in list_values to avoid panic (#6100)

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2025-08-14
Source: https://github.com/graphprotocol/graph-node/commit/28ed68e31a4d45a35b67ada0be8953ca1980225c
Type: security-commit

## Details
graphql: handle empty lists in list_values to avoid panic (#6100)

* graphql: handle empty lists in list_values to avoid panic

* graphql: add unit test for empty IN filter

## Patch
### graphql/src/store/query.rs
```diff
@@ -417,6 +417,9 @@ fn build_child_filter_from_object(
 fn list_values(value: Value, filter_type: &str) -> Result<Vec<Value>, QueryExecutionError> {
     match value {
         Value::List(values) => {
+            if values.is_empty() {
+                return Ok(values);
+            }
             // Check that all values in list are of the same type
             let root_discriminant = discriminant(&values[0]);
             for value in &values {
@@ -968,6 +971,26 @@ mod tests {
         )
     }
 
+    #[test]
+    fn build_query_handles_empty_in_list() {
+        let query_field = default_field_with(
+            "where",
+            r::Value::Object(Object::from_iter(vec![(
+                "id_in".into(),
+                r::Value::List(vec![]),
+            )])),
+        );
+
+        let result = query(&query_field);
+        assert_eq!(
+            result.filter,
+            Some(EntityFilter::And(vec![EntityFilter::In(
+                "id".to_string(),
+                Vec::<Value>::new(),
+            )]))
+        );
+    }
+
     #[test]
     fn build_query_yields_block_change_gte_filter() {
         let query_field = default_field_with(
```
