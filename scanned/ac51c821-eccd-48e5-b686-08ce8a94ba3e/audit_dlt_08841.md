# [?] bugfix(semantic): Prevent crash on `?` on generics. (#9999)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2026-05-28
Source: https://github.com/starkware-libs/cairo/commit/a834fcb46bc79453c96d608b6eb05af1c2597bde
Type: security-commit

## Details
bugfix(semantic): Prevent crash on `?` on generics. (#9999)

## Patch
### crates/cairo-lang-semantic/src/corelib.rs
```diff
@@ -506,11 +506,8 @@ pub fn unwrap_error_propagation_type<'db>(
                 None
             }
         }
-        TypeLongId::GenericParameter(_) => todo!(
-            "When generic types are supported, if type is of matching type, allow unwrapping it \
-             to type."
-        ),
-        TypeLongId::Concrete(
+        TypeLongId::GenericParameter(_)
+        | TypeLongId::Concrete(
             semantic::ConcreteTypeId::Struct(_) | semantic::ConcreteTypeId::Extern(_),
         )
         | TypeLongId::Tuple(_)
```

### crates/cairo-lang-semantic/src/expr/test_data/error_propagate
```diff
@@ -153,3 +153,30 @@ error[E2063]: Type "core::integer::u32" cannot error propagate
  --> lib.cairo:2:5
     6_u32?;
     ^^^^^^
+
+//! > ==========================================================================
+
+//! > Test generics operand for error propagation.
+
+//! > test_runner_name
+test_function_diagnostics(expect_diagnostics: true)
+
+//! > function_code
+fn foo(a: Option<felt252>) -> Option<felt252> {
+    bar(a)
+}
+
+//! > function_name
+foo
+
+//! > module_code
+fn bar<T, +Copy<T>>(t: T) -> T {
+    t?;
+    t
+}
+
+//! > expected_diagnostics
+error[E2061]: `?` can only be used in a function with `Option` or `Result` return type.
+ --> lib.cairo:2:5
+    t?;
+    ^^
```
