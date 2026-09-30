# [?] fix(ssa interpreter): Default to zero when we have an overflowing shl (#8638)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-05-22
Source: https://github.com/noir-lang/noir/commit/23d7409f37630b4268b60b0511338b0d0d5b5df6
Type: security-commit

## Details
fix(ssa interpreter): Default to zero when we have an overflowing shl (#8638)

## Patch
### compiler/noirc_evaluator/src/ssa/interpreter/mod.rs
```diff
@@ -1069,12 +1069,6 @@ impl Interpreter<'_> {
                     }));
                 };
 
-                let overflow = || {
-                    let instruction =
-                        format!("`{}` ({lhs} << {rhs})", display_binary(binary, self.dfg()));
-                    InterpreterError::Overflow { instruction }
-                };
-
                 let rhs = rhs as u32;
                 use NumericValue::*;
                 match lhs {
@@ -1084,22 +1078,16 @@ impl Interpreter<'_> {
                             typ: "Field",
                         }));
                     }
-                    U1(value) => {
-                        if rhs == 0 {
-                            U1(value)
-                        } else {
-                            return Err(overflow());
-                        }
-                    }
-                    U8(value) => U8(value.checked_shl(rhs).ok_or_else(overflow)?),
-                    U16(value) => U16(value.checked_shl(rhs).ok_or_else(overflow)?),
-                    U32(value) => U32(value.checked_shl(rhs).ok_or_else(overflow)?),
-                    U64(value) => U64(value.checked_shl(rhs).ok_or_else(overflow)?),
-                    U128(value) => U128(value.checked_shl(rhs).ok_or_else(overflow)?),
-                    I8(value) => I8(value.checked_shl(rhs).ok_or_else(overflow)?),
-                    I16(value) => I16(value.checked_shl(rhs).ok_or_else(overflow)?),
-                    I32(value) => I32(value.checked_shl(rhs).ok_or_else(overflow)?),
-                    I64(value) => I64(value.checked_shl(rhs).ok_or_else(overflow)?),
+                    U1(value) => U1(if rhs == 0 { value } else { false }),
+                    U8(value) => U8(value.checked_shl(rhs).unwrap_or(0)),
+                    U16(value) => U16(value.checked_shl(rhs).unwrap_or(0)),
+                    U32(value) => U32(value.checked_shl(rhs).unwrap_or(0)),
+                    U64(value) => U64(value.checked_shl(rhs).unwrap_or(0)),
+                    U128(value) => U128(value.checked_shl(rhs).unwrap_or(0)),
+                    I8(value) => I8(value.checked_shl(rhs).unwrap_or(0)),
+                    I16(value) => I16(value.checked_shl(rhs).unwrap_or(0)),
+                    I32(value) => I32(value.checked_shl(rhs).unwrap_or(0)),
+                    I64(value) => I64(value.checked_shl(rhs).unwrap_or(0)),
                 }
             }
             BinaryOp::Shr => {
```

### compiler/noirc_evaluator/src/ssa/interpreter/tests/instructions.rs
```diff
@@ -299,10 +299,10 @@ fn shl() {
     assert_eq!(value, from_constant(12_u128.into(), NumericType::signed(8)));
 }
 
-/// shl should overflow if the rhs is greater than the bit count
+/// shl does not error on overflow. It just returns zero.
 #[test]
 fn shl_overflow() {
-    let error = expect_error(
+    let value = expect_value(
         "
         acir(inline) fn main f0 {
           b0():
@@ -311,7 +311,7 @@ fn shl_overflow() {
         }
     ",
     );
-    assert!(matches!(error, InterpreterError::Overflow { .. }));
+    assert_eq!(value, from_constant(0_u128.into(), NumericType::unsigned(8)));
 }
 
 #[test]
@@ -333,7 +333,7 @@ fn shr() {
 }
 
 #[test]
-/// Unlike shl, shr does not error on overflow. It just returns 0. See https://github.com/noir-lang/noir/pull/7509.
+/// shr does not error on overflow. It just returns 0. See https://github.com/noir-lang/noir/pull/7509.
 fn shr_overflow() {
     let value = expect_value(
         "
```

### compiler/noirc_frontend/src/hir/comptime/interpreter/infix.rs
```diff
@@ -200,7 +200,7 @@ pub(super) fn evaluate_infix(
             (lhs_value as lhs ">>" rhs_value as rhs) => lhs.checked_shr(rhs.into()).or(Some(0))
         },
         BinaryOpKind::ShiftLeft => match_bitshift! {
-            (lhs_value as lhs "<<" rhs_value as rhs) => lhs.checked_shl(rhs.into())
+            (lhs_value as lhs "<<" rhs_value as rhs) => lhs.checked_shl(rhs.into()).or(Some(0))
         },
         BinaryOpKind::Modulo => match_integer! {
             (lhs_value as lhs "%" rhs_value as rhs) => lhs.checked_rem(rhs)
```
