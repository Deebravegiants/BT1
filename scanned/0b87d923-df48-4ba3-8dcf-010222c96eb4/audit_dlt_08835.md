# [?] fix(starknet-classes): reject crafted out-of-range type ids instead of panicking (#10224)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-07-20
Source: https://github.com/starkware-libs/cairo/commit/ff745b1062fb371be812e5e2e6823a0905093de9
Type: security-commit

## Details
fix(starknet-classes): reject crafted out-of-range type ids instead of panicking (#10224)

## Patch
### crates/cairo-lang-starknet-classes/src/casm_contract_class.rs
```diff
@@ -442,6 +442,11 @@ impl CasmContractClass {
                 });
             }
         }
+        let program_info = ProgramRegistryInfo::new(&program).map_err(|err| {
+            StarknetSierraCompilationError::CompilationError(Box::new(
+                CompilationError::ProgramRegistryError(err),
+            ))
+        })?;
         let type_resolver = TypeResolver { type_decl: &program.type_declarations };
 
         // Validates the entry point's signature, returning its entry statement, function id and
@@ -533,11 +538,6 @@ impl CasmContractClass {
             skip_non_linear_solver_comparisons: false,
             compute_runtime_costs: false,
         };
-        let program_info = ProgramRegistryInfo::new(&program).map_err(|err| {
-            StarknetSierraCompilationError::CompilationError(Box::new(
-                CompilationError::ProgramRegistryError(err),
-            ))
-        })?;
         let metadata = calc_metadata(&program, &program_info, metadata_computation_config)?;
         let cairo_program = cairo_lang_sierra_to_casm::compiler::compile(
             &program,
```

### crates/cairo-lang-starknet-classes/src/casm_contract_class_test.rs
```diff
@@ -5,6 +5,8 @@ use std::fs;
 use std::io::BufReader;
 
 use cairo_lang_sierra::ids::{ConcreteTypeId, GenericLibfuncId};
+use cairo_lang_sierra::program_registry::ProgramRegistryError;
+use cairo_lang_sierra_to_casm::compiler::CompilationError;
 use cairo_lang_test_utils::compare_contents_or_fix_with_path;
 use cairo_lang_test_utils::parse_test_file::TestRunnerResult;
 use cairo_lang_utils::ordered_hash_map::OrderedHashMap;
@@ -107,6 +109,27 @@ fn test_entry_point_mid_list_gas_or_system_rejected() {
     }
 }
 
+#[test]
+fn test_entry_point_out_of_range_type_id_rejected() {
+    let contract_class = load_example_contract_class("libfuncs_coverage__libfuncs_coverage");
+    let mut extracted = contract_class.extract_sierra_program(false).unwrap();
+    let program = &mut extracted.program;
+    // An id one past the last declaration is guaranteed undeclared.
+    let out_of_range = ConcreteTypeId::new(program.type_declarations.len() as u64);
+    let func_idx = contract_class.entry_points_by_type.external[0].function_idx;
+    // Point the entry point's input (the `Span<felt252>` calldata param) at the undeclared type id.
+    *program.funcs[func_idx].signature.param_types.last_mut().unwrap() = out_of_range.clone();
+    assert_eq!(
+        CasmContractClass::from_contract_class(contract_class, extracted, false, usize::MAX)
+            .unwrap_err(),
+        StarknetSierraCompilationError::CompilationError(Box::new(
+            CompilationError::ProgramRegistryError(Box::new(ProgramRegistryError::MissingType(
+                out_of_range
+            ))),
+        )),
+    );
+}
+
 /// Tests that the CASM compiled from a contract in the contract_crate is the same as in
 /// <test_case>.compiled_contract_class.json.
 #[test_case("account__account")]
```
