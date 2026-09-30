# [?] fix: correct location for out of bounds match case integer (#10454)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-11-10
Source: https://github.com/noir-lang/noir/commit/36ecc83ad50a16988debe0216dd9b56ae179043a
Type: security-commit

## Details
fix: correct location for out of bounds match case integer (#10454)

## Patch
### compiler/noirc_frontend/src/elaborator/enums.rs
```diff
@@ -24,7 +24,7 @@ use crate::{
     hir_def::{
         expr::{
             Case, Constructor, HirBlockExpression, HirEnumConstructorExpression, HirExpression,
-            HirIdent, HirMatch,
+            HirIdent, HirLiteral, HirMatch,
         },
         function::{FuncMeta, FunctionBody, HirFunction, Parameters},
         stmt::{HirLetStatement, HirPattern, HirStatement},
@@ -462,6 +462,12 @@ impl Elaborator<'_> {
                     None => self.interner.next_type_variable_with_kind(Kind::IntegerOrField),
                 };
                 unify_with_expected_type(self, &actual);
+
+                let expr = HirExpression::Literal(HirLiteral::Integer(value));
+                let location = expr_location;
+                let expr_id = self.interner.push_expr_full(expr, location, actual.clone());
+                self.push_integer_literal_expr_id(expr_id);
+
                 Pattern::Int(value)
             }
             ExpressionKind::Literal(Literal::Bool(value)) => {
```

### test_programs/compile_failure/regression_10389_1/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+[package]
+name = "regression_10389_1"
+type = "bin"
+authors = [""]
+compiler_unstable_features = ["enums"]
+
+[dependencies]
```

### test_programs/compile_failure/regression_10389_1/src/main.nr
```diff
@@ -0,0 +1,7 @@
+fn main() {
+    let x = 255_u8;
+    match x {
+        -1 => {},
+        _ => {},
+    }
+}
```

### test_programs/compile_failure/regression_10389_2/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+[package]
+name = "regression_10389_2"
+type = "bin"
+authors = [""]
+compiler_unstable_features = ["enums"]
+
+[dependencies]
```

### test_programs/compile_failure/regression_10389_2/src/main.nr
```diff
@@ -0,0 +1,6 @@
+fn main(x: u8) {
+    match x {
+        -1 => {},
+        _ => {},
+    }
+}
```

### tooling/nargo_cli/tests/snapshots/compile_failure/regression_10389_1/execute__tests__stderr.snap
```diff
@@ -0,0 +1,12 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: The value `-1` cannot fit into `u8` which has range `0..=255`
+  ┌─ src/main.nr:4:9
+  │
+4 │         -1 => {},
+  │         --
+  │
+
+Aborting due to 1 previous error
```

### tooling/nargo_cli/tests/snapshots/compile_failure/regression_10389_2/execute__tests__stderr.snap
```diff
@@ -0,0 +1,12 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: The value `-1` cannot fit into `u8` which has range `0..=255`
+  ┌─ src/main.nr:3:9
+  │
+3 │         -1 => {},
+  │         --
+  │
+
+Aborting due to 1 previous error
```
