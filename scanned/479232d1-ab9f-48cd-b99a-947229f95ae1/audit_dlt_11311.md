# [?] fix(interpreter): Do not overflow on signed checked ops (#8806)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-06-06
Source: https://github.com/noir-lang/noir/commit/851cfd208d8fadd69dfc74324405c6d72d286651
Type: security-commit

## Details
fix(interpreter): Do not overflow on signed checked ops (#8806)

## Patch
### compiler/noirc_evaluator/src/ssa/interpreter/mod.rs
```diff
@@ -877,6 +877,21 @@ impl<'ssa> Interpreter<'ssa> {
     }
 }
 
+/// Applies an infallible integer binary operation to two `NumericValue`s.
+///
+/// # Parameters
+/// - `$lhs`, `$rhs`: The left hand side and right hand side operands (must be the same variant).
+/// - `$binary`: The binary instruction, used for error handling if types mismatch.
+/// - `$f`: A function (e.g., `wrapping_add`) that applies the operation on the raw numeric types.
+///
+/// # Panics
+/// - If either operand is a [NumericValue::Field] or [NumericValue::U1] variant, this macro will panic with unreachable.
+///
+/// # Errors
+/// - If the operand types don't match, returns an [InternalError::MismatchedTypesInBinaryOperator].
+///
+/// # Returns
+/// A `NumericValue` containing the result of the operation, matching the original type.
 macro_rules! apply_int_binop {
     ($lhs:expr, $rhs:expr, $binary:expr, $f:expr) => {{
         use value::NumericValue::*;
@@ -908,6 +923,24 @@ macro_rules! apply_int_binop {
     }};
 }
 
+/// Applies a fallible integer binary operation (e.g., checked arithmetic) to two `NumericValue`s.
+///
+/// # Parameters
+/// - `$dfg`: The data flow graph, used for formatting diagnostic error messages.
+/// - `$lhs`, `$rhs`: The left-hand side and right-hand side operands (must be the same variant).
+/// - `$binary`: The binary instruction, used for diagnostics and overflow reporting.
+/// - `$f`: A fallible operation function that returns an `Option<_>` (e.g., `checked_add`).
+///
+/// # Panics
+/// - If either operand is a [NumericValue::Field]or [NumericValue::U1], this macro panics as those types are not supported.
+///
+/// # Errors
+/// - Returns [InterpreterError::Overflow] if the checked operation returns `None`.
+/// - Returns [InterpreterError::DivisionByZero] for `Div` and `Mod` on zero.
+/// - Returns [InternalError::MismatchedTypesInBinaryOperator] if the operand types don't match.
+///
+/// # Returns
+/// A `NumericValue` containing the result of the operation, or an `Err` with the appropriate error.
 macro_rules! apply_int_binop_opt {
     ($dfg:expr, $lhs:expr, $rhs:expr, $binary:expr, $f:expr) => {{
         use value::NumericValue::*;
@@ -1025,19 +1058,32 @@ impl Interpreter<'_> {
         let dfg = self.dfg();
         let result = match binary.operator {
             BinaryOp::Add { unchecked: false } => {
-                apply_int_binop_opt!(dfg, lhs, rhs, binary, num_traits::CheckedAdd::checked_add)
+                if lhs.get_type().is_unsigned() {
+                    apply_int_binop_opt!(dfg, lhs, rhs, binary, num_traits::CheckedAdd::checked_add)
+                } else {
+                    apply_int_binop!(lhs, rhs, binary, num_traits::WrappingAdd::wrapping_add)
+                }
             }
             BinaryOp::Add { unchecked: true } => {
                 apply_int_binop!(lhs, rhs, binary, num_traits::WrappingAdd::wrapping_add)
             }
             BinaryOp::Sub { unchecked: false } => {
-                apply_int_binop_opt!(dfg, lhs, rhs, binary, num_traits::CheckedSub::checked_sub)
+                if lhs.get_type().is_unsigned() {
+                    apply_int_binop_opt!(dfg, lhs, rhs, binary, num_traits::CheckedSub::checked_sub)
+                } else {
+                    apply_int_binop!(lhs, rhs, binary, num_traits::WrappingSub::wrapping_sub)
+                }
             }
             BinaryOp::Sub { unchecked: true } => {
                 apply_int_binop!(lhs, rhs, binary, num_traits::WrappingSub::wrapping_sub)
             }
             BinaryOp::Mul { unchecked: false } => {
-                apply_int_binop_opt!(dfg, lhs, rhs, binary, num_traits::CheckedMul::checked_mul)
+                // Only unsigned multiplication has side effects
+                if lhs.get_type().is_unsigned() {
+                    apply_int_binop_opt!(dfg, lhs, rhs, binary, num_traits::CheckedMul::checked_mul)
+                } else {
+                    apply_int_binop!(lhs, rhs, binary, num_traits::WrappingMul::wrapping_mul)
+                }
             }
             BinaryOp::Mul { unchecked: true } => {
                 apply_int_binop!(lhs, rhs, binary, num_traits::WrappingMul::wrapping_mul)
```

### compiler/noirc_evaluator/src/ssa/interpreter/tests/instructions.rs
```diff
@@ -18,7 +18,7 @@ use crate::ssa::{
 use super::{executes_with_no_errors, expect_error};
 
 #[test]
-fn add() {
+fn add_unsigned() {
     let value = expect_value(
         "
         acir(inline) fn main f0 {
@@ -32,7 +32,22 @@ fn add() {
 }
 
 #[test]
-fn add_overflow() {
+fn add_signed() {
+    let value = expect_value(
+        "
+        acir(inline) fn main f0 {
+          b0():
+            v0 = add i32 2, i32 100
+            v1 = truncate v0 to 32 bits, max_bit_size: 33
+            return v1
+        }
+    ",
+    );
+    assert_eq!(value, Value::Numeric(NumericValue::I32(102)));
+}
+
+#[test]
+fn add_overflow_unsigned() {
     let error = expect_error(
         "
         acir(inline) fn main f0 {
@@ -46,7 +61,22 @@ fn add_overflow() {
 }
 
 #[test]
-fn add_unchecked() {
+fn add_overflow_signed() {
+    let value = expect_value(
+        "
+        acir(inline) fn main f0 {
+          b0():
+            v0 = add i8 2, i8 127
+            v1 = truncate v0 to 8 bits, max_bit_size: 9
+            return v1
+        }
+    ",
+    );
+    assert_eq!(value, Value::Numeric(NumericValue::I8(-127)));
+}
+
+#[test]
+fn add_unchecked_unsigned() {
     executes_with_no_errors(
         "
         acir(inline) fn main f0 {
@@ -59,7 +89,21 @@ fn add_unchecked() {
 }
 
 #[test]
-fn sub() {
+fn add_unchecked_signed() {
+    let value = expect_value(
+        "
+        acir(inline) fn main f0 {
+          b0():
+            v0 = unchecked_add i8 2, i8 127
+            return v0
+        }
+    ",
+    );
+    assert_eq!(value, Value::Numeric(NumericValue::I8(-127)));
+}
+
+#[test]
+fn sub_unsigned() {
     let value = expect_value(
         "
         acir(inline) fn main f0 {
@@ -73,12 +117,27 @@ fn sub() {
 }
 
 #[test]
-fn sub_underflow() {
+fn sub_signed() {
+    let value = expect_value(
+        "
+        acir(inline) fn main f0 {
+          b0():
+            v0 = sub i32 10101, i32 10102
+            v1 = truncate v0 to 32 bits, max_bit_size: 33
+            return v0
+        }
+    ",
+    );
+    assert_eq!(value, Value::Numeric(NumericValue::I32(-1)));
+}
+
+#[test]
+fn sub_underflow_unsigned() {
     let error = expect_error(
         "
         acir(inline) fn main f0 {
           b0():
-            v0 = sub i8 136, i8 10  // -120 - 10
+            v0 = sub u8 0, u8 10  // 0 - 10
             v1 = truncate v0 to 8 bits, max_bit_size: 9
             return v1
         }
@@ -88,7 +147,39 @@ fn sub_underflow() {
 }
 
 #[test]
-fn sub_unchecked() {
+fn sub_underflow_signed() {
+    let value = expect_value(
+        "
+        acir(inline) fn main f0 {
+          b0():
+            v0 = sub i8 136, i8 10  // -120 - 10
+            v1 = truncate v0 to 8 bits, max_bit_size: 9
+            return v1
+        }
+    ",
+    );
+    // Expected wrapping sub:
+    // i8 can only be -128 to 127
+    // -120 - 10 = -130 = 126
+    assert!(matches!(value, Value::Numeric(NumericValue::I8(126))));
+}
+
+#[test]
+fn sub_unchecked_unsigned() {
+    let value = expect_value(
+        "
+        acir(inline) fn main f0 {
+          b0():
+            v0 = unchecked_sub u8 0, u8 10  // 0 - 10
+            return v0
+        }
+    ",
+    );
+    assert!(matches!(value, Value::Numeric(NumericValue::U8(246))));
+}
+
+#[test]
+fn sub_unchecked_signed() {
     let value = expect_value(
         "
         acir(inline) fn main f0 {
@@ -102,7 +193,7 @@ fn sub_unchecked() {
 }
 
 #[test]
-fn mul() {
+fn mul_unsigned() {
     let value = expect_value(
         "
         acir(inline) fn main f0 {
@@ -116,7 +207,21 @@ fn mul() {
 }
 
 #[test]
-fn mul_overflow() {
+fn mul_signed() {
+    let value = expect_value(
+        "
+        acir(inline) fn main f0 {
+          b0():
+            v0 = mul i64 2, i64 100
+            return v0
+        }
+    ",
+    );
+    assert_eq!(value, Value::Numeric(NumericValue::I64(200)));
+}
+
+#[test]
+fn mul_overflow_unsigned() {
     let error = expect_error(
         "
         acir(inline) fn main f0 {
@@ -130,7 +235,21 @@ fn mul_overflow() {
 }
 
 #[test]
-fn mul_unchecked() {
+fn mul_overflow_signed() {
+    let value = expect_value(
+        "
+        acir(inline) fn main f0 {
+          b0():
+            v0 = mul i8 127, i8 2
+            return v0
+        }
+    ",
+    );
+    assert_eq!(value, Value::Numeric(NumericValue::I8(-2)));
+}
+
+#[test]
+fn mul_unchecked_unsigned() {
     let value = expect_value(
         "
         acir(inline) fn main f0 {
@@ -143,6 +262,20 @@ fn mul_unchecked() {
     assert_eq!(value, Value::Numeric(NumericValue::U8(0)));
 }
 
+#[test]
+fn mul_unchecked_signed() {
+    let value = expect_value(
+        "
+        acir(inline) fn main f0 {
+          b0():
+            v0 = unchecked_mul i8 127, i8 2
+            return v0
+        }
+    ",
+    );
+    assert_eq!(value, Value::Numeric(NumericValue::I8(-2)));
+}
+
 #[test]
 fn div() {
     let value = expect_value(
```

### cspell.json
```diff
@@ -25,6 +25,7 @@
         "bignum",
         "bincode",
         "bindgen",
+        "binop",
         "bitand",
         "bitmask",
         "bitshift",
```
