# [?] fix(ssa): SSA Interpreter handle overflow by promoting to Field (#10097)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-10-10
Source: https://github.com/noir-lang/noir/commit/d09585f1a9b1370c3be58ffb3477eb0fa4349fd7
Type: security-commit

## Details
fix(ssa): SSA Interpreter handle overflow by promoting to Field (#10097)

## Patch
### compiler/noirc_evaluator/src/ssa/interpreter/intrinsics.rs
```diff
@@ -6,14 +6,11 @@ use iter_extended::{try_vecmap, vecmap};
 use noirc_printable_type::{PrintableType, PrintableValueDisplay, decode_printable_value};
 use num_bigint::BigUint;
 
-use crate::ssa::{
-    interpreter::NumericValue,
-    ir::{
-        dfg,
-        instruction::{Endian, Intrinsic},
-        types::{NumericType, Type},
-        value::ValueId,
-    },
+use crate::ssa::ir::{
+    dfg,
+    instruction::{Endian, Intrinsic},
+    types::{NumericType, Type},
+    value::ValueId,
 };
 
 use super::{ArrayValue, IResult, IResults, InternalError, Interpreter, InterpreterError, Value};
@@ -30,7 +27,7 @@ impl<W: Write> Interpreter<'_, W> {
                 check_argument_count(args, 1, intrinsic)?;
                 let array = self.lookup_array_or_slice(args[0], "call to array_len")?;
                 let length = array.elements.borrow().len();
-                Ok(vec![Value::Numeric(NumericValue::U32(length as u32))])
+                Ok(vec![Value::u32(length as u32)])
             }
             Intrinsic::ArrayAsStrUnchecked => {
                 check_argument_count(args, 1, intrinsic)?;
@@ -40,7 +37,7 @@ impl<W: Write> Interpreter<'_, W> {
                 check_argument_count(args, 1, intrinsic)?;
                 let array = self.lookup_array_or_slice(args[0], "call to as_slice")?;
                 let length = array.elements.borrow().len();
-                let length = Value::Numeric(NumericValue::U32(length as u32));
+                let length = Value::u32(length as u32);
 
                 let elements = array.elements.borrow().to_vec();
                 let slice = Value::slice(elements, array.element_types.clone());
@@ -537,7 +534,7 @@ impl<W: Write> Interpreter<'_, W> {
             new_elements.push(self.lookup(*arg)?);
         }
 
-        let new_length = Value::Numeric(NumericValue::U32(length + 1));
+        let new_length = Value::u32(length + 1);
         let new_slice = Value::slice(new_elements, element_types);
         Ok(vec![new_length, new_slice])
     }
@@ -552,7 +549,7 @@ impl<W: Write> Interpreter<'_, W> {
         let mut new_elements = try_vecmap(args.iter().skip(2), |arg| self.lookup(*arg))?;
         new_elements.extend_from_slice(&slice_elements.borrow());
 
-        let new_length = Value::Numeric(NumericValue::U32(length + 1));
+        let new_length = Value::u32(length + 1);
         let new_slice = Value::slice(new_elements, element_types);
         Ok(vec![new_length, new_slice])
     }
@@ -578,7 +575,7 @@ impl<W: Write> Interpreter<'_, W> {
         let mut popped_elements = vecmap(0..element_types.len(), |_| slice_elements.pop().unwrap());
         popped_elements.reverse();
 
-        let new_length = Value::Numeric(NumericValue::U32(length - 1));
+        let new_length = Value::u32(length - 1);
         let new_slice = Value::slice(slice_elements, element_types);
         let mut results = vec![new_length, new_slice];
         results.extend(popped_elements);
@@ -601,7 +598,7 @@ impl<W: Write> Interpreter<'_, W> {
 
         let mut results = slice_elements.drain(0..element_types.len()).collect::<Vec<_>>();
 
-        let new_length = Value::Numeric(NumericValue::U32(length - 1));
+        let new_length = Value::u32(length - 1);
         let new_slice = Value::slice(slice_elements, element_types);
         results.push(new_length);
         results.push(new_slice);
@@ -623,7 +620,7 @@ impl<W: Write> Interpreter<'_, W> {
             index += 1;
         }
 
-        let new_length = Value::Numeric(NumericValue::U32(length + 1));
+        let new_length = Value::u32(length + 1);
         let new_slice = Value::slice(slice_elements, element_types);
         Ok(vec![new_length, new_slice])
     }
@@ -646,7 +643,7 @@ impl<W: Write> Interpreter<'_, W> {
         let index = index as usize * element_types.len();
         let removed: Vec<_> = slice_elements.drain(index..index + element_types.len()).collect();
 
-        let new_length = Value::Numeric(NumericValue::U32(length - 1));
+        let new_length = Value::u32(length - 1);
         let new_slice = Value::slice(slice_elements, element_types);
         let mut results = vec![new_length, new_slice];
         results.extend(removed);
@@ -842,8 +839,8 @@ fn values_to_fields(values: &[Value]) -> Vec<FieldElement> {
                 }
             }
             // Chamber the length for a potential vector following it.
-            if let Value::Numeric(NumericValue::U32(length)) = value {
-                vector_length = Some(*length as usize);
+            if let Some(length) = value.as_u32() {
+                vector_length = Some(length as usize);
             } else {
                 vector_length = None;
             }
```

### compiler/noirc_evaluator/src/ssa/interpreter/mod.rs
```diff
@@ -10,11 +10,15 @@ use super::{
         value::ValueId,
     },
 };
-use crate::ssa::ir::{instruction::binary::truncate_field, printer::display_binary};
+use crate::ssa::{
+    interpreter::value::Fitted,
+    ir::{instruction::binary::truncate_field, printer::display_binary, types::NumericType},
+};
 use acvm::{AcirField, FieldElement};
 use errors::{InternalError, InterpreterError, MAX_UNSIGNED_BIT_SIZE};
 use iter_extended::{try_vecmap, vecmap};
 use noirc_frontend::Shared;
+use num_traits::{CheckedShl, CheckedShr};
 use rustc_hash::FxHashMap as HashMap;
 use value::{ArrayValue, NumericValue, ReferenceValue};
 
@@ -608,23 +612,39 @@ impl<'ssa, W: Write> Interpreter<'ssa, W> {
     }
 
     fn interpret_not(&mut self, id: ValueId, result: ValueId) -> IResult<()> {
-        let new_result = match self.lookup_numeric(id, "not instruction")? {
+        let num_value = self.lookup_numeric(id, "not instruction")?;
+        let bit_size = num_value.get_type().bit_size();
+
+        // Based on AcirContext::not_var
+        fn fitted_not<T: std::ops::Not<Output = T>>(value: Fitted<T>, bit_size: u32) -> Fitted<T> {
+            value.map(
+                |value| !value,
+                |value| {
+                    // Based on AcirContext::not_var
+                    let bit_size = FieldElement::from(bit_size);
+                    let max = FieldElement::from(2u128).pow(&bit_size) - FieldElement::one();
+                    max - value
+                },
+            )
+        }
+
+        let new_result = match num_value {
             NumericValue::Field(_) => {
                 return Err(internal(InternalError::UnsupportedOperatorForType {
                     operator: "!",
                     typ: "Field",
                 }));
             }
             NumericValue::U1(value) => NumericValue::U1(!value),
-            NumericValue::U8(value) => NumericValue::U8(!value),
-            NumericValue::U16(value) => NumericValue::U16(!value),
-            NumericValue::U32(value) => NumericValue::U32(!value),
-            NumericValue::U64(value) => NumericValue::U64(!value),
-            NumericValue::U128(value) => NumericValue::U128(!value),
-            NumericValue::I8(value) => NumericValue::I8(!value),
-            NumericValue::I16(value) => NumericValue::I16(!value),
-            NumericValue::I32(value) => NumericValue::I32(!value),
-            NumericValue::I64(value) => NumericValue::I64(!value),
+            NumericValue::U8(value) => NumericValue::U8(fitted_not(value, bit_size)),
+            NumericValue::U16(value) => NumericValue::U16(fitted_not(value, bit_size)),
+            NumericValue::U32(value) => NumericValue::U32(fitted_not(value, bit_size)),
+            NumericValue::U64(value) => NumericValue::U64(fitted_not(value, bit_size)),
+            NumericValue::U128(value) => NumericValue::U128(fitted_not(value, bit_size)),
+            NumericValue::I8(value) => NumericValue::I8(fitted_not(value, bit_size)),
+            NumericValue::I16(value) => NumericValue::I16(fitted_not(value, bit_size)),
+            NumericValue::I32(value) => NumericValue::I32(fitted_not(value, bit_size)),
+            NumericValue::I64(value) => NumericValue::I64(fitted_not(value, bit_size)),
         };
         self.define(result, Value::Numeric(new_result))
     }
@@ -636,31 +656,66 @@ impl<'ssa, W: Write> Interpreter<'ssa, W> {
         max_bit_size: u32,
         result: ValueId,
     ) -> IResult<()> {
+        use Fitted::*;
+        use NumericValue::*;
+
         let value = self.lookup_numeric(value_id, "truncate")?;
+        let typ = value.get_type();
         if bit_size == 0 {
             return Err(internal(InternalError::TruncateToZeroBits { value_id, max_bit_size }));
         }
 
-        let truncated = match value {
-            NumericValue::Field(value) => NumericValue::Field(truncate_field(value, bit_size)),
-            NumericValue::U1(value) => NumericValue::U1(value),
-            NumericValue::U8(value) => NumericValue::U8(truncate_unsigned(value, bit_size)?),
-            NumericValue::U16(value) => NumericValue::U16(truncate_unsigned(value, bit_size)?),
-            NumericValue::U32(value) => NumericValue::U32(truncate_unsigned(value, bit_size)?),
-            NumericValue::U64(value) => NumericValue::U64(truncate_unsigned(value, bit_size)?),
-            NumericValue::U128(value) => NumericValue::U128(truncate_unsigned(value, bit_size)?),
-            NumericValue::I8(value) => {
-                NumericValue::I8(truncate_unsigned(value as u8, bit_size)? as i8)
-            }
-            NumericValue::I16(value) => {
-                NumericValue::I16(truncate_unsigned(value as u16, bit_size)? as i16)
-            }
-            NumericValue::I32(value) => {
-                NumericValue::I32(truncate_unsigned(value as u32, bit_size)? as i32)
-            }
-            NumericValue::I64(value) => {
-                NumericValue::I64(truncate_unsigned(value as u64, bit_size)? as i64)
+        // Truncate an unsigned value.
+        fn truncate_fitted<F, T>(
+            cons: F,
+            typ: NumericType,
+            value: Fitted<T>,
+            bit_size: u32,
+        ) -> IResult<NumericValue>
+        where
+            T: TryFrom<u128>,
+            u128: From<T>,
+            <T as TryFrom<u128>>::Error: std::fmt::Debug,
+            F: Fn(Fitted<T>) -> NumericValue,
+        {
+            match value {
+                Fit(value) => Ok(cons(Fit(truncate_unsigned(value, bit_size)?))),
+                Unfit(value) => {
+                    let truncated = truncate_field(value, bit_size);
+                    NumericValue::from_constant(truncated, typ)
+                        .or_else(|_| Ok(cons(Unfit(truncated))))
+                }
             }
+        }
+
+        // Truncate a signed value via unsigned cast and back.
+        macro_rules! truncate_via {
+            ($cons:expr, $typ:expr, $value:ident, $bit_size:ident, $signed:ty, $unsigned:ty) => {
+                match $value {
+                    Fit(value) => {
+                        $cons(Fit(truncate_unsigned(value as $unsigned, $bit_size)? as $signed))
+                    }
+                    Unfit(value) => {
+                        let truncated = truncate_field(value, bit_size);
+                        NumericValue::from_constant(truncated, typ)
+                            .unwrap_or_else(|_| $cons(Unfit(truncated)))
+                    }
+                }
+            };
+        }
+
+        let truncated = match value {
+            Field(value) => Field(truncate_field(value, bit_size)),
+            U1(value) => U1(value),
+            U8(value) => truncate_fitted(U8, typ, value, bit_size)?,
+            U16(value) => truncate_fitted(U16, typ, value, bit_size)?,
+            U32(value) => truncate_fitted(U32, typ, value, bit_size)?,
+            U64(value) => truncate_fitted(U64, typ, value, bit_size)?,
+            U128(value) => truncate_fitted(U128, typ, value, bit_size)?,
+            I8(value) => truncate_via!(I8, typ, value, bit_size, i8, u8),
+            I16(value) => truncate_via!(I16, typ, value, bit_size, i16, u16),
+            I32(value) => truncate_via!(I32, typ, value, bit_size, i32, u32),
+            I64(value) => truncate_via!(I64, typ, value, bit_size, i64, u64),
         };
 
         self.define(result, Value::Numeric(truncated))
@@ -688,34 +743,35 @@ impl<'ssa, W: Write> Interpreter<'ssa, W> {
             if x <= 0.0001 { 0 } else { x.log2() as u32 + 1 }
         }
 
+        fn fitted_bit_count<T: Into<f64>>(value: Fitted<T>) -> u32 {
+            value.apply(|value| bit_count(value), |value| value.num_bits())
+        }
+
         let bit_count = match value {
             NumericValue::Field(value) => value.num_bits(),
             // max_bit_size > 0 so u1 should always pass these checks
             NumericValue::U1(_) => return Ok(()),
-            NumericValue::U8(value) => bit_count(value),
-            NumericValue::U16(value) => bit_count(value),
-            NumericValue::U32(value) => bit_count(value),
+            NumericValue::U8(value) => fitted_bit_count(value),
+            NumericValue::U16(value) => fitted_bit_count(value),
+            NumericValue::U32(value) => fitted_bit_count(value),
             NumericValue::U64(value) => {
                 // u64, u128, and i64 don't impl Into<f64>
-                if value == 0 { 0 } else { value.ilog2() + 1 }
-            }
-            NumericValue::U128(value) => {
-                if value == 0 {
-                    0
-                } else {
-                    value.ilog2() + 1
-                }
-            }
-            NumericValue::I8(value) => bit_count(value),
-            NumericValue::I16(value) => bit_count(value),
-            NumericValue::I32(value) => bit_count(value),
-            NumericValue::I64(value) => {
-                if value == 0 {
-                    0
-                } else {
-                    value.ilog2() + 1
-                }
+                value.apply(
+                    |value| if value == 0 { 0 } else { value.ilog2() + 1 },
+                    |value| value.num_bits(),
+                )
             }
+            NumericValue::U128(value) => value.apply(
+                |value| if value == 0 { 0 } else { value.ilog2() + 1 },
+                |value| value.num_bits(),
+            ),
+            NumericValue::I8(value) => fitted_bit_count(value),
+            NumericValue::I16(value) => fitted_bit_count(value),
+            NumericValue::I32(value) => fitted_bit_count(value),
+            NumericValue::I64(value) => value.apply(
+                |value| if value == 0 { 0 } else { value.ilog2() + 1 },
+                |value| value.num_bits(),
+            ),
         };
 
         if bit_count > max_bit_size {
@@ -1118,12 +1174,75 @@ impl<'ssa, W: Write> Interpreter<'ssa, W> {
     }
 }
 
+/// Applies a fallible integer binary operation on `Fitted` values, or returns an overflow error.
+///
+/// If one of the values are already `Unfit`, the result is an overflow.
+macro_rules! apply_fit_binop_opt {
+    ($lhs:expr, $rhs:expr, $f:expr, $overflow:expr) => {
+        match ($lhs, $rhs) {
+            (Fitted::Fit(lhs), Fitted::Fit(rhs)) => {
+                $f(&lhs, &rhs).map(Fitted::Fit).ok_or_else($overflow)
+            }
+            _ => Err($overflow()),
+        }
+    };
+}
+
+/// Applies a fallible integer binary operation on `Fitted` values, promoting values to `Field` in
+/// case there is an overflow, thus turning the operation infallible.
+///
+/// If the result is an overflow, it promotes the values to `Field` and performs the operation there.
+/// If the operation is applied on `Unfit` values, and the result fits in the original numeric type,
+/// it is converted back to a `Fit` value.
+///
+/// For example we would normally have an infallible `wrapped_add`, but we want to match ACIR
+/// by not wrapping around but extending into larger bit sizes.
+///
+/// # Parameters
+/// - `$cons`: Constructor for a `NumericValue`
+/// - `$lhs`, `$rhs`: The `Fitted` values in the left-hand side and right-hand side operands.
+/// - `$f`: The function to apply on the integer values if both are `Fit`; returns `None` on overflow.
+/// - `$g`: The function to apply on `Field` values.
+/// - `$lhs_num`, `$rhs_num`: The original `NumericValue`s.
+macro_rules! apply_fit_binop {
+    ($cons:expr, $lhs:expr, $rhs:expr, $f:expr, $g:expr, $lhs_num:expr, $rhs_num:expr) => {
+        if let (Fitted::Fit(lhs), Fitted::Fit(rhs)) = ($lhs, $rhs) {
+            let fitted = $f(&lhs, &rhs).map(Fitted::Fit).unwrap_or_else(|| {
+                Fitted::Unfit($g($lhs_num.convert_to_field(), $rhs_num.convert_to_field()))
+            });
+            $cons(fitted)
+        } else {
+            let field = $g($lhs_num.convert_to_field(), $rhs_num.convert_to_field());
+            let typ = $lhs_num.get_type();
+            NumericValue::from_constant(field, typ).unwrap_or_else(|_| {
+                let fitted = Fitted::Unfit(field);
+                $cons(fitted)
+            })
+        }
+    };
+}
+
+/// Apply a comparison operator on `Fitted` values, returning a `bool`.
+///
+/// This is here for the sake of `apply_int_comparison_op`, but comparing `Field` is only meaningful for equality.
+/// For anything else it's best to panic, or return an error; we'll see if it comes up.
+macro_rules! apply_fit_comparison_op {
+    ($lhs:expr, $rhs:expr, $f:expr, $g:expr, $lhs_num:expr, $rhs_num:expr) => {{
+        if let (Fitted::Fit(lhs), Fitted::Fit(rhs)) = ($lhs, $rhs) {
+            $f(lhs, rhs)
+        } else {
+            $g($lhs_num.convert_to_field(), $rhs_num.convert_to_field())
+        }
+    }};
+}
+
 /// Applies an infallible integer binary operation to two `NumericValue`s.
 ///
 /// # Parameters
 /// - `$lhs`, `$rhs`: The left hand side and right hand side operands (must be the same variant).
 /// - `$binary`: The binary instruction, used for error handling if types mismatch.
-/// - `$f`: A function (e.g., `wrapping_add`) that applies the operation on the raw numeric types.
+/// - `$f`: A function (e.g., `checked_add`) that applies the operation on the raw numeric types.
+/// - `$g`: A function that performs the equivalent of `$f` on `Field` values.
 ///
 /// # Panics
 /// - If either operand is a [NumericValue::Field] or [NumericValue::U1] variant, this macro will panic with unreachable.
@@ -1134,22 +1253,24 @@ impl<'ssa, W: Write> Interpreter<'ssa, W> {
 /// # Returns
 /// A `NumericValue` containing the result of the operation, matching the original type.
 macro_rules! apply_int_binop {
-    ($lhs:expr, $rhs:expr, $binary:expr, $f:expr) => {{
+    ($lhs:expr, $rhs:expr, $binary:expr, $f:expr, $g:expr) => {{
         use value::NumericValue::*;
+        let lhs_num: value::NumericValue = $lhs;
+        let rhs_num: value::NumericValue = $rhs;
         match ($lhs, $rhs) {
             (Field(_), Field(_)) => {
                 unreachable!("Expected only integer values, found field values")
             }
             (U1(_), U1(_)) => unreachable!("Expected only large integer values, found u1"),
-            (U8(lhs), U8(rhs)) => U8($f(&lhs, &rhs)),
-            (U16(lhs), U16(rhs)) => U16($f(&lhs, &rhs)),
-            (U32(lhs), U32(rhs)) => U32($f(&lhs, &rhs)),
-            (U64(lhs), U64(rhs)) => U64($f(&lhs, &rhs)),
-            (U128(lhs), U128(rhs)) => U128($f(&lhs, &rhs)),
-            (I8(lhs), I8(rhs)) => I8($f(&lhs, &rhs)),
-            (I16(lhs), I16(rhs)) => I16($f(&lhs, &rhs)),
-            (I32(lhs), I32(rhs)) => I32($f(&lhs, &rhs)),
-            (I64(lhs), I64(rhs)) => I64($f(&lhs, &rhs)),
+            (U8(lhs), U8(rhs)) => apply_fit_binop!(U8, lhs, rhs, $f, $g, lhs_num, rhs_num),
+            (U16(lhs), U16(rhs)) => apply_fit_binop!(U16, lhs, rhs, $f, $g, lhs_num, rhs_num),
+            (U32(lhs), U32(rhs)) => apply_fit_binop!(U32, lhs, rhs, $f, $g, lhs_num, rhs_num),
+            (U64(lhs), U64(rhs)) => apply_fit_binop!(U64, lhs, rhs, $f, $g, lhs_num, rhs_num),
+            (U128(lhs), U128(rhs)) => apply_fit_binop!(U128, lhs, rhs, $f, $g, lhs_num, rhs_num),
+            (I8(lhs), I8(rhs)) => apply_fit_binop!(I8, lhs, rhs, $f, $g, lhs_num, rhs_num),
+            (I16(lhs), I16(rhs)) => apply_fit_binop!(I16, lhs, rhs, $f, $g, lhs_num, rhs_num),
+            (I32(lhs), I32(rhs)) => apply_fit_binop!(I32, lhs, rhs, $f, $g, lhs_num, rhs_num),
+            (I64(lhs), I64(rhs)) => apply_fit_binop!(I64, lhs, rhs, $f, $g, lhs_num, rhs_num),
             (lhs, rhs) => {
                 let binary = $binary;
                 return Err(internal(InternalError::MismatchedTypesInBinaryOperator {
@@ -1167,10 +1288,10 @@ macro_rules! apply_int_binop {
 /// Applies a fallible integer binary operation (e.g., checked arithmetic) to two `NumericValue`s.
 ///
 /// # Parameters
-/// - `$dfg`: The data flow graph, used for formatting diagnostic error messages.
 /// - `$lhs`, `$rhs`: The left-hand side and right-hand side operands (must be the same variant).
 /// - `$binary`: The binary instruction, used for diagnostics and overflow reporting.
 /// - `$f`: A fallible operation function that returns an `Option<_>` (e.g., `checked_add`).
+/// - `$display_binary`: A function to display the binary operation for diagnostic purposes.
 ///
 /// # Panics
 /// - If either operand is a [NumericValue::Field]or [NumericValue::U1], this macro panics as those types are not supported.
@@ -1210,15 +1331,15 @@ macro_rules! apply_int_binop_opt {
                 unreachable!("Expected only integer values, found field values")
             }
             (U1(_), U1(_)) => unreachable!("Expected only large integer values, found u1"),
-            (U8(lhs), U8(rhs)) => U8($f(&lhs, &rhs).ok_or_else(overflow)?),
-            (U16(lhs), U16(rhs)) => U16($f(&lhs, &rhs).ok_or_else(overflow)?),
-            (U32(lhs), U32(rhs)) => U32($f(&lhs, &rhs).ok_or_else(overflow)?),
-            (U64(lhs), U64(rhs)) => U64($f(&lhs, &rhs).ok_or_else(overflow)?),
-            (U128(lhs), U128(rhs)) => U128($f(&lhs, &rhs).ok_or_else(overflow)?),
-            (I8(lhs), I8(rhs)) => I8($f(&lhs, &rhs).ok_or_else(overflow)?),
-            (I16(lhs), I16(rhs)) => I16($f(&lhs, &rhs).ok_or_else(overflow)?),
-            (I32(lhs), I32(rhs)) => I32($f(&lhs, &rhs).ok_or_else(overflow)?),
-            (I64(lhs), I64(rhs)) => I64($f(&lhs, &rhs).ok_or_else(overflow)?),
+            (U8(lhs), U8(rhs)) => U8(apply_fit_binop_opt!(lhs, rhs, $f, overflow)?),
+            (U16(lhs), U16(rhs)) => U16(apply_fit_binop_opt!(lhs, rhs, $f, overflow)?),
+            (U32(lhs), U32(rhs)) => U32(apply_fit_binop_opt!(lhs, rhs, $f, overflow)?),
+            (U64(lhs), U64(rhs)) => U64(apply_fit_binop_opt!(lhs, rhs, $f, overflow)?),
+            (U128(lhs), U128(rhs)) => U128(apply_fit_binop_opt!(lhs, rhs, $f, overflow)?),
+            (I8(lhs), I8(rhs)) => I8(apply_fit_binop_opt!(lhs, rhs, $f, overflow)?),
+            (I16(lhs), I16(rhs)) => I16(apply_fit_binop_opt!(lhs, rhs, $f, overflow)?),
+            (I32(lhs), I32(rhs)) => I32(apply_fit_binop_opt!(lhs, rhs, $f, overflow)?),
+            (I64(lhs), I64(rhs)) => I64(apply_fit_binop_opt!(lhs, rhs, $f, overflow)?),
             (lhs, rhs) => {
                 return Err(internal(InternalError::MismatchedTypesInBinaryOperator {
                     lhs: lhs.to_string(),
@@ -1233,22 +1354,38 @@ macro_rules! apply_int_binop_opt {
 }
 
 macro_rules! apply_int_comparison_op {
-    ($lhs:expr, $rhs:expr, $binary:expr, $f:expr) => {{
+    ($lhs:expr, $rhs:expr, $binary:expr, $f:expr, $g:expr) => {{
         use NumericValue::*;
+        let lhs_num: NumericValue = $lhs;
+        let rhs_num: NumericValue = $rhs;
         match ($lhs, $rhs) {
             (Field(_), Field(_)) => {
                 unreachable!("Expected only integer values, found field values")
             }
             (U1(_), U1(_)) => unreachable!("Expected only large integer values, found u1"),
-            (U8(lhs), U8(rhs)) => U1($f(&lhs, &rhs)),
-            (U16(lhs), U16(rhs)) => U1($f(&lhs, &rhs)),
-            (U32(lhs), U32(rhs)) => U1($f(&lhs, &rhs)),
-            (U64(lhs), U64(rhs)) => U1($f(&lhs, &rhs)),
-            (U128(lhs), U128(rhs)) => U1($f(&lhs, &rhs)),
-            (I8(lhs), I8(rhs)) => U1($f(&lhs, &rhs)),
-            (I16(lhs), I16(rhs)) => U1($f(&lhs, &rhs)),
-            (I32(lhs), I32(rhs)) => U1($f(&lhs, &rhs)),
-            (I64(lhs), I64(rhs)) => U1($f(&lhs, &rhs)),
+            (U8(lhs), U8(rhs)) => U1(apply_fit_comparison_op!(lhs, rhs, $f, $g, lhs_num, rhs_num)),
+            (U16(lhs), U16(rhs)) => {
+                U1(apply_fit_comparison_op!(lhs, rhs, $f, $g, lhs_num, rhs_num))
+            }
+            (U32(lhs), U32(rhs)) => {
+                U1(apply_fit_comparison_op!(lhs, rhs, $f, $g, lhs_num, rhs_num))
+            }
+            (U64(lhs), U64(rhs)) => {
+                U1(apply_fit_comparison_op!(lhs, rhs, $f, $g, lhs_num, rhs_num))
+            }
+            (U128(lhs), U128(rhs)) => {
+                U1(apply_fit_comparison_op!(lhs, rhs, $f, $g, lhs_num, rhs_num))
+            }
+            (I8(lhs), I8(rhs)) => U1(apply_fit_comparison_op!(lhs, rhs, $f, $g, lhs_num, rhs_num)),
+            (I16(lhs), I16(rhs)) => {
+                U1(apply_fit_comparison_op!(lhs, rhs, $f, $g, lhs_num, rhs_num))
+            }
+            (I32(lhs), I32(rhs)) => {
+                U1(apply_fit_comparison_op!(lhs, rhs, $f, $g, lhs_num, rhs_num))
+            }
+            (I64(lhs), I64(rhs)) => {
+                U1(apply_fit_comparison_op!(lhs, rhs, $f, $g, lhs_num, rhs_num))
+            }
             (lhs, rhs) => {
                 let binary = $binary;
                 return Err(internal(InternalError::MismatchedTypesInBinaryOperator {
@@ -1307,7 +1444,7 @@ fn evaluate_binary(
             )
         }
         BinaryOp::Add { unchecked: true } => {
-            apply_int_binop!(lhs, rhs, binary, num_traits::WrappingAdd::wrapping_add)
+            apply_int_binop!(lhs, rhs, binary, num_traits::CheckedAdd::checked_add, |a, b| a + b)
         }
         BinaryOp::Sub { unchecked: false } => {
             apply_int_binop_opt!(
@@ -1319,7 +1456,7 @@ fn evaluate_binary(
             )
         }
         BinaryOp::Sub { unchecked: true } => {
-            apply_int_binop!(lhs, rhs, binary, num_traits::WrappingSub::wrapping_sub)
+            apply_int_binop!(lhs, rhs, binary, num_traits::CheckedSub::checked_sub, |a, b| a - b)
         }
         BinaryOp::Mul { unchecked: false } => {
             // Only unsigned multiplication has side effects
@@ -1332,7 +1469,7 @@ fn evaluate_binary(
             )
         }
         BinaryOp::Mul { unchecked: true } => {
-            apply_int_binop!(lhs, rhs, binary, num_traits::WrappingMul::wrapping_mul)
+            apply_int_binop!(lhs, rhs, binary, num_traits::CheckedMul::checked_mul, |a, b| a * b)
         }
         BinaryOp::Div => apply_int_binop_opt!(
             lhs,
@@ -1348,62 +1485,59 @@ fn evaluate_binary(
             num_traits::CheckedRem::checked_rem,
             display_binary
         ),
-        BinaryOp::Eq => apply_int_comparison_op!(lhs, rhs, binary, |a, b| a == b),
-        BinaryOp::Lt => apply_int_comparison_op!(lhs, rhs, binary, |a, b| a < b),
+        BinaryOp::Eq => apply_int_comparison_op!(lhs, rhs, binary, |a, b| a == b, |a, b| a == b),
+        BinaryOp::Lt => {
+            apply_int_comparison_op!(lhs, rhs, binary, |a, b| a < b, |_, _| unreachable!(
+                "unfit lt: fit types should have been restored already"
+            ))
+        }
         BinaryOp::And => {
-            apply_int_binop!(lhs, rhs, binary, std::ops::BitAnd::bitand)
+            apply_int_binop!(lhs, rhs, binary, |a, b| Some(a & b), |_, _| unreachable!(
+                "unfit and: fit types should have been restored already"
+            ))
         }
         BinaryOp::Or => {
-            apply_int_binop!(lhs, rhs, binary, std::ops::BitOr::bitor)
+            apply_int_binop!(lhs, rhs, binary, |a, b| Some(a | b), |_, _| unreachable!(
+                "unfit or: fit types should have been restored already"
+            ))
         }
         BinaryOp::Xor => {
-            apply_int_binop!(lhs, rhs, binary, std::ops::BitXor::bitxor)
+            apply_int_binop!(lhs, rhs, binary, |a, b| Some(a ^ b), |_, _| unreachable!(
+                "unfit xor: fit types should have been restored already"
+            ))
         }
         BinaryOp::Shl => {
             use NumericValue::*;
             let instruction = format!("`{}` ({lhs} << {rhs})", display_binary(binary));
-            let overflow = InterpreterError::Overflow { operator: BinaryOp::Shl, instruction };
+            let over = || InterpreterError::Overflow { operator: BinaryOp::Shl, instruction };
+
+            fn shl<A: CheckedShl>(a: &A, b: &u32) -> Option<A> {
+                a.checked_shl(*b)
+            }
+            fn shl_into<A: CheckedShl, B: Into<u32> + Copy>(a: &A, b: &B) -> Option<A> {
+                shl(a, &(*b).into())
+            }
+            fn shl_try<A: CheckedShl, B: TryInto<u32> + Copy>(a: &A, b: &B) -> Option<A> {
+                shl(a, &(*b).try_into().ok()?)
+            }
+
             match (lhs, rhs) {
                 (Field(_), _) | (_, Field(_)) => {
                     return Err(internal(InternalError::UnsupportedOperatorForType {
                         operator: "<<",
                         typ: "Field",
                     }));
                 }
-                (U1(lhs_value), U1(rhs_value)) => U1(if !rhs_value { lhs_value } else { false }),
-                (U8(lhs_value), U8(rhs_value)) => {
-                    lhs_value.checked_shl(rhs_value.into()).map(U8).ok_or(overflow)?
-                }
-                (U16(lhs_value), U16(rhs_value)) => {
-                    lhs_value.checked_shl(rhs_value.into()).map(U16).ok_or(overflow)?
-                }
-                (U32(lhs_value), U32(rhs_value)) => {
-                    lhs_value.checked_shl(rhs_value).map(U32).ok_or(overflow)?
-                }
-                (U64(lhs_value), U64(rhs_value)) => {
-                    let rhs_value: u32 = rhs_value.try_into().map_err(|_| overflow.clone())?;
-                    lhs_value.checked_shl(rhs_value).map(U64).ok_or(overflow)?
-                }
-                (U128(lhs_value), U128(rhs_value)) => {
-                    let rhs_value: u32 = rhs_value.try_into().map_err(|_| overflow.clone())?;
-                    lhs_value.checked_shl(rhs_value).map(U128).ok_or(overflow)?
-                }
-                (I8(lhs_value), I8(rhs_value)) => {
-                    let rhs_value: u32 = rhs_value.try_into().map_err(|_| overflow.clone())?;
-                    lhs_value.checked_shl(rhs_value).map(I8).ok_or(overflow)?
-                }
-                (I16(lhs_value), I16(rhs_value)) => {
-                    let rhs_value: u32 = rhs_value.try_into().map_err(|_| overflow.clone())?;
-                    lhs_value.checked_shl(rhs_value).map(I16).ok_or(overflow)?
-                }
-                (I32(lhs_value), I32(rhs_value)) => {
-                    let rhs_value: u32 = rhs_value.try_into().map_err(|_| overflow.clone())?;
-                    lhs_value.checked_shl(rhs_value).map(I32).ok_or(overflow)?
-                }
-                (I64(lhs_value), I64(rhs_value)) => {
-                    let rhs_value: u32 = rhs_value.try_into().map_err(|_| overflow.clone())?;
-                    lhs_value.checked_shl(rhs_value).map(I64).ok_or(overflow)?
-                }
+                (U1(lhs), U1(rhs)) => U1(if !rhs { lhs } else { false }),
+                (U8(lhs), U8(rhs)) => U8(apply_fit_binop_opt!(lhs, rhs, shl_into, over)?),
+                (U16(lhs), U16(rhs)) => U16(apply_fit_binop_opt!(lhs, rhs, shl_into, over)?),
+                (U32(lhs), U32(rhs)) => U32(apply_fit_binop_opt!(lhs, rhs, shl, over)?),
+                (U64(lhs), U64(rhs)) => U64(apply_fit_binop_opt!(lhs, rhs, shl_try, over)?),
+                (U128(lhs), U128(rhs)) => U128(apply_fit_binop_opt!(lhs, rhs, shl_try, over)?),
+                (I8(lhs), I8(rhs)) => I8(apply_fit_binop_opt!(lhs, rhs, shl_try, over)?),
+                (I16(lhs), I16(rhs)) => I16(apply_fit_binop_opt!(lhs, rhs, shl_try, over)?),
+                (I32(lhs), I32(rhs)) => I32(apply_fit_binop_opt!(lhs, rhs, shl_try, over)?),
+                (I64(lhs), I64(rhs)) => I64(apply_fit_binop_opt!(lhs, rhs, shl_try, over)?),
                 _ => {
                     return Err(internal(InternalError::MismatchedTypesInBinaryOperator {
                         lhs: lhs.to_string(),
@@ -1416,51 +1550,38 @@ fn evaluate_binary(
             }
         }
         BinaryOp::Shr => {
+            use NumericValue::*;
+
             let instruction = format!("`{}` ({lhs} >> {rhs})", display_binary(binary));
-            let overflow = InterpreterError::Overflow { operator: BinaryOp::Shr, instruction };
+            let over = || InterpreterError::Overflow { operator: BinaryOp::Shr, instruction };
+
+            fn shr<A: CheckedShr>(a: &A, b: &u32) -> Option<A> {
+                a.checked_shr(*b)
+            }
+            fn shr_into<A: CheckedShr, B: Into<u32> + Copy>(a: &A, b: &B) -> Option<A> {
+                shr(a, &(*b).into())
+            }
+            fn shr_try<A: CheckedShr, B: TryInto<u32> + Copy>(a: &A, b: &B) -> Option<A> {
+                shr(a, &(*b).try_into().ok()?)
+            }
 
-            use NumericValue::*;
             match (lhs, rhs) {
                 (Field(_), _) | (_, Field(_)) => {
                     return Err(internal(InternalError::UnsupportedOperatorForType {
                         operator: "<<",
                         typ: "Field",
                     }));
                 }
-                (U1(lhs_value), U1(rhs_value)) => U1(if !rhs_value { lhs_value } else { false }),
-                (U8(lhs_value), U8(rhs_value)) => {
-                    lhs_value.checked_shr(rhs_value.into()).map(U8).ok_or(overflow)?
-                }
-                (U16(lhs_value), U16(rhs_value)) => {
-                    lhs_value.checked_shr(rhs_value.into()).map(U16).ok_or(overflow)?
-                }
-                (U32(lhs_value), U32(rhs_value)) => {
-                    lhs_value.checked_shr(rhs_value).map(U32).ok_or(overflow)?
-                }
-                (U64(lhs_value), U64(rhs_value)) => {
-                    let rhs_value: u32 = rhs_value.try_into().map_err(|_| overflow.clone())?;
-                    lhs_value.checked_shr(rhs_value).map(U64).ok_or(overflow)?
-                }
-                (U128(lhs_value), U128(rhs_value)) => {
-                    let rhs_value: u32 = rhs_value.try_into().map_err(|_| overflow.clone())?;
-                    lhs_value.checked_shr(rhs_value).map(U128).ok_or(overflow)?
-                }
-                (I8(lhs_value), I8(rhs_value)) => {
-                    let rhs_value: u32 = rhs_value.try_into().map_err(|_| overflow.clone())?;
-                    lhs_value.checked_shr(rhs_value).map(I8).ok_or(overflow)?
-                }
-                (I16(lhs_value), I16(rhs_value)) => {
-                    let rhs_value: u32 = rhs_value.try_into().map_err(|_| overflow.clone())?;
-                    lhs_value.checked_shr(rhs_value).map(I16).ok_or(overflow)?
-                }
-                (I32(lhs_value), I32(rhs_value)) => {
-                    let rhs_value: u32 = rhs_value.try_into().map_err(|_| overflow.clone())?;
-                    lhs_value.checked_shr(rhs_value).map(I32).ok_or(overflow)?
-                }
-                (I64(lhs_value), I64(rhs_value)) => {
-                    let rhs_value: u32 = rhs_value.try_into().map_err(|_| overflow.clone())?;
-                    lhs_value.checked_shr(rhs_value).map(I64).ok_or(overflow)?
-                }
+                (U1(lhs), U1(rhs)) => U1(if !rhs { lhs } else { false }),
+                (U8(lhs), U8(rhs)) => U8(apply_fit_binop_opt!(lhs, rhs, shr_into, over)?),
+                (U16(lhs), U16(rhs)) => U16(apply_fit_binop_opt!(lhs, rhs, shr_into, over)?),
+                (U32(lhs), U32(rhs)) => U32(apply_fit_binop_opt!(lhs, rhs, shr, over)?),
+                (U64(lhs), U64(rhs)) => U64(apply_fit_binop_opt!(lhs, rhs, shr_try, over)?),
+                (U128(lhs), U128(rhs)) => U128(apply_fit_binop_opt!(lhs, rhs, shr_try, over)?),
+                (I8(lhs), I8(rhs)) => I8(apply_fit_binop_opt!(lhs, rhs, shr_try, over)?),
+                (I16(lhs), I16(rhs)) => I16(apply_fit_binop_opt!(lhs, rhs, shr_try, over)?),
+                (I32(lhs), I32(rhs)) => I32(apply_fit_binop_opt!(lhs, rhs, shr_try, over)?),
+                (I64(lhs), I64(rhs)) => I64(apply_fit_binop_opt!(lhs, rhs, shr_try, over)?),
                 _ => {
                     return Err(internal(InternalError::MismatchedTypesInBinaryOperator {
                         lhs: lhs.to_string(),
@@ -1693,12 +1814,12 @@ mod test {
             assert_eq!(
                 super::evaluate_binary(
                     &binary,
-                    NumericValue::I8(lhs),
-                    NumericValue::I8(rhs),
+                    NumericValue::I8(lhs.into()),
+                    NumericValue::I8(rhs.into()),
                     true,
                     display
                 ),
-                expected_result.map(NumericValue::I8),
+                expected_result.map(|i| NumericValue::I8(i.into())),
                 "{lhs} << {rhs}",
             );
         }
```

### compiler/noirc_evaluator/src/ssa/interpreter/tests/instructions.rs
```diff
@@ -1,11 +1,12 @@
 use std::sync::Arc;
 
+use acvm::{AcirField, FieldElement};
 use iter_extended::vecmap;
 use noirc_frontend::Shared;
 
 use crate::ssa::{
     interpreter::{
-        InterpreterError, NumericValue, Value,
+        InterpreterError, Value,
         tests::{
             expect_value, expect_value_with_args, expect_values, expect_values_with_args,
             from_constant,
@@ -21,6 +22,10 @@ use crate::ssa::{
 
 use super::{executes_with_no_errors, expect_error};
 
+fn make_unfit(value: impl Into<FieldElement>, typ: NumericType) -> Value {
+    Value::unfit(value.into(), typ).unwrap()
+}
+
 #[test]
 fn add_unsigned() {
     let value = expect_value(
@@ -32,7 +37,7 @@ fn add_unsigned() {
         }
     ",
     );
-    assert_eq!(value, Value::Numeric(NumericValue::U32(102)));
+    assert_eq!(value, Value::u32(102));
 }
 
 #[test]
@@ -47,7 +52,7 @@ fn add_signed() {
         }
     ",
     );
-    assert_eq!(value, Value::Numeric(NumericValue::I32(102)));
+    assert_eq!(value, Value::i32(102));
 }
 
 #[test]
@@ -103,7 +108,8 @@ fn add_unchecked_signed() {
         }
     ",
     );
-    assert_eq!(value, Value::Numeric(NumericValue::I8(-127)));
+    assert_ne!(value, Value::i8(-128), "no wrapping");
+    assert_eq!(value, make_unfit(129u32, NumericType::signed(8)));
 }
 
 #[test]
@@ -117,7 +123,7 @@ fn sub_unsigned() {
         }
     ",
     );
-    assert_eq!(value, Value::Numeric(NumericValue::U32(10000)));
+    assert_eq!(value, Value::u32(10000));
 }
 
 #[test]
@@ -132,7 +138,7 @@ fn sub_signed() {
         }
     ",
     );
-    assert_eq!(value, Value::Numeric(NumericValue::I32(-1)));
+    assert_eq!(value, Value::i32(-1));
 }
 
 #[test]
@@ -176,7 +182,12 @@ fn sub_unchecked_unsigned() {
         }
     ",
     );
-    assert!(matches!(value, Value::Numeric(NumericValue::U8(246))));
+    assert_ne!(value, Value::u8(246), "no wrapping");
+    assert_eq!(
+        value,
+        // Note that this is not the same as `Value::i8(-10).convert_to_field()`, because that casts to u8 first.
+        make_unfit(FieldElement::zero() - FieldElement::from(10u32), NumericType::unsigned(8))
+    );
 }
 
 #[test]
@@ -190,7 +201,7 @@ fn sub_unchecked_signed() {
         }
     ",
     );
-    assert_eq!(value, Value::Numeric(NumericValue::I8(-7)));
+    assert_eq!(value, Value::i8(-7));
 }
 
 #[test]
@@ -204,7 +215,7 @@ fn mul_unsigned() {
         }
     ",
     );
-    assert_eq!(value, Value::Numeric(NumericValue::U64(200)));
+    assert_eq!(value, Value::u64(200));
 }
 
 #[test]
@@ -221,7 +232,7 @@ fn mul_signed() {
         }
     ",
     );
-    assert_eq!(value, Value::Numeric(NumericValue::I64(200)));
+    assert_eq!(value, Value::i64(200));
 }
 
 #[test]
@@ -263,7 +274,8 @@ fn mul_unchecked_unsigned() {
         }
     ",
     );
-    assert_eq!(value, Value::Numeric(NumericValue::U8(0)));
+    assert_ne!(value, Value::u8(0), "no wrapping");
+    assert_eq!(value, make_unfit(256u32, NumericType::unsigned(8)));
 }
 
 #[test]
@@ -277,7 +289,8 @@ fn mul_unchecked_signed() {
         }
     ",
     );
-    assert_eq!(value, Value::Numeric(NumericValue::I8(-2)));
+    assert_ne!(value, Value::i8(-2), "no wrapping");
+    assert_eq!(value, make_unfit(254u32, NumericType::signed(8)));
 }
 
 #[test]
@@ -291,7 +304,7 @@ fn div() {
         }
     ",
     );
-    assert_eq!(value, Value::Numeric(NumericValue::I16(64)));
+    assert_eq!(value, Value::i16(64));
 }
 
 #[test]
@@ -319,7 +332,7 @@ fn r#mod() {
         }
     ",
     );
-    assert_eq!(value, Value::Numeric(NumericValue::I64(2)));
+    assert_eq!(value, Value::i64(2));
 }
 
 #[test]
@@ -853,7 +866,7 @@ fn array_get_disabled_by_enable_side_effects_if_index_is_not_known_to_be_safe()
             return v1
         }
     "#,
-        vec![Value::Numeric(NumericValue::U32(1))],
+        vec![Value::u32(1)],
     );
     // If enable_side_effects is false, array get will retrieve the value at the first compatible index
     assert_eq!(value, from_constant(1_u32.into(), NumericType::NativeField));
```

### compiler/noirc_evaluator/src/ssa/interpreter/tests/intrinsics.rs
```diff
@@ -18,7 +18,7 @@ fn to_le_bits() {
         }
     ",
     );
-    assert_eq!(value, Value::Numeric(NumericValue::U1(true)));
+    assert_eq!(value, Value::bool(true));
 }
 
 #[test]
@@ -35,7 +35,7 @@ fn to_le_radix() {
         }
     ",
     );
-    assert_eq!(value, Value::Numeric(NumericValue::U8(255)));
+    assert_eq!(value, Value::u8(255));
 }
 
 #[test]
```

### compiler/noirc_evaluator/src/ssa/interpreter/tests/mod.rs
```diff
@@ -137,17 +137,17 @@ fn return_all_numeric_constant_types() {
     let returns = expect_values(src);
     assert_eq!(returns.len(), 11);
 
-    assert_eq!(returns[0], Value::Numeric(NumericValue::Field(FieldElement::zero())));
-    assert_eq!(returns[1], Value::Numeric(NumericValue::U1(true)));
-    assert_eq!(returns[2], Value::Numeric(NumericValue::U8(2)));
-    assert_eq!(returns[3], Value::Numeric(NumericValue::U16(3)));
-    assert_eq!(returns[4], Value::Numeric(NumericValue::U32(4)));
-    assert_eq!(returns[5], Value::Numeric(NumericValue::U64(5)));
-    assert_eq!(returns[6], Value::Numeric(NumericValue::U128(6)));
-    assert_eq!(returns[7], Value::Numeric(NumericValue::I8(-1)));
-    assert_eq!(returns[8], Value::Numeric(NumericValue::I16(-2)));
-    assert_eq!(returns[9], Value::Numeric(NumericValue::I32(-3)));
-    assert_eq!(returns[10], Value::Numeric(NumericValue::I64(-4)));
+    assert_eq!(returns[0], Value::field(FieldElement::zero()));
+    assert_eq!(returns[1], Value::bool(true));
+    assert_eq!(returns[2], Value::u8(2));
+    assert_eq!(returns[3], Value::u16(3));
+    assert_eq!(returns[4], Value::u32(4));
+    assert_eq!(returns[5], Value::u64(5));
+    assert_eq!(returns[6], Value::u128(6));
+    assert_eq!(returns[7], Value::i8(-1));
+    assert_eq!(returns[8], Value::i16(-2));
+    assert_eq!(returns[9], Value::i32(-3));
+    assert_eq!(returns[10], Value::i64(-4));
 }
 
 #[test]
@@ -166,7 +166,7 @@ fn call_function() {
         }
     ";
     let actual = expect_value(src);
-    assert_eq!(Value::Numeric(NumericValue::U32(6)), actual);
+    assert_eq!(Value::u32(6), actual);
 }
 
 #[test]
@@ -1697,7 +1697,7 @@ fn signed_integer_casting() {
       }
       "#;
     let value = expect_value(src);
-    assert_eq!(value, Value::Numeric(NumericValue::I8(0)));
+    assert_eq!(value, Value::i8(0));
 }
 
 #[test]
@@ -1738,5 +1738,5 @@ fn signed_integer_casting_2() {
       }
       "#;
     let value = expect_value(src);
-    assert_eq!(value, Value::Numeric(NumericValue::I64(89)));
+    assert_eq!(value, Value::i64(89));
 }
```

### compiler/noirc_evaluator/src/ssa/interpreter/value.rs
```diff
@@ -28,21 +28,89 @@ pub enum Value {
     ForeignFunction(String),
 }
 
+/// Represents a numeric type that either fits in the expected bit size,
+/// or would have to be represented as a `Field` to match the semantics of ACIR.
+///
+/// The reason this exists is the difference in behavior of unchecked operations in Brillig and ACIR:
+/// * In Brillig unchecked operations wrap around, but we have other opcodes surrounding it that
+///   either prevent such operations from being carried out, or check for any overflows later.
+/// * In ACIR, everything is represented as a `Field`, and overflows are not checked, so e.g. an unchecked
+///   multiplication of `u32` values can result in something that only fits in a `u64`.
+///
+/// When we interpret an operation that would wrap around, if we are in an ACIR context we can use
+/// the `Unfit` variant to indicate that the value went beyond what fits into the base type.
+///
+/// Since we normally require that ACIR and Brillig return the same result, once an operation
+/// overflows its type, we have reason to believe that ACIR and Brillig would not return the same
+/// value, since Brillig wraps, and ACIR does not.
+///
+/// However, some operations that we ported back from ACIR to SSA are implemented in such a
+/// way that transient values "escape" the boundaries of their type, only to be restored later,
+/// so keeping the `Field` serves more than informational purposes. We expect that under normal
+/// circumstances this effect is temporary, and by the time we would have to apply operations
+/// on the values that aren't implemented for `Field` (e.g. `lt` and bitwise ops), the values will
+/// be back on track.
+#[derive(Debug, Copy, Clone, PartialEq, Eq)]
+pub enum Fitted<T> {
+    Fit(T),
+    Unfit(FieldElement),
+}
+
+impl<A> Fitted<A> {
+    pub fn map<B>(
+        self,
+        f: impl FnOnce(A) -> B,
+        g: impl FnOnce(FieldElement) -> FieldElement,
+    ) -> Fitted<B> {
+        match self {
+            Self::Fit(value) => Fitted::Fit(f(value)),
+            Self::Unfit(value) => Fitted::Unfit(g(value)),
+        }
+    }
+
+    pub fn apply<B>(self, f: impl FnOnce(A) -> B, g: impl FnOnce(FieldElement) -> B) -> B {
+        match self {
+            Self::Fit(value) => f(value),
+            Self::Unfit(value) => g(value),
+        }
+    }
+}
+
+macro_rules! impl_fitted {
+    ($($t:ty),*) => {
+        $(
+        impl From<$t> for Fitted<$t> {
+            fn from(value: $t) -> Self {
+                Self::Fit(value)
+            }
+        }
+
+        impl From<FieldElement> for Fitted<$t> {
+            fn from(value: FieldElement) -> Self {
+                Self::Unfit(value)
+            }
+        }
+        )*
+    };
+}
+
+impl_fitted! { u8, u16, u32, u64, u128, i8, i16, i32, i64 }
+
 #[derive(Debug, Copy, Clone, PartialEq, Eq)]
 pub enum NumericValue {
     Field(FieldElement),
 
     U1(bool),
-    U8(u8),
-    U16(u16),
-    U32(u32),
-    U64(u64),
-    U128(u128),
-
-    I8(i8),
-    I16(i16),
-    I32(i32),
-    I64(i64),
+    U8(Fitted<u8>),
+    U16(Fitted<u16>),
+    U32(Fitted<u32>),
+    U64(Fitted<u64>),
+    U128(Fitted<u128>),
+
+    I8(Fitted<i8>),
+    I16(Fitted<i16>),
+    I32(Fitted<i32>),
+    I64(Fitted<i64>),
 }
 
 #[derive(Debug, Clone, PartialEq, Eq)]
@@ -102,21 +170,21 @@ impl Value {
 
     pub(crate) fn as_u8(&self) -> Option<u8> {
         match self {
-            Value::Numeric(NumericValue::U8(value)) => Some(*value),
+            Value::Numeric(NumericValue::U8(Fitted::Fit(value))) => Some(*value),
             _ => None,
         }
     }
 
     pub(crate) fn as_u32(&self) -> Option<u32> {
         match self {
-            Value::Numeric(NumericValue::U32(value)) => Some(*value),
+            Value::Numeric(NumericValue::U32(Fitted::Fit(value))) => Some(*value),
             _ => None,
         }
     }
 
     pub(crate) fn as_u64(&self) -> Option<u64> {
         match self {
-            Value::Numeric(NumericValue::U64(value)) => Some(*value),
+            Value::Numeric(NumericValue::U64(Fitted::Fit(value))) => Some(*value),
             _ => None,
         }
     }
@@ -154,12 +222,50 @@ impl Value {
         Ok(Self::array(values, vec![Type::Numeric(typ)]))
     }
 
-    // This is used in tests but shouldn't be cfg(test) only
-    #[allow(unused)]
-    pub(crate) fn bool(value: bool) -> Self {
+    pub fn bool(value: bool) -> Self {
         Self::Numeric(NumericValue::U1(value))
     }
 
+    pub fn field(value: FieldElement) -> Self {
+        Self::Numeric(NumericValue::Field(value))
+    }
+
+    pub fn u8(value: u8) -> Self {
+        Self::Numeric(NumericValue::U8(value.into()))
+    }
+
+    pub fn u16(value: u16) -> Self {
+        Self::Numeric(NumericValue::U16(value.into()))
+    }
+
+    pub fn u32(value: u32) -> Self {
+        Self::Numeric(NumericValue::U32(value.into()))
+    }
+
+    pub fn u128(value: u128) -> Self {
+        Self::Numeric(NumericValue::U128(value.into()))
+    }
+
+    pub fn u64(value: u64) -> Self {
+        Self::Numeric(NumericValue::U64(value.into()))
+    }
+
+    pub fn i8(value: i8) -> Self {
+        Self::Numeric(NumericValue::I8(value.into()))
+    }
+
+    pub fn i16(value: i16) -> Self {
+        Self::Numeric(NumericValue::I16(value.into()))
+    }
+
+    pub fn i32(value: i32) -> Self {
+        Self::Numeric(NumericValue::I32(value.into()))
+    }
+
+    pub fn i64(value: i64) -> Self {
+        Self::Numeric(NumericValue::I64(value.into()))
+    }
+
     pub fn array(elements: Vec<Value>, element_types: Vec<Type>) -> Self {
         Self::ArrayOrSlice(ArrayValue {
             elements: Shared::new(elements),
@@ -252,6 +358,15 @@ impl Value {
     pub fn snapshot_args(args: &[Value]) -> Vec<Value> {
         args.iter().map(|arg| arg.snapshot()).collect()
     }
+
+    /// Wrap a `Field` into an `Unfit`, with a type that we were _supposed_ to get,
+    /// had some operation not overflown.
+    ///
+    /// This is used only in tests to construct expected values.
+    #[cfg(test)]
+    pub(crate) fn unfit(field: FieldElement, typ: NumericType) -> IResult<Self> {
+        NumericValue::unfit(field, typ).map(Self::Numeric)
+    }
 }
 
 impl NumericValue {
@@ -289,6 +404,11 @@ impl NumericValue {
         }
     }
 
+    /// Create a `NumericValue` from a `Field` constant.
+    ///
+    /// Returns an error if the value does not fit into the number of bits indicated by the `NumericType`.
+    ///
+    /// Never creates `Fitted::Unfit` values.
     pub fn from_constant(constant: FieldElement, typ: NumericType) -> IResult<NumericValue> {
         use super::InternalError::{ConstantDoesNotFitInType, UnsupportedNumericType};
         use super::InterpreterError::Internal;
@@ -307,48 +427,56 @@ impl NumericValue {
             NumericType::Unsigned { bit_size: 8 } => constant
                 .try_into_u128()
                 .and_then(|x| x.try_into().ok())
+                .map(Fitted::Fit)
                 .map(Self::U8)
                 .ok_or(does_not_fit),
             NumericType::Unsigned { bit_size: 16 } => constant
                 .try_into_u128()
                 .and_then(|x| x.try_into().ok())
+                .map(Fitted::Fit)
                 .map(Self::U16)
                 .ok_or(does_not_fit),
             NumericType::Unsigned { bit_size: 32 } => constant
                 .try_into_u128()
                 .and_then(|x| x.try_into().ok())
+                .map(Fitted::Fit)
                 .map(Self::U32)
                 .ok_or(does_not_fit),
             NumericType::Unsigned { bit_size: 64 } => constant
                 .try_into_u128()
                 .and_then(|x| x.try_into().ok())
+                .map(Fitted::Fit)
                 .map(Self::U64)
                 .ok_or(does_not_fit),
             NumericType::Unsigned { bit_size: 128 } => {
-                constant.try_into_u128().map(Self::U128).ok_or(does_not_fit)
+                constant.try_into_u128().map(Fitted::Fit).map(Self::U128).ok_or(does_not_fit)
             }
             // Signed cases are a bit weird. We want to allow all values in the corresponding
             // unsigned range so we have to cast to the unsigned type first to see if it fits.
             // If it does, any values `>= 2^N / 2` for `iN` are interpreted as negative.
             NumericType::Signed { bit_size: 8 } => constant
                 .try_into_u128()
                 .and_then(|x| u8::try_from(x).ok())
-                .map(|x| Self::I8(x as i8))
+                .map(|x| Fitted::Fit(x as i8))
+                .map(Self::I8)
                 .ok_or(does_not_fit),
             NumericType::Signed { bit_size: 16 } => constant
                 .try_into_u128()
                 .and_then(|x| u16::try_from(x).ok())
-                .map(|x| Self::I16(x as i16))
+                .map(|x| Fitted::Fit(x as i16))
+                .map(Self::I16)
                 .ok_or(does_not_fit),
             NumericType::Signed { bit_size: 32 } => constant
                 .try_into_u128()
                 .and_then(|x| u32::try_from(x).ok())
-                .map(|x| Self::I32(x as i32))
+                .map(|x| Fitted::Fit(x as i32))
+                .map(Self::I32)
                 .ok_or(does_not_fit),
             NumericType::Signed { bit_size: 64 } => constant
                 .try_into_u128()
                 .and_then(|x| u64::try_from(x).ok())
-                .map(|x| Self::I64(x as i64))
+                .map(|x| Fitted::Fit(x as i64))
+                .map(Self::I64)
                 .ok_or(does_not_fit),
             typ => Err(Internal(UnsupportedNumericType { typ })),
         }
@@ -359,27 +487,50 @@ impl NumericValue {
             NumericValue::Field(field) => *field,
             NumericValue::U1(boolean) if *boolean => FieldElement::one(),
             NumericValue::U1(_) => FieldElement::zero(),
-            NumericValue::U8(value) => FieldElement::from(u32::from(*value)),
-            NumericValue::U16(value) => FieldElement::from(u32::from(*value)),
-            NumericValue::U32(value) => FieldElement::from(*value),
-            NumericValue::U64(value) => FieldElement::from(*value),
-            NumericValue::U128(value) => FieldElement::from(*value),
+            NumericValue::U8(Fitted::Fit(value)) => FieldElement::from(u32::from(*value)),
+            NumericValue::U16(Fitted::Fit(value)) => FieldElement::from(u32::from(*value)),
+            NumericValue::U32(Fitted::Fit(value)) => FieldElement::from(*value),
+            NumericValue::U64(Fitted::Fit(value)) => FieldElement::from(*value),
+            NumericValue::U128(Fitted::Fit(value)) => FieldElement::from(*value),
             // Need to cast possibly negative values to the unsigned variants
             // first to ensure they are zero-extended rather than sign-extended
-            NumericValue::I8(value) => FieldElement::from(i128::from(*value as u8)),
-            NumericValue::I16(value) => FieldElement::from(i128::from(*value as u16)),
-            NumericValue::I32(value) => FieldElement::from(i128::from(*value as u32)),
-            NumericValue::I64(value) => FieldElement::from(i128::from(*value as u64)),
+            NumericValue::I8(Fitted::Fit(value)) => FieldElement::from(i128::from(*value as u8)),
+            NumericValue::I16(Fitted::Fit(value)) => FieldElement::from(i128::from(*value as u16)),
+            NumericValue::I32(Fitted::Fit(value)) => FieldElement::from(i128::from(*value as u32)),
+            NumericValue::I64(Fitted::Fit(value)) => FieldElement::from(i128::from(*value as u64)),
+
+            NumericValue::U8(Fitted::Unfit(value))
+            | NumericValue::U16(Fitted::Unfit(value))
+            | NumericValue::U32(Fitted::Unfit(value))
+            | NumericValue::U64(Fitted::Unfit(value))
+            | NumericValue::U128(Fitted::Unfit(value))
+            | NumericValue::I8(Fitted::Unfit(value))
+            | NumericValue::I16(Fitted::Unfit(value))
+            | NumericValue::I32(Fitted::Unfit(value))
+            | NumericValue::I64(Fitted::Unfit(value)) => *value,
         }
     }
 
-    pub fn is_negative(&self) -> bool {
-        match self {
-            NumericValue::I8(v) => *v < 0,
-            NumericValue::I16(v) => *v < 0,
-            NumericValue::I32(v) => *v < 0,
-            NumericValue::I64(v) => *v < 0,
-            _ => false,
+    /// Creates a `NumericValue` of a specific bit size with a `Fitted::Unfit` value.
+    #[cfg(test)]
+    pub fn unfit(field: FieldElement, typ: NumericType) -> IResult<NumericValue> {
+        use super::InternalError::UnsupportedNumericType;
+        use super::InterpreterError::Internal;
+
+        match typ {
+            NumericType::NativeField | NumericType::Unsigned { bit_size: 1 } => {
+                unreachable!("{typ} cannot be unfit")
+            }
+            NumericType::Unsigned { bit_size: 8 } => Ok(Self::U8(Fitted::Unfit(field))),
+            NumericType::Unsigned { bit_size: 16 } => Ok(Self::U16(Fitted::Unfit(field))),
+            NumericType::Unsigned { bit_size: 32 } => Ok(Self::U32(Fitted::Unfit(field))),
+            NumericType::Unsigned { bit_size: 64 } => Ok(Self::U64(Fitted::Unfit(field))),
+            NumericType::Unsigned { bit_size: 128 } => Ok(Self::U128(Fitted::Unfit(field))),
+            NumericType::Signed { bit_size: 8 } => Ok(Self::I8(Fitted::Unfit(field))),
+            NumericType::Signed { bit_size: 16 } => Ok(Self::I16(Fitted::Unfit(field))),
+            NumericType::Signed { bit_size: 32 } => Ok(Self::I32(Fitted::Unfit(field))),
+            NumericType::Signed { bit_size: 64 } => Ok(Self::I64(Fitted::Unfit(field))),
+            typ => Err(Internal(UnsupportedNumericType { typ })),
         }
     }
 }
@@ -397,6 +548,16 @@ impl std::fmt::Display for Value {
     }
 }
 
+impl<T: std::fmt::Display> std::fmt::Display for Fitted<T> {
+    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
+        match self {
+            Fitted::Fit(v) => v.fmt(f),
+            // Distinguish an overflowed value from the type it's supposed to be.
+            Fitted::Unfit(v) => write!(f, "({v})"),
+        }
+    }
+}
+
 impl std::fmt::Display for NumericValue {
     fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
         match self {
@@ -436,19 +597,22 @@ impl std::fmt::Display for ArrayValue {
         if self.element_types.len() == 1
             && matches!(self.element_types[0], Type::Numeric(NumericType::Unsigned { bit_size: 8 }))
         {
-            let printable = self.elements.borrow().iter().all(|value| {
-                matches!(value, Value::Numeric(NumericValue::U8(byte)) if is_printable_byte(*byte))
-            });
+            let printable = self
+                .elements
+                .borrow()
+                .iter()
+                .all(|value| value.as_u8().is_some_and(is_printable_byte));
+
             if printable {
                 let bytes = self
                     .elements
                     .borrow()
                     .iter()
                     .map(|value| {
-                        let Value::Numeric(NumericValue::U8(byte)) = value else {
+                        let Some(byte) = value.as_u8() else {
                             panic!("Expected U8 value in array, found {value}");
                         };
-                        *byte
+                        byte
                     })
                     .collect::<Vec<_>>();
                 let string = String::from_utf8(bytes).unwrap();
```

### compiler/noirc_evaluator/src/ssa/opt/expand_signed_math.rs
```diff
@@ -326,11 +326,7 @@ fn expand_signed_math_post_check(func: &Function) {
 mod tests {
     use crate::{
         assert_ssa_snapshot,
-        ssa::{
-            interpreter::value::{NumericValue, Value},
-            opt::assert_ssa_does_not_change,
-            ssa_gen::Ssa,
-        },
+        ssa::{interpreter::value::Value, opt::assert_ssa_does_not_change, ssa_gen::Ssa},
     };
 
     #[test]
@@ -357,14 +353,11 @@ mod tests {
             (20, -10, false),
         ];
         for (lhs, rhs, expected) in test_cases {
-            let result = ssa.interpret(vec![
-                Value::Numeric(NumericValue::I8(lhs)),
-                Value::Numeric(NumericValue::I8(rhs)),
-            ]);
+            let result = ssa.interpret(vec![Value::i8(lhs), Value::i8(rhs)]);
             assert!(result.is_ok());
             let result = result.unwrap();
             assert_eq!(result.len(), 1);
-            assert_eq!(result[0], Value::Numeric(NumericValue::U1(expected)));
+            assert_eq!(result[0], Value::bool(expected));
         }
 
         assert_ssa_snapshot!(ssa, @r"
@@ -409,17 +402,11 @@ mod tests {
         let ssa = ssa.expand_signed_math();
 
         // Check that -128 i8 / -1 i8 overflows
-        let result = ssa.interpret(vec![
-            Value::Numeric(NumericValue::I8(-128)),
-            Value::Numeric(NumericValue::I8(-1)),
-        ]);
+        let result = ssa.interpret(vec![Value::i8(-128), Value::i8(-1)]);
         assert!(result.is_err());
 
         // Check that 10 i8 / 0 i8 overflows
-        let result = ssa.interpret(vec![
-            Value::Numeric(NumericValue::I8(10)),
-            Value::Numeric(NumericValue::I8(0)),
-        ]);
+        let result = ssa.interpret(vec![Value::i8(10), Value::i8(0)]);
         assert!(result.is_err());
 
         assert_ssa_snapshot!(ssa, @r#"
@@ -485,17 +472,11 @@ mod tests {
         let ssa = ssa.expand_signed_math();
 
         // Check that -128 i8 / -1 i8 overflows
-        let result = ssa.interpret(vec![
-            Value::Numeric(NumericValue::I8(-128)),
-            Value::Numeric(NumericValue::I8(-1)),
-        ]);
+        let result = ssa.interpret(vec![Value::i8(-128), Value::i8(-1)]);
         assert!(result.is_err());
 
         // Check that 10 i8 / 0 i8 overflows
-        let result = ssa.interpret(vec![
-            Value::Numeric(NumericValue::I8(10)),
-            Value::Numeric(NumericValue::I8(0)),
-        ]);
+        let result = ssa.interpret(vec![Value::i8(10), Value::i8(0)]);
         assert!(result.is_err());
 
         assert_ssa_snapshot!(ssa, @r#"
```

### tooling/ast_fuzzer/src/compare/interpreted.rs
```diff
@@ -299,10 +299,8 @@ fn append_input_value_to_ssa(typ: &AbiType, input: &InputValue, values: &mut Vec
             let num_val = NumericValue::from_constant(*f, num_typ).expect("cannot create constant");
             values.push(Value::Numeric(num_val));
         }
-        InputValue::String(s) => values.push(array_value(
-            vecmap(s.as_bytes(), |b| Value::Numeric(NumericValue::U8(*b))),
-            vec![Type::unsigned(8)],
-        )),
+        InputValue::String(s) => values
+            .push(array_value(vecmap(s.as_bytes(), |b| Value::u8(*b)), vec![Type::unsigned(8)])),
         InputValue::Vec(input_values) => match typ {
             AbiType::Array { length, typ } => {
                 assert_eq!(*length as usize, input_values.len(), "array length != input length");
```
