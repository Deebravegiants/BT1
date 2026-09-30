# [?] fix: emit diagnostic for non-type numeric literal suffix instead of panicking (#9810)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-04-05
Source: https://github.com/starkware-libs/cairo/commit/a459dfa0e1f4628307f55d2e45d1033e748d187f
Type: security-commit

## Details
fix: emit diagnostic for non-type numeric literal suffix instead of panicking (#9810)

## Patch
### crates/cairo-lang-semantic/src/corelib.rs
```diff
@@ -181,7 +181,7 @@ pub fn try_get_ty_by_name<'db>(
         }
         _ => GenericTypeId::option_from(module_item_id),
     }
-    .unwrap_or_else(|| panic!("{} is not a type.", name.long(db)));
+    .ok_or(SemanticDiagnosticKind::NotAType)?;
 
     Ok(semantic::TypeLongId::Concrete(semantic::ConcreteTypeId::new(
         db,
```

### crates/cairo-lang-semantic/src/expr/test_data/literal
```diff
@@ -16,3 +16,24 @@ error[E2008]: A numeric literal of type core::pedersen::Pedersen cannot be creat
  --> lib.cairo:2:14
     let _a = 'a'_Pedersen;
              ^^^^^^^^^^^^
+
+//! > ==========================================================================
+
+//! > Numeric literal with a non-type suffix.
+
+//! > test_runner_name
+test_function_diagnostics(expect_diagnostics: true)
+
+//! > function_code
+fn foo() {
+    let _x = 1_boolean;
+}
+
+//! > function_name
+foo
+
+//! > expected_diagnostics
+error[E2011]: Not a type.
+ --> lib.cairo:2:14
+    let _x = 1_boolean;
+             ^^^^^^^^^
```
