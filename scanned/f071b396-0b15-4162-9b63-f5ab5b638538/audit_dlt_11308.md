# [?] fix(comptime): Overflow on shl  (#8829)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-06-07
Source: https://github.com/noir-lang/noir/commit/57ec192fdd2c21fa11d1b66a74f586ac43b936d0
Type: security-commit

## Details
fix(comptime): Overflow on shl  (#8829)

## Patch
### compiler/noirc_frontend/src/hir/comptime/interpreter/infix.rs
```diff
@@ -214,7 +214,7 @@ pub(super) fn evaluate_infix(
             }
         }
         BinaryOpKind::ShiftLeft => match_bitshift! {
-            (lhs_value as lhs "<<" rhs_value as rhs) => lhs.checked_shl(rhs.into()).or(Some(0))
+            (lhs_value as lhs "<<" rhs_value as rhs) => lhs.checked_shl(rhs.into())
         },
         BinaryOpKind::Modulo => match_integer! {
             (lhs_value as lhs "%" rhs_value as rhs) => lhs.checked_rem(rhs)
@@ -224,7 +224,8 @@ pub(super) fn evaluate_infix(
 
 #[cfg(test)]
 mod test {
-    use crate::hir::comptime::tests::interpret;
+    use crate::hir::comptime::InterpreterError;
+    use crate::hir::comptime::tests::{interpret, interpret_expect_error};
 
     use super::{BinaryOpKind, HirBinaryOp, Location, Value};
 
@@ -242,6 +243,58 @@ mod test {
         assert_eq!(result, Value::U128(170141183460469231731687303715884105727));
     }
 
+    #[test]
+    fn shl_unsigned() {
+        let src = r#"
+            comptime fn main() -> pub u64 {
+                3 << 4
+            }
+        "#;
+        let result = interpret(src);
+        assert_eq!(result, Value::U64(48));
+    }
+
+    #[test]
+    fn shl_signed() {
+        let src = r#"
+            comptime fn main() -> pub i64 {
+                2 << 3
+            }
+        "#;
+        let result = interpret(src);
+        assert_eq!(result, Value::I64(16));
+    }
+
+    #[test]
+    fn shl_unsigned_overflow() {
+        let src = r#"
+            comptime fn main() -> pub u64 {
+                1 << 128
+            }
+        "#;
+
+        let err = interpret_expect_error(src);
+        let InterpreterError::MathError { operator, .. } = err else {
+            panic!("Expected overflow error");
+        };
+        assert_eq!(operator, "<<");
+    }
+
+    #[test]
+    fn shl_signed_overflow() {
+        let src = r#"
+            comptime fn main() -> pub i64 {
+                1 << 64
+            }
+        "#;
+
+        let err = interpret_expect_error(src);
+        let InterpreterError::MathError { operator, .. } = err else {
+            panic!("Expected overflow error");
+        };
+        assert_eq!(operator, "<<");
+    }
+
     #[test]
     fn shr_unsigned() {
         let src = r#"
```
