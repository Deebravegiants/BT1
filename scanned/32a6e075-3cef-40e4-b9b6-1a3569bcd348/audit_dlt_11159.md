# [?] fix: prevent panic when parsing empty string (#774)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2022-02-18
Source: https://github.com/FuelLabs/sway/commit/023a90118041b074f1c8530cb19b7c799088886a
Type: security-commit

## Details
fix: prevent panic when parsing empty string (#774)

* fix: prevent panic when parsing empty string

* Fix PR feedback

* Move the `error::new()` function to a `CompileResult::new()` method.

Co-authored-by: Toby Hutton <toby@grusly.com>

## Patch
### sway-core/src/error.rs
```diff
@@ -94,6 +94,14 @@ impl<T> From<Result<T, TypeError>> for CompileResult<T> {
 }
 
 impl<T> CompileResult<T> {
+    pub fn new(value: Option<T>, warnings: Vec<CompileWarning>, errors: Vec<CompileError>) -> Self {
+        CompileResult {
+            value,
+            warnings,
+            errors,
+        }
+    }
+
     pub fn ok(
         mut self,
         warnings: &mut Vec<CompileWarning>,
```

### sway-core/src/lib.rs
```diff
@@ -696,8 +696,7 @@ fn parse_root_from_pairs(
         }
     }
 
-    let fuel_ast = fuel_ast_opt.unwrap();
-    ok(fuel_ast, warnings, errors)
+    CompileResult::new(fuel_ast_opt, warnings, errors)
 }
 
 #[test]
```
