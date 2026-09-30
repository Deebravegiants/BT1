# [?] fix: outdated function name in PushValues panic (#8993)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2025-12-10
Source: https://github.com/starkware-libs/cairo/commit/7e7c82fd6dd8a646a205853fd19b1b0742cba633
Type: security-commit

## Details
fix: outdated function name in PushValues panic (#8993)

## Patch
### crates/cairo-lang-sierra-generator/src/program_generator.rs
```diff
@@ -52,7 +52,10 @@ fn collect_and_generate_libfunc_declarations<'db>(
             pre_sierra::Statement::Sierra(program::GenStatement::Return(_))
             | pre_sierra::Statement::Label(_) => None,
             pre_sierra::Statement::PushValues(_) => {
-                panic!("Unexpected pre_sierra::Statement::PushValues in collect_used_libfuncs().")
+                panic!(
+                    "Unexpected pre_sierra::Statement::PushValues in \
+                     collect_and_generate_libfunc_declarations()."
+                )
             }
         })
         .collect()
```
