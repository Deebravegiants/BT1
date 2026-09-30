# [?] fix: don't crash on duplicate trait impl (#12477)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-04-29
Source: https://github.com/noir-lang/noir/commit/d2c1ebd0a8d881bcaffa6351afb42d32088e3a4c
Type: security-commit

## Details
fix: don't crash on duplicate trait impl (#12477)

## Patch
### compiler/noirc_frontend/src/elaborator/impls.rs
```diff
@@ -180,11 +180,9 @@ impl Elaborator<'_> {
                 };
 
                 // Handle method shadowing when a duplicate method name is found
-                if result.is_err() {
-                    let existing = module.find_func_with_name(method.name_ident()).expect(
-                        "declare_function should only error if there is an existing function",
-                    );
-
+                if result.is_err()
+                    && let Some(existing) = module.find_func_with_name(method.name_ident())
+                {
                     // Inherent impls take precedence over trait impls for qualified calls.
                     // If the existing method is from a trait impl, remove it from module scope
                     // so that `TypeName::method` resolves to the inherent impl version.
```

### compiler/noirc_frontend/src/tests/traits/trait_impl_validation.rs
```diff
@@ -503,3 +503,31 @@ fn overlapping_generic_impls() {
     "#;
     check_errors(src);
 }
+
+#[test]
+fn does_not_crash_when_trait_impl_is_defined_multiple_times() {
+    let src = r#"
+    pub struct Wrap { }
+
+    trait Marker1 { 
+        fn mark(); 
+    } 
+    trait Marker2 { 
+        fn mark(); 
+    }
+
+    impl Marker1 for Wrap { 
+        fn mark() { } 
+    } 
+    impl Marker2 for Wrap { 
+         ~~~~~~~ Previous impl defined here
+        fn mark() {} 
+    } 
+    impl Marker2 for Wrap { 
+                     ^^^^ Impl for type `Wrap` overlaps with existing impl
+                     ~~~~ Overlapping impl
+        fn mark() {} 
+    }
+    "#;
+    check_errors(src);
+}
```
