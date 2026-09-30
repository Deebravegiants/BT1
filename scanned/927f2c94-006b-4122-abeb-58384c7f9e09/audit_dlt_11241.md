# [?] fix(ssa interpreter): Clarify overflow error (#12483)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-04-29
Source: https://github.com/noir-lang/noir/commit/bda0d7aaf14a99aa2a22842f85c565f3a1ef4c63
Type: security-commit

## Details
fix(ssa interpreter): Clarify overflow error (#12483)

## Patch
### compiler/noirc_evaluator/src/ssa/interpreter/mod.rs
```diff
@@ -1535,7 +1535,11 @@ macro_rules! apply_int_binop_opt {
         let operator = binary.operator;
 
         let overflow = || {
-            if matches!(operator, BinaryOp::Div | BinaryOp::Mod) {
+            // For `Div`/`Mod`, `checked_div`/`checked_rem` return `None` either because
+            // the divisor is zero or because the operation overflows
+            // (e.g. signed `MIN / -1`). Distinguish the two by inspecting the divisor.
+            if matches!(operator, BinaryOp::Div | BinaryOp::Mod) && rhs.convert_to_field().is_zero()
+            {
                 let lhs_id = binary.lhs;
                 let rhs_id = binary.rhs;
                 let lhs = lhs.to_string();
```

### compiler/noirc_evaluator/src/ssa/interpreter/tests/instructions.rs
```diff
@@ -315,6 +315,40 @@ fn div_zero() {
     assert!(matches!(error, InterpreterError::DivisionByZero { .. }));
 }
 
+#[test]
+fn div_signed_overflow() {
+    let error = expect_error(
+        "
+        acir(inline) fn main f0 {
+          b0():
+            v0 = div i32 2147483648, i32 4294967295
+            return v0
+        }
+    ",
+    );
+    assert!(
+        matches!(error, InterpreterError::Overflow { .. }),
+        "expected Overflow for i32::MIN / -1, got {error:?}"
+    );
+}
+
+#[test]
+fn mod_signed_overflow() {
+    let error = expect_error(
+        "
+        acir(inline) fn main f0 {
+          b0():
+            v0 = mod i32 2147483648, i32 4294967295
+            return v0
+        }
+    ",
+    );
+    assert!(
+        matches!(error, InterpreterError::Overflow { .. }),
+        "expected Overflow for i32::MIN % -1, got {error:?}"
+    );
+}
+
 #[test]
 fn r#mod() {
     let value = expect_value(
```
