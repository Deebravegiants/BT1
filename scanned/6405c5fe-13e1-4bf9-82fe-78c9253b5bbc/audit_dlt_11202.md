# [?] starknet_os_runner: avoid panic in unexpected relocatble value in a casm`s bytecode (#11759)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/sequencer
Published: 2026-01-19
Source: https://github.com/starkware-libs/sequencer/commit/81a768e38790721ad95ca3081616eb94b5725fcc
Type: security-commit

## Details
starknet_os_runner: avoid panic in unexpected relocatble value in a casm`s bytecode (#11759)

## Patch
### Cargo.lock
```diff
@@ -12102,6 +12102,7 @@ dependencies = [
  "tempfile",
  "thiserror 1.0.69",
  "tokio",
+ "tracing",
  "url",
 ]
 
```

### crates/starknet_os_runner/Cargo.toml
```diff
@@ -31,6 +31,7 @@ starknet_patricia.workspace = true
 tempfile.workspace = true
 thiserror.workspace = true
 tokio = { workspace = true, features = ["macros", "process", "rt-multi-thread", "time"] }
+tracing.workspace = true
 url.workspace = true
 
 [dev-dependencies]
```

### crates/starknet_os_runner/src/classes_provider.rs
```diff
@@ -18,6 +18,7 @@ use cairo_vm::types::relocatable::MaybeRelocatable;
 use futures::future::try_join_all;
 use starknet_api::core::{ClassHash, CompiledClassHash};
 use starknet_types_core::felt::Felt;
+use tracing::error;
 
 use crate::errors::ClassesProviderError;
 
@@ -36,10 +37,16 @@ pub(crate) fn compiled_class_v1_to_casm(
         .program
         .iter_data()
         .map(|maybe_relocatable| match maybe_relocatable {
-            MaybeRelocatable::Int(felt) => BigUintAsHex { value: felt.to_biguint() },
-            _ => panic!("Expected all bytecode elements to be MaybeRelocatable::Int"),
+            MaybeRelocatable::Int(felt) => Ok(BigUintAsHex { value: felt.to_biguint() }),
+            MaybeRelocatable::RelocatableValue(relocatable) => {
+                error!(
+                    "Unexpected error: bytecode of a class contained a relocatable value: {:?}",
+                    relocatable
+                );
+                Err(ClassesProviderError::InvalidBytecodeElement)
+            }
         })
-        .collect();
+        .collect::<Result<Vec<_>, _>>()?;
 
     Ok(CasmContractClass {
         prime,
```

### crates/starknet_os_runner/src/errors.rs
```diff
@@ -52,6 +52,8 @@ pub enum ClassesProviderError {
         "Starknet os does not support deprecated contract classes, class hash: {0} is deprecated"
     )]
     DeprecatedContractError(ClassHash),
+    #[error("Unexpected error: bytecode of a class contained a non-integer value")]
+    InvalidBytecodeElement,
     #[error(transparent)]
     StateError(#[from] StateError),
     #[error(transparent)]
```
