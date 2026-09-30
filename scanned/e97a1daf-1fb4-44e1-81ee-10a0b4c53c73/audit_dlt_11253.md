# [?] fix: prevent crash when resolving method in trait impl with unknown t… (#11656)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-02-23
Source: https://github.com/noir-lang/noir/commit/7cff3a6c2e989f220429bccc9d03177c2eb8c49c
Type: security-commit

## Details
fix: prevent crash when resolving method in trait impl with unknown t… (#11656)

## Patch
### compiler/noirc_frontend/src/elaborator/variable.rs
```diff
@@ -248,15 +248,16 @@ impl Elaborator<'_> {
         // Check if the constant exists in the trait definition (even if impl is missing it).
         // This prevents spurious "Could not resolve" errors inside trait methods when the impl is missing the constant,
         // since the "missing associated constant" error is reported elsewhere.
-        let trait_impl = self.interner.get_trait_implementation(*trait_impl_id);
-        let trait_id = trait_impl.borrow().trait_id;
-        let trait_ = self.interner.get_trait(trait_id);
-        if let Some(definition_id) = trait_.associated_constant_ids.get(name).copied() {
-            let numeric_type = self.interner.definition_type(definition_id);
-            let hir_ident = HirIdent::non_trait_method(definition_id, location);
-            let hir_expr = HirExpression::Ident(hir_ident, None);
-            let id = self.interner.push_expr_full(hir_expr, location, numeric_type.clone());
-            return Some((id, numeric_type));
+        if let Some(trait_impl) = self.interner.try_get_trait_implementation(*trait_impl_id) {
+            let trait_id = trait_impl.borrow().trait_id;
+            let trait_ = self.interner.get_trait(trait_id);
+            if let Some(definition_id) = trait_.associated_constant_ids.get(name).copied() {
+                let numeric_type = self.interner.definition_type(definition_id);
+                let hir_ident = HirIdent::non_trait_method(definition_id, location);
+                let hir_expr = HirExpression::Ident(hir_ident, None);
+                let id = self.interner.push_expr_full(hir_expr, location, numeric_type.clone());
+                return Some((id, numeric_type));
+            }
         }
 
         // Check the `Self::method_name` case when `Self` is a primitive type (2 segments)
```

### compiler/noirc_frontend/src/tests/traits/trait_associated_items.rs
```diff
@@ -1845,3 +1845,18 @@ fn associated_constant_in_return_type_with_generic_impl_forwarding() {
     "#;
     assert_no_errors(src);
 }
+
+// Regression test for https://github.com/noir-lang/noir/issues/11655
+#[test]
+fn self_method_call_on_trait_impl_for_unknown_trait() {
+    let src = r#"
+    impl Unknown for Field {
+         ^^^^^^^ Trait Unknown not found
+        fn unknown() {
+            Self::method()
+                  ^^^^^^ No method named 'method' found for type 'Field'
+        }
+    }
+    "#;
+    check_errors(src);
+}
```
