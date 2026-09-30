# [?] fix: wrong error message in brillig bit shift overflow (#9702)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-09-08
Source: https://github.com/noir-lang/noir/commit/e9f2016045837187259dcbd92fad83801d5e592d
Type: security-commit

## Details
fix: wrong error message in brillig bit shift overflow (#9702)

## Patch
### acvm-repo/brillig_vm/src/arithmetic.rs
```diff
@@ -16,7 +16,7 @@ pub(crate) enum BrilligArithmeticError {
     #[error("Bit size for rhs {rhs_bit_size} does not match op bit size {op_bit_size}")]
     MismatchedRhsBitSize { rhs_bit_size: u32, op_bit_size: u32 },
     #[error("Attempted to shift by {shift_size} bits on a type of bit size {bit_size}")]
-    BitshiftOverflow { bit_size: u32, shift_size: u32 },
+    BitshiftOverflow { bit_size: u32, shift_size: u128 },
     #[error("Attempted to divide by zero")]
     DivisionByZero,
 }
@@ -179,7 +179,7 @@ pub(crate) fn evaluate_binary_int_op<F: AcirField>(
                 } else {
                     Err(BrilligArithmeticError::BitshiftOverflow {
                         bit_size: 8,
-                        shift_size: rhs as u32,
+                        shift_size: rhs as u128,
                     })
                 }
             }
@@ -188,36 +188,36 @@ pub(crate) fn evaluate_binary_int_op<F: AcirField>(
                     Ok(MemoryValue::U16(evaluate_binary_int_op_shifts(op, lhs, rhs)))
                 } else {
                     Err(BrilligArithmeticError::BitshiftOverflow {
-                        bit_size: 8,
-                        shift_size: rhs as u32,
+                        bit_size: 16,
+                        shift_size: rhs as u128,
                     })
                 }
             }
             (MemoryValue::U32(lhs), MemoryValue::U32(rhs), IntegerBitSize::U32) => {
                 if rhs < 32 {
                     Ok(MemoryValue::U32(evaluate_binary_int_op_shifts(op, lhs, rhs)))
                 } else {
-                    Err(BrilligArithmeticError::BitshiftOverflow { bit_size: 8, shift_size: rhs })
+                    Err(BrilligArithmeticError::BitshiftOverflow {
+                        bit_size: 32,
+                        shift_size: rhs as u128,
+                    })
                 }
             }
             (MemoryValue::U64(lhs), MemoryValue::U64(rhs), IntegerBitSize::U64) => {
                 if rhs < 64 {
                     Ok(MemoryValue::U64(evaluate_binary_int_op_shifts(op, lhs, rhs)))
                 } else {
                     Err(BrilligArithmeticError::BitshiftOverflow {
-                        bit_size: 8,
-                        shift_size: rhs as u32,
+                        bit_size: 64,
+                        shift_size: rhs as u128,
                     })
                 }
             }
             (MemoryValue::U128(lhs), MemoryValue::U128(rhs), IntegerBitSize::U128) => {
                 if rhs < 128 {
                     Ok(MemoryValue::U128(evaluate_binary_int_op_shifts(op, lhs, rhs)))
                 } else {
-                    Err(BrilligArithmeticError::BitshiftOverflow {
-                        bit_size: 8,
-                        shift_size: rhs as u32,
-                    })
+                    Err(BrilligArithmeticError::BitshiftOverflow { bit_size: 128, shift_size: rhs })
                 }
             }
             _ => Err(BrilligArithmeticError::MismatchedLhsBitSize {
```

### compiler/noirc_frontend/src/hir/comptime/interpreter/infix.rs
```diff
@@ -20,7 +20,8 @@ pub(super) fn evaluate_infix(
         let rhs = rhs_type.clone();
         InterpreterError::InvalidValuesForBinary { lhs, rhs, location, operator }
     };
-
+    let lhs_overflow = InterpreterError::BinaryOperationOverflow { operator: "<<", location };
+    let rhs_overflow = InterpreterError::BinaryOperationOverflow { operator: ">>", location };
     let math_error = |operator| InterpreterError::BinaryOperationOverflow { location, operator };
 
     /// Generate matches that can promote the type of one side to the other if they are compatible.
@@ -184,11 +185,20 @@ pub(super) fn evaluate_infix(
         },
         #[allow(trivial_numeric_casts)]
         BinaryOpKind::ShiftRight => match_integer! {
-            (lhs_value as lhs ">>" rhs_value as rhs) => lhs.checked_shr(rhs as u32)
+            (lhs_value as lhs ">>" rhs_value as rhs) => {
+                #[allow(unused_comparisons, clippy::absurd_extreme_comparisons)]
+                if rhs > 127 {return Err(rhs_overflow);}
+                lhs.checked_shr(rhs as u32)
+            }
         },
         #[allow(trivial_numeric_casts)]
         BinaryOpKind::ShiftLeft => match_integer! {
-            (lhs_value as lhs "<<" rhs_value as rhs) => lhs.checked_shl(rhs as u32)
+            (lhs_value as lhs "<<" rhs_value as rhs) => {
+                #[allow(unused_comparisons, clippy::absurd_extreme_comparisons)]
+                if rhs > 127 {return Err(lhs_overflow);}
+                lhs.checked_shl(
+                rhs as u32
+            )}
         },
         BinaryOpKind::Modulo => match (&lhs_value, &rhs_value) {
             (Value::I8(i8::MIN), Value::I8(-1)) => Ok(Value::I8(0)),
```
