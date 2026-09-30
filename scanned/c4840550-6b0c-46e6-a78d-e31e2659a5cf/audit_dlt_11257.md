# [?] fix: Error instead of panic when method is not found (#11330)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-01-26
Source: https://github.com/noir-lang/noir/commit/e1b2904367e55e88385af7905c2ded8e86920b49
Type: security-commit

## Details
fix: Error instead of panic when method is not found (#11330)

## Patch
### compiler/noirc_frontend/src/elaborator/types.rs
```diff
@@ -2197,8 +2197,6 @@ impl Elaborator<'_> {
     /// * in any of the traits which appear in the constraints of the function
     ///
     /// Pushes an error if the method cannot be found.
-    ///
-    /// Panics if we are not elaborating a function currently.
     fn lookup_method_in_trait_constraints(
         &mut self,
         object_type: &Type,
@@ -2208,7 +2206,15 @@ impl Elaborator<'_> {
     ) -> Option<HirMethodReference> {
         let func_id = match self.current_item {
             Some(DependencyId::Function(id)) => id,
-            _ => panic!("unexpected method outside a function: {method_name}"),
+            _ => {
+                // Unexpected method outside a function.
+                self.push_err(TypeCheckError::UnresolvedMethodCall {
+                    method_name: method_name.to_string(),
+                    object_type: object_type.clone(),
+                    location,
+                });
+                return None;
+            }
         };
         let func_meta = self.interner.function_meta(&func_id);
 
```

### compiler/noirc_frontend/src/tests/globals.rs
```diff
@@ -217,3 +217,20 @@ fn comptime_global_using_nested_quoted_type() {
     ";
     assert_no_errors(src);
 }
+
+#[test]
+fn global_closure_with_undefined_variable_method_call() {
+    // A global contained a closure with a method call on an undefined variable.
+    // It should report an error, and not panic.
+    let src = r#"
+    global foo: fn() -> Field = || {
+        v0.bar()
+        ^^ cannot find `v0` in this scope
+        ~~ not found in this scope
+    };
+    fn main() {
+        let _ = foo;
+    }
+    "#;
+    check_errors(src);
+}
```
