# [?] fix: correct AssemblyError message for out of bounds parameters

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2022-01-30
Source: https://github.com/0xMiden/miden-vm/commit/603aa685d405b3b1675aacb7bffeba705e9b6736
Type: security-commit

## Details
fix: correct AssemblyError message for out of bounds parameters

## Patch
### assembly/src/parsers/io_ops.rs
```diff
@@ -543,7 +543,7 @@ mod tests {
 
         // parameter out of bounds
         let reason = format!(
-            "parameter value must be greater than {} and less than than {}",
+            "parameter value must be greater than or equal to {} and less than or equal to {}",
             1, ADVICE_READ_LIMIT
         );
         // less than lower bound
```

### assembly/src/parsers/mod.rs
```diff
@@ -180,7 +180,7 @@ fn parse_int_param(
             op,
             param_idx,
             format!(
-                "parameter value must be greater than {} and less than than {}",
+                "parameter value must be greater than or equal to {} and less than or equal to {}",
                 lower_bound, upper_bound
             )
             .as_str(),
```
