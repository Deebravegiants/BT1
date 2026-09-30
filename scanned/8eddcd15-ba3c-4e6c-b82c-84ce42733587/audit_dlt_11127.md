# [?] Check for typed program errors before unwrapping to prevent panics. (#7190)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2025-05-22
Source: https://github.com/FuelLabs/sway/commit/07f8fc37359e9455ef2114d863457d3977c2bac2
Type: security-commit

## Details
Check for typed program errors before unwrapping to prevent panics. (#7190)

## Description
As the title says.

## Patch
### sway-lsp/src/core/session.rs
```diff
@@ -330,9 +330,16 @@ pub fn traverse(
             continue;
         };
 
+        // Ensure that the typed program result is Ok before proceeding.
+        // If it's an Err, it indicates a failure in generating the typed AST,
+        // and we should return an error rather than panicking on unwrap.
+        if typed.is_err() {
+            return Err(LanguageServerError::FailedToParse);
+        }
+
         let program_id = typed
             .as_ref()
-            .unwrap()
+            .unwrap() // safe to unwrap because we checked for Err above
             .namespace
             .current_package_ref()
             .program_id;
```
