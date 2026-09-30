# [?] fix: signed division by -1 can overflow (#9976)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-09-26
Source: https://github.com/noir-lang/noir/commit/8ca4af784ce805900a8d5472830c9c28e92562b8
Type: security-commit

## Details
fix: signed division by -1 can overflow (#9976)

## Patch
### compiler/noirc_evaluator/src/acir/acir_context/mod.rs
```diff
@@ -1166,8 +1166,10 @@ impl<F: AcirField> AcirContext<F> {
         let assert_message =
             self.generate_assertion_message_payload("Attempt to divide with overflow".to_string());
         let unsigned = self.not_var(q_sign, AcirType::unsigned(1))?;
-        // We just use `unsigned` for the predicate of assert_neq_var because if the `predicate` is false, the quotient
-        // we get from the unsigned division under the predicate will not be 2^{bit_size-1} anyways.
+
+        // This overflow check must also be under the predicate
+        let unsigned = self.mul_var(unsigned, predicate)?;
+
         self.assert_neq_var(quotient, max_power_of_two, unsigned, Some(assert_message))?;
 
         Ok((quotient, remainder))
```

### compiler/noirc_evaluator/src/ssa/interpreter/mod.rs
```diff
@@ -1338,30 +1338,20 @@ fn evaluate_binary(
         BinaryOp::Mul { unchecked: true } => {
             apply_int_binop!(lhs, rhs, binary, num_traits::WrappingMul::wrapping_mul)
         }
-        BinaryOp::Div => {
-            apply_int_binop_opt!(
-                lhs,
-                rhs,
-                binary,
-                num_traits::CheckedDiv::checked_div,
-                display_binary
-            )
-        }
-        BinaryOp::Mod => match (lhs, rhs) {
-            (NumericValue::I8(i8::MIN), NumericValue::I8(-1)) => NumericValue::I8(0),
-            (NumericValue::I16(i16::MIN), NumericValue::I16(-1)) => NumericValue::I16(0),
-            (NumericValue::I32(i32::MIN), NumericValue::I32(-1)) => NumericValue::I32(0),
-            (NumericValue::I64(i64::MIN), NumericValue::I64(-1)) => NumericValue::I64(0),
-            _ => {
-                apply_int_binop_opt!(
-                    lhs,
-                    rhs,
-                    binary,
-                    num_traits::CheckedRem::checked_rem,
-                    display_binary
-                )
-            }
-        },
+        BinaryOp::Div => apply_int_binop_opt!(
+            lhs,
+            rhs,
+            binary,
+            num_traits::CheckedDiv::checked_div,
+            display_binary
+        ),
+        BinaryOp::Mod => apply_int_binop_opt!(
+            lhs,
+            rhs,
+            binary,
+            num_traits::CheckedRem::checked_rem,
+            display_binary
+        ),
         BinaryOp::Eq => apply_int_comparison_op!(lhs, rhs, binary, |a, b| a == b),
         BinaryOp::Lt => apply_int_comparison_op!(lhs, rhs, binary, |a, b| a < b),
         BinaryOp::And => {
```

### compiler/noirc_evaluator/src/ssa/interpreter/tests/instructions.rs
```diff
@@ -336,21 +336,6 @@ fn mod_zero() {
     assert!(matches!(error, InterpreterError::DivisionByZero { .. }));
 }
 
-#[test]
-fn regression_9336() {
-    let result = expect_value_with_args(
-        "
-        acir(inline) fn main f0 {
-          b0(v0: i8):
-            v1 = mod i8 -128, v0
-            return v1
-        }
-    ",
-        vec![Value::Numeric(NumericValue::I8(-1))],
-    );
-    assert_eq!(result, Value::Numeric(NumericValue::I8(0)));
-}
-
 #[test]
 fn eq() {
     let value = expect_value(
```

### compiler/noirc_evaluator/src/ssa/ir/instruction.rs
```diff
@@ -10,7 +10,7 @@ use acvm::{
 use iter_extended::vecmap;
 use noirc_frontend::hir_def::types::Type as HirType;
 
-use crate::ssa::opt::pure::Purity;
+use crate::ssa::{ir::integer::IntegerConstant, opt::pure::Purity};
 
 use super::{
     basic_block::BasicBlockId,
@@ -534,7 +534,28 @@ impl Instruction {
                     !matches!(typ, Type::Numeric(NumericType::NativeField))
                 }
                 BinaryOp::Div | BinaryOp::Mod => {
-                    dfg.get_numeric_constant(binary.rhs).is_none_or(|c| c.is_zero())
+                    // If we don't know rhs at compile time, it might be zero or -1
+                    let Some(rhs) = dfg.get_numeric_constant(binary.rhs) else {
+                        return true;
+                    };
+
+                    // Div or mod by zero is a side effect (failure)
+                    if rhs.is_zero() {
+                        return true;
+                    }
+
+                    // For signed types, division or modulo by -1 can overflow.
+                    let typ = dfg.type_of_value(binary.rhs).unwrap_numeric();
+                    let NumericType::Signed { bit_size } = typ else {
+                        return false;
+                    };
+
+                    let minus_one = IntegerConstant::Signed { value: -1, bit_size };
+                    if IntegerConstant::from_numeric_constant(rhs, typ) == Some(minus_one) {
+                        return true;
+                    }
+
+                    false
                 }
                 BinaryOp::Shl | BinaryOp::Shr => {
                     // Bit-shifts which are known to be by a number of bits less than the bit size of the type have no side effects.
```

### compiler/noirc_evaluator/src/ssa/ir/instruction/binary.rs
```diff
@@ -192,6 +192,24 @@ pub(crate) fn eval_constant_binary_op(
             let Some(rhs) = try_convert_field_element_to_signed_integer(rhs, bit_size) else {
                 return CouldNotEvaluate;
             };
+
+            let two_pow_bit_size_minus_one = 1i128 << (bit_size - 1);
+
+            // Because we always perform signed operations using i128, an operation like `-128_i8 / -1`
+            // will not overflow as it'll actually be done via `-128_i128 / -1`. Thus we need to
+            // manually check this specific case.
+            if matches!(operator, BinaryOp::Div | BinaryOp::Mod) && rhs == -1 {
+                assert!(bit_size < 128);
+                let min_value = -two_pow_bit_size_minus_one;
+                if lhs == min_value {
+                    return Failure(if operator == BinaryOp::Div {
+                        "attempt to divide with overflow".to_string()
+                    } else {
+                        "attempt to calculate the remainder with overflow".to_string()
+                    });
+                }
+            }
+
             let result = function(lhs, rhs);
 
             let result = {
@@ -212,7 +230,6 @@ pub(crate) fn eval_constant_binary_op(
                 }
 
                 // Check for overflow
-                let two_pow_bit_size_minus_one = 1i128 << (bit_size - 1);
                 let Some(result) = result else {
                     if let BinaryOp::Shl = operator {
                         return CouldNotEvaluate;
```

### compiler/noirc_evaluator/src/ssa/ir/integer.rs
```diff
@@ -95,6 +95,13 @@ impl IntegerConstant {
         }
     }
 
+    pub(crate) fn is_minus_one(&self) -> bool {
+        match self {
+            Self::Signed { value, .. } => *value == -1,
+            Self::Unsigned { .. } => false,
+        }
+    }
+
     pub(crate) fn is_negative(&self) -> bool {
         match self {
             Self::Signed { value, .. } => value.is_negative(),
```

### compiler/noirc_evaluator/src/ssa/opt/loop_invariant.rs
```diff
@@ -2382,6 +2382,35 @@ mod test {
         assert_ssa_does_not_change(src, Ssa::loop_invariant_code_motion);
     }
 
+    #[test]
+    fn do_not_hoist_signed_div_by_minus_one_from_non_executed_nested_loop() {
+        let src = r#"
+          brillig(inline) predicate_pure fn main f0 {
+            b0():
+              jmp b1(i32 0)
+            b1(v0: i32):
+              v4 = lt v0, i32 10
+              jmpif v4 then: b2, else: b3
+            b2():
+              jmp b4(i32 10)
+            b3():
+              return
+            b4(v1: i32):
+              v6 = lt v1, i32 10
+              jmpif v6 then: b5, else: b6
+            b5():
+              v9 = div v0, i32 -1
+              v10 = unchecked_add v1, i32 1
+              jmp b4(v10)
+            b6():
+              v8 = unchecked_add v0, i32 1
+              jmp b1(v8)
+          }
+        "#;
+
+        assert_ssa_does_not_change(src, Ssa::loop_invariant_code_motion);
+    }
+
     /// Test that in itself `MakeArray` is only safe to be hoisted in ACIR.
     #[test_case(RuntimeType::Brillig(InlineType::default()), CanBeHoistedResult::WithRefCount)]
     #[test_case(RuntimeType::Acir(InlineType::default()), CanBeHoistedResult::Yes)]
```

### compiler/noirc_evaluator/src/ssa/opt/loop_invariant/simplify.rs
```diff
@@ -36,7 +36,7 @@ impl LoopInvariantContext<'_> {
 
                 if left {
                     // If the induction variable is on the LHS, we're dividing with a constant.
-                    if !value.is_zero() {
+                    if !value.is_zero() && !value.is_minus_one() {
                         return true;
                     }
                 } else {
```

### compiler/noirc_frontend/src/hir/comptime/errors.rs
```diff
@@ -512,6 +512,8 @@ impl<'a> From<&'a InterpreterError> for CustomDiagnostic {
             InterpreterError::InvalidValuesForBinary { lhs, rhs, operator, location } => {
                 let msg = if *operator == "/" {
                     "Attempt to divide by zero".to_string()
+                } else if *operator == "%" {
+                    "Attempt to calculate the remainder with a divisor of zero".to_string()
                 } else {
                     format!("No implementation for `{lhs}` {operator} `{rhs}`")
                 };
```

### compiler/noirc_frontend/src/hir/comptime/interpreter/infix.rs
```diff
@@ -23,14 +23,16 @@ pub(super) fn evaluate_infix(
     let lhs_overflow = InterpreterError::BinaryOperationOverflow { operator: "<<", location };
     let rhs_overflow = InterpreterError::BinaryOperationOverflow { operator: ">>", location };
     let math_error = |operator| InterpreterError::BinaryOperationOverflow { location, operator };
-    if operator.kind == BinaryOpKind::Divide && rhs_value.is_zero() {
+
+    if matches!(operator.kind, BinaryOpKind::Divide | BinaryOpKind::Modulo) && rhs_value.is_zero() {
         return Err(InterpreterError::InvalidValuesForBinary {
             lhs: lhs_type,
             rhs: rhs_type,
             location,
-            operator: "/",
+            operator: if operator.kind == BinaryOpKind::Divide { "/" } else { "%" },
         });
     }
+
     /// Generate matches that can promote the type of one side to the other if they are compatible.
     macro_rules! match_values {
         (($lhs_value:ident as $lhs:ident $op:literal $rhs_value:ident as $rhs:ident) {
@@ -208,14 +210,8 @@ pub(super) fn evaluate_infix(
                 lhs.checked_shl(rhs as u32)
             }
         },
-        BinaryOpKind::Modulo => match (&lhs_value, &rhs_value) {
-            (Value::I8(i8::MIN), Value::I8(-1)) => Ok(Value::I8(0)),
-            (Value::I16(i16::MIN), Value::I16(-1)) => Ok(Value::I16(0)),
-            (Value::I32(i32::MIN), Value::I32(-1)) => Ok(Value::I32(0)),
-            (Value::I64(i64::MIN), Value::I64(-1)) => Ok(Value::I64(0)),
-            _ => match_integer! {
-                (lhs_value as lhs "%" rhs_value as rhs) => lhs.checked_rem(rhs)
-            },
+        BinaryOpKind::Modulo => match_integer! {
+            (lhs_value as lhs "%" rhs_value as rhs) => lhs.checked_rem(rhs)
         },
     }
 }
@@ -247,9 +243,8 @@ mod test {
         let rhs = Value::I8(-1);
         let operator = HirBinaryOp { kind: BinaryOpKind::Modulo, location: Location::dummy() };
         let location = Location::dummy();
-        let result = evaluate_infix(lhs, rhs, operator, location).unwrap();
-
-        assert_eq!(result, Value::I8(0));
+        let err = evaluate_infix(lhs, rhs, operator, location).unwrap_err();
+        assert!(matches!(err, InterpreterError::BinaryOperationOverflow { .. }));
     }
 
     #[test]
```

### compiler/noirc_frontend/src/tests.rs
```diff
@@ -4357,6 +4357,20 @@ fn attempt_to_divide_by_zero_at_comptime() {
     check_errors!(src);
 }
 
+#[test]
+fn attempt_to_modulo_by_zero_at_comptime() {
+    let src = r#"
+        fn main() -> pub u8 {
+            comptime {
+                255 as u8 % 0
+                ^^^^^^^^^^^^^ Attempt to calculate the remainder with a divisor of zero
+            }
+        }
+
+        "#;
+    check_errors!(src);
+}
+
 #[test]
 fn same_name_in_types_and_values_namespace_works() {
     let src = "
```

### cspell.json
```diff
@@ -141,6 +141,7 @@
         "Guillaume",
         "gzipped",
         "hasher",
+        "hashers",
         "hashset",
         "heaptrack",
         "hexdigit",
```
