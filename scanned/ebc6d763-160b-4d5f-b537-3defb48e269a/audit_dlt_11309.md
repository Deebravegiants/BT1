# [?] fix(interpreter): Return -1 for negative shr signed overflow or 0 for positive shr signed overflow (#8828)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-06-07
Source: https://github.com/noir-lang/noir/commit/522d4c185601ae2b9f5b677cb95df7a7644cfd26
Type: security-commit

## Details
fix(interpreter): Return -1 for negative shr signed overflow or 0 for positive shr signed overflow (#8828)

## Patch
### EXTERNAL_NOIR_LIBRARIES.yml
```diff
@@ -71,7 +71,7 @@ libraries:
     repo: AztecProtocol/aztec-packages
     ref: *AZ_COMMIT
     path: noir-projects/aztec-nr
-    timeout: 70
+    timeout: 75
     critical: false
   noir_contracts:
     repo: AztecProtocol/aztec-packages
```

### compiler/noirc_evaluator/src/ssa/interpreter/mod.rs
```diff
@@ -1137,7 +1137,14 @@ impl Interpreter<'_> {
                 }
             }
             BinaryOp::Shr => {
-                let zero = || NumericValue::zero(lhs.get_type());
+                let fallback = || {
+                    if lhs.is_negative() {
+                        NumericValue::neg_one(lhs.get_type())
+                    } else {
+                        NumericValue::zero(lhs.get_type())
+                    }
+                };
+
                 let Some(rhs) = rhs.as_u8() else {
                     let rhs = rhs.to_string();
                     return Err(internal(InternalError::RhsOfBitShiftShouldBeU8 {
@@ -1157,15 +1164,15 @@ impl Interpreter<'_> {
                         }));
                     }
                     U1(value) => U1(if rhs == 0 { value } else { false }),
-                    U8(value) => value.checked_shr(rhs).map(U8).unwrap_or_else(zero),
-                    U16(value) => value.checked_shr(rhs).map(U16).unwrap_or_else(zero),
-                    U32(value) => value.checked_shr(rhs).map(U32).unwrap_or_else(zero),
-                    U64(value) => value.checked_shr(rhs).map(U64).unwrap_or_else(zero),
-                    U128(value) => value.checked_shr(rhs).map(U128).unwrap_or_else(zero),
-                    I8(value) => value.checked_shr(rhs).map(I8).unwrap_or_else(zero),
-                    I16(value) => value.checked_shr(rhs).map(I16).unwrap_or_else(zero),
-                    I32(value) => value.checked_shr(rhs).map(I32).unwrap_or_else(zero),
-                    I64(value) => value.checked_shr(rhs).map(I64).unwrap_or_else(zero),
+                    U8(value) => value.checked_shr(rhs).map(U8).unwrap_or_else(fallback),
+                    U16(value) => value.checked_shr(rhs).map(U16).unwrap_or_else(fallback),
+                    U32(value) => value.checked_shr(rhs).map(U32).unwrap_or_else(fallback),
+                    U64(value) => value.checked_shr(rhs).map(U64).unwrap_or_else(fallback),
+                    U128(value) => value.checked_shr(rhs).map(U128).unwrap_or_else(fallback),
+                    I8(value) => value.checked_shr(rhs).map(I8).unwrap_or_else(fallback),
+                    I16(value) => value.checked_shr(rhs).map(I16).unwrap_or_else(fallback),
+                    I32(value) => value.checked_shr(rhs).map(I32).unwrap_or_else(fallback),
+                    I64(value) => value.checked_shr(rhs).map(I64).unwrap_or_else(fallback),
                 }
             }
         };
```

### compiler/noirc_evaluator/src/ssa/interpreter/tests/instructions.rs
```diff
@@ -10,6 +10,7 @@ use crate::ssa::{
         value::ReferenceValue,
     },
     ir::{
+        integer::IntegerConstant,
         types::{NumericType, Type},
         value::ValueId,
     },
@@ -449,7 +450,7 @@ fn shl_overflow() {
 }
 
 #[test]
-fn shr() {
+fn shr_unsigned() {
     let values = expect_values(
         "
         acir(inline) fn main f0 {
@@ -467,8 +468,33 @@ fn shr() {
 }
 
 #[test]
-/// shr does not error on overflow. It just returns 0. See https://github.com/noir-lang/noir/pull/7509.
-fn shr_overflow() {
+fn shr_signed() {
+    let values = expect_values(
+        "
+        acir(inline) fn main f0 {
+          b0():
+            v0 = shr i16 65520, u8 2      
+            v1 = shr i16 65533, u8 1      
+            v2 = shr i16 65528, u8 3 
+            return v0, v1, v2
+        }
+    ",
+    );
+
+    let neg_four = IntegerConstant::Signed { value: -4, bit_size: 16 };
+    let (neg_four_constant, typ) = neg_four.into_numeric_constant();
+    assert_eq!(values[0], from_constant(neg_four_constant, typ));
+    let neg_two = IntegerConstant::Signed { value: -2, bit_size: 16 };
+    let (neg_two_constant, typ) = neg_two.into_numeric_constant();
+    assert_eq!(values[1], from_constant(neg_two_constant, typ));
+    let neg_one = IntegerConstant::Signed { value: -1, bit_size: 16 };
+    let (neg_one_constant, typ) = neg_one.into_numeric_constant();
+    assert_eq!(values[2], from_constant(neg_one_constant, typ));
+}
+
+#[test]
+/// shr on unsigned integer does not error on overflow. It just returns 0. See https://github.com/noir-lang/noir/pull/7509.
+fn shr_overflow_unsigned() {
     let value = expect_value(
         "
         acir(inline) fn main f0 {
@@ -481,6 +507,44 @@ fn shr_overflow() {
     assert_eq!(value, from_constant(0_u128.into(), NumericType::unsigned(8)));
 }
 
+#[test]
+/// shr on signed integers does not error on overflow.
+/// If the value being shifted is positive we return 0, and -1 if it is negative.
+/// See https://github.com/noir-lang/noir/pull/8805.
+fn shr_overflow_signed_negative_lhs() {
+    let value = expect_value(
+        "
+        acir(inline) fn main f0 {
+          b0():
+            v0 = shr i8 192, u8 9
+            return v0
+        }
+    ",
+    );
+
+    let neg_one = IntegerConstant::Signed { value: -1, bit_size: 8 };
+    let (neg_one_constant, typ) = neg_one.into_numeric_constant();
+    assert_eq!(value, from_constant(neg_one_constant, typ));
+}
+
+#[test]
+/// shr on signed integers does not error on overflow.
+/// If the value being shifted is positive we return 0, and -1 if it is negative.
+/// See https://github.com/noir-lang/noir/pull/8805.
+fn shr_overflow_signed_positive_lhs() {
+    let value = expect_value(
+        "
+        acir(inline) fn main f0 {
+          b0():
+            v0 = shr i8 1, u8 255
+            return v0
+        }
+    ",
+    );
+
+    assert_eq!(value, Value::Numeric(NumericValue::I8(0)));
+}
+
 #[test]
 fn cast() {
     let values = expect_values(
```

### compiler/noirc_evaluator/src/ssa/interpreter/value.rs
```diff
@@ -7,6 +7,7 @@ use noirc_frontend::Shared;
 use crate::ssa::ir::{
     function::FunctionId,
     instruction::Intrinsic,
+    integer::IntegerConstant,
     types::{CompositeType, NumericType, Type},
     value::ValueId,
 };
@@ -256,6 +257,13 @@ impl NumericValue {
         Self::from_constant(FieldElement::zero(), typ).expect("zero should fit in every type")
     }
 
+    pub(crate) fn neg_one(typ: NumericType) -> Self {
+        let neg_one = IntegerConstant::Signed { value: -1, bit_size: typ.bit_size() };
+        let (neg_one_constant, typ) = neg_one.into_numeric_constant();
+        Self::from_constant(neg_one_constant, typ)
+            .unwrap_or_else(|_| panic!("Negative one cannot fit in {typ}"))
+    }
+
     pub(crate) fn as_field(&self) -> Option<FieldElement> {
         match self {
             NumericValue::Field(value) => Some(*value),
@@ -360,6 +368,16 @@ impl NumericValue {
             NumericValue::I64(value) => FieldElement::from(*value as u64 as i128),
         }
     }
+
+    pub fn is_negative(&self) -> bool {
+        match self {
+            NumericValue::I8(v) => *v < 0,
+            NumericValue::I16(v) => *v < 0,
+            NumericValue::I32(v) => *v < 0,
+            NumericValue::I64(v) => *v < 0,
+            _ => false,
+        }
+    }
 }
 
 impl std::fmt::Display for Value {
```

### compiler/noirc_evaluator/src/ssa/opt/remove_bit_shifts.rs
```diff
@@ -230,7 +230,7 @@ impl Context<'_, '_, '_> {
         );
         let minus_one_or_zero =
             self.insert_binary(minus_one, BinaryOp::Mul { unchecked: true }, lhs_sign_as_int);
-        // -1, or 0 if lhs is positve or if there is no overflow
+        // -1, or 0 if lhs is positive or if there is no overflow
         let one = self.numeric_constant(FieldElement::one(), lhs_typ);
         let no_overflow = self.insert_binary(
             one,
```

### compiler/noirc_frontend/src/hir/comptime/interpreter/infix.rs
```diff
@@ -195,9 +195,24 @@ pub(super) fn evaluate_infix(
         BinaryOpKind::Xor => match_bitwise! {
             (lhs_value as lhs "^" rhs_value as rhs) => lhs ^ rhs
         },
-        BinaryOpKind::ShiftRight => match_bitshift! {
-            (lhs_value as lhs ">>" rhs_value as rhs) => Some(lhs.wrapping_shr(rhs.into()))
-        },
+        BinaryOpKind::ShiftRight => {
+            let is_negative = lhs_value.is_negative();
+            match_bitshift! {
+                (lhs_value as lhs ">>" rhs_value as rhs) => {
+                    Some(
+                        lhs.checked_shr(rhs.into())
+                            .unwrap_or(
+                                // fallback based on whether we have a negative value
+                                if is_negative {
+                                    // !0 = -1 for signed types
+                                    !0
+                                } else {
+                                    0
+                                })
+                    )
+                }
+            }
+        }
         BinaryOpKind::ShiftLeft => match_bitshift! {
             (lhs_value as lhs "<<" rhs_value as rhs) => lhs.checked_shl(rhs.into()).or(Some(0))
         },
@@ -209,6 +224,8 @@ pub(super) fn evaluate_infix(
 
 #[cfg(test)]
 mod test {
+    use crate::hir::comptime::tests::interpret;
+
     use super::{BinaryOpKind, HirBinaryOp, Location, Value};
 
     use super::evaluate_infix;
@@ -224,4 +241,109 @@ mod test {
 
         assert_eq!(result, Value::U128(170141183460469231731687303715884105727));
     }
+
+    #[test]
+    fn shr_unsigned() {
+        let src = r#"
+            comptime fn main() -> pub u64 {
+                64 >> 1
+            }
+        "#;
+        let result = interpret(src);
+        assert_eq!(result, Value::U64(32));
+    }
+
+    #[test]
+    fn shr_unsigned_overflow() {
+        let src = r#"
+            comptime fn main() -> pub u64 {
+                64 >> 63
+            }
+        "#;
+        let result = interpret(src);
+        assert_eq!(result, Value::U64(0));
+
+        let src = r#"
+            comptime fn main() -> pub u64 {
+                64 >> 255
+            }
+        "#;
+        let result = interpret(src);
+        // 255 % 64 == 63, so 64 >> 63 => 0
+        assert_eq!(result, Value::U64(0));
+
+        let src = "
+            comptime fn main() -> pub u32 {
+                1360887544 >> 141
+            }
+        ";
+        let result = interpret(src);
+        assert_eq!(result, Value::U32(0));
+    }
+
+    #[test]
+    fn shr_signed_overflow_negative_lhs() {
+        let src = "
+        comptime fn main() -> pub i64 {
+            -64 >> 63
+        }
+        ";
+        let result = interpret(src);
+        assert_eq!(result, Value::I64(-1));
+
+        let src = "
+        comptime fn main() -> pub i64 {
+            -64 >> 255
+        }
+        ";
+        let result = interpret(src);
+        // 255 % 64 == 63, so 64 >> 63 => -1
+        assert_eq!(result, Value::I64(-1));
+
+        let src = "
+        comptime fn main() -> pub i32 {
+            -1360887544 >> 141
+        }
+        ";
+        let result = interpret(src);
+        assert_eq!(result, Value::I32(-1));
+    }
+
+    #[test]
+    fn shr_signed_overflow_positive_lhs() {
+        let src = "
+        comptime fn main() -> pub i64 {
+            64 >> 63
+        }
+        ";
+        let result = interpret(src);
+        assert_eq!(result, Value::I64(0));
+
+        let src = "
+        comptime fn main() -> pub i64 {
+            64 >> 255
+        }
+        ";
+        let result = interpret(src);
+        assert_eq!(result, Value::I64(0));
+
+        let src = "
+        comptime fn main() -> pub i32 {
+            1360887544 >> 141
+        }
+        ";
+        let result = interpret(src);
+        assert_eq!(result, Value::I32(0));
+    }
+
+    #[test]
+    fn shr_signed() {
+        let src = r#"
+            comptime fn main() -> pub i64 {
+                -64 >> 1
+            }
+        "#;
+        let result = interpret(src);
+        assert_eq!(result, Value::I64(-32));
+    }
 }
```

### compiler/noirc_frontend/src/hir/comptime/tests.rs
```diff
@@ -79,13 +79,13 @@ fn interpret_helper(src: &str) -> Result<Value, InterpreterError> {
     })
 }
 
-fn interpret(src: &str) -> Value {
+pub(super) fn interpret(src: &str) -> Value {
     interpret_helper(src).unwrap_or_else(|error| {
         panic!("Expected interpreter to exit successfully, but found {error:?}")
     })
 }
 
-fn interpret_expect_error(src: &str) -> InterpreterError {
+pub(super) fn interpret_expect_error(src: &str) -> InterpreterError {
     interpret_helper(src).expect_err("Expected interpreter to error")
 }
 
```

### compiler/noirc_frontend/src/hir/comptime/value.rs
```diff
@@ -627,6 +627,16 @@ impl Value {
             }
         }
     }
+
+    pub fn is_negative(&self) -> bool {
+        match self {
+            Value::I8(x) => *x < 0,
+            Value::I16(x) => *x < 0,
+            Value::I32(x) => *x < 0,
+            Value::I64(x) => *x < 0,
+            _ => false, // Unsigned or Field types are never negative
+        }
+    }
 }
 
 /// Unwraps an Rc value without cloning the inner value if the reference count is 1. Clones otherwise.
```

### tooling/nargo_cli/tests/snapshots/compile_success_no_bug/comptime_right_shift_no_overflow/execute__tests__expanded.snap
```diff
@@ -3,6 +3,6 @@ source: tooling/nargo_cli/tests/execute.rs
 expression: expanded_code
 ---
 fn main(x: Field) -> pub Field {
-    let y: Field = 1;
+    let y: Field = 0;
     x + y
 }
```
