# [?] [scmd] fix empty table print panic.

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2020-04-15
Source: https://github.com/starcoinorg/starcoin/commit/da69223327b1b132038aec6a13473d1cca912f30
Type: security-commit

## Details
[scmd] fix empty table print panic.

## Patch
### commons/scmd/src/result.rs
```diff
@@ -73,6 +73,9 @@ pub fn fmt_table(value: Value) -> Result<()> {
         Value::Array(values) => values,
         value => vec![value],
     };
+    if values.is_empty() {
+        return Ok(());
+    }
     let first = &values[0];
     let first_value = serde_json::to_value(first)?;
     if first_value.is_null() {
```
