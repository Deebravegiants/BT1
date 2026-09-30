# [?] fix(frontend): emit one error for numeric type alias overflow (#12565)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-05-06
Source: https://github.com/noir-lang/noir/commit/edcf12e897790342f58c9ec526506b87f673dd5b
Type: security-commit

## Details
fix(frontend): emit one error for numeric type alias overflow (#12565)

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

## Patch
### compiler/noirc_frontend/src/elaborator/function_context.rs
```diff
@@ -131,6 +131,14 @@ impl Elaborator<'_> {
         self.get_function_context_mut().integer_literal_expr_ids.push(literal_expr_id);
     }
 
+    pub(super) fn integer_literal_expr_ids_len(&mut self) -> usize {
+        self.get_function_context_mut().integer_literal_expr_ids.len()
+    }
+
+    pub(super) fn truncate_integer_literal_expr_ids(&mut self, len: usize) {
+        self.get_function_context_mut().integer_literal_expr_ids.truncate(len);
+    }
+
     #[tracing::instrument(level = "trace", skip_all)]
     fn get_function_context_mut(&mut self) -> &mut FunctionContext {
         let context = self.function_context.last_mut();
```

### compiler/noirc_frontend/src/elaborator/variable.rs
```diff
@@ -141,7 +141,14 @@ impl Elaborator<'_> {
                         }
                     }
 
+                    // The alias's numeric expression has already been kind-checked at
+                    // alias-definition time (see `convert_expression_type`), which is
+                    // where any "value does not fit" diagnostic is emitted. Drop any
+                    // literals queued for the function-context fit check during
+                    // re-elaboration so the same overflow is not reported twice.
+                    let literals_before = self.integer_literal_expr_ids_len();
                     let (id, typ) = self.elaborate_expression(expr);
+                    self.truncate_integer_literal_expr_ids(literals_before);
                     self.pop_scope();
 
                     // Unify the expression's type with the declared type from the type alias
```

### compiler/noirc_frontend/src/tests/aliases.rs
```diff
@@ -762,7 +762,6 @@ fn regression_10971() {
     // Regression test for https://github.com/noir-lang/noir/issues/10971
     let src = r#"
     pub type X: u8 = 257u8;
-    ^^^^^^^^^^^^^^^^^^^^^^ The value `257` cannot fit into `u8` which has range `0..=255`
                      ^^^^^ The value `257` cannot fit into `u8` which has range `0..=255`
 
     fn main() {
```
