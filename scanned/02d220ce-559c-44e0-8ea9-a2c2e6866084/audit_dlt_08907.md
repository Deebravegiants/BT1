# [?] fix(executor/native): catch Cairo native compiler panics

## Summary
Severity: Unknown
Chain: Starknet
Component: software-mansion/pathfinder
Published: 2025-03-13
Source: https://github.com/software-mansion/pathfinder/commit/38282bcc0821f482cb6d1b6f035ed43c08dc1638
Type: security-commit

## Details
fix(executor/native): catch Cairo native compiler panics

And convert those into an error.

## Patch
### crates/executor/src/state_reader/native.rs
```diff
@@ -131,12 +131,16 @@ fn sierra_class_as_native(input: CompilerInput) -> Result<NativeCompiledClassV1,
         minor: input.sierra_version.minor as usize,
         patch: input.sierra_version.patch as usize,
     };
-    let contract_executor = AotContractExecutor::new(
-        &sierra_program,
-        &sierra_class.entry_points_by_type,
-        version_id,
-        cairo_native::OptLevel::Default,
-    )
+
+    let contract_executor = std::panic::catch_unwind(|| {
+        AotContractExecutor::new(
+            &sierra_program,
+            &sierra_class.entry_points_by_type,
+            version_id,
+            cairo_native::OptLevel::Default,
+        )
+    })
+    .map_err(|e| StateError::StateReadError(format!("Error compiling native class: {e:?}")))?
     .map_err(|e| StateError::StateReadError(format!("Error compiling native class: {e}")))?;
 
     let casm_definition = String::from_utf8(input.casm_definition).map_err(|error| {
```
