# [?] fix: Report logical index in OOB error in dynamic composite arrays (#13237)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-07-02
Source: https://github.com/noir-lang/noir/commit/d09de15576e130975e15ad3a388c44619e76d8b9
Type: security-commit

## Details
fix: Report logical index in OOB error in dynamic composite arrays (#13237)

## Patch
### compiler/noirc_evaluator/src/ssa/ssa_gen/context.rs
```diff
@@ -122,11 +122,17 @@ type FunctionQueue = Vec<(FuncId, IrFunctionId)>;
 /// store has zero cells to write — so the implicit check is missing and an
 /// explicit one must be emitted. Brillig has no implicit check at all and
 /// always needs the explicit one. `array_type` must be a `Type::Array`.
+///
+/// When the element flattens to more than one ACIR cell (a composite type such
+/// as a tuple or struct), the implicit memory op check reports the *flattened*
+/// index and size (e.g. `index * element_size`), which are detached from the
+/// logical index and length the user wrote. An explicit check is emitted so the
+/// error can report the logical values instead.
 pub(super) fn array_index_needs_explicit_oob_check(
     runtime: RuntimeType,
     array_type: &Type,
 ) -> bool {
-    runtime.is_brillig() || array_type.element_size().0 == 0
+    runtime.is_brillig() || array_type.element_size().0 != 1
 }
 
 impl<'a> FunctionContext<'a> {
@@ -884,11 +890,22 @@ impl<'a> FunctionContext<'a> {
                 match array_type {
                     Type::Array(_, len) => {
                         if array_index_needs_explicit_oob_check(runtime, array_type) {
-                            let len = self
-                                .builder
-                                .numeric_constant(u128::from(len.0), NumericType::length_type());
+                            let logical_len = len.0;
+                            // A composite element type flattens the memory op index, so attach a
+                            // dynamic error reporting the logical index and length (see the read
+                            // path in `codegen_array_index`).
+                            let dynamic_error =
+                                if runtime.is_acir() && array_type.element_size().0 > 1 {
+                                    Some(self.out_of_bounds_error(index, logical_len))
+                                } else {
+                                    None
+                                };
+                            let len = self.builder.numeric_constant(
+                                u128::from(logical_len),
+                                NumericType::length_type(),
+                            );
                             self.builder.set_location(location);
-                            self.codegen_access_check(index, len);
+                            self.codegen_access_check(index, len, dynamic_error);
                         }
                     }
                     _ => unreachable!("must have array or vector but got {array_type}"),
@@ -905,7 +922,7 @@ impl<'a> FunctionContext<'a> {
                 // Checks for index Out-of-bounds
                 match array_type {
                     Type::Vector(_) => {
-                        self.codegen_access_check(index, vector_values[0]);
+                        self.codegen_access_check(index, vector_values[0], None);
                     }
                     _ => unreachable!("must have array or vector but got {array_type}"),
                 }
```

### compiler/noirc_evaluator/src/ssa/ssa_gen/mod.rs
```diff
@@ -551,10 +551,19 @@ impl FunctionContext<'_> {
         match array_type {
             Type::Array(_, len) => {
                 if context::array_index_needs_explicit_oob_check(runtime, array_type) {
+                    let logical_len = len.0;
+                    // For a composite element type, ACIR's implicit memory op check reports the
+                    // flattened index and size. Attach a dynamic error carrying the logical index
+                    // and length so the reported message matches what the user wrote.
+                    let dynamic_error = if runtime.is_acir() && array_type.element_size().0 > 1 {
+                        Some(self.out_of_bounds_error(index, logical_len))
+                    } else {
+                        None
+                    };
                     let len = self
                         .builder
-                        .numeric_constant(u128::from(len.0), NumericType::length_type());
-                    self.codegen_access_check(index, len);
+                        .numeric_constant(u128::from(logical_len), NumericType::length_type());
+                    self.codegen_access_check(index, len, dynamic_error);
                 }
             }
             Type::Vector(_) => {
@@ -563,6 +572,7 @@ impl FunctionContext<'_> {
                 self.codegen_access_check(
                     index,
                     length.expect("ICE: a length must be supplied for checking index"),
+                    None,
                 );
             }
 
@@ -595,11 +605,19 @@ impl FunctionContext<'_> {
     /// Prepare an array or vector access.
     /// Check that the index being used to access an array/vector element
     /// is less than the (potentially dynamic) array/vector length.
-    fn codegen_access_check(&mut self, index: ValueId, length: ValueId) {
+    ///
+    /// When `dynamic_error` is `Some`, that error is used as the failure message and the
+    /// range-check optimization is skipped (a range-check opcode can only carry a static
+    /// message). Otherwise a static `"Index out of bounds"` message is used.
+    fn codegen_access_check(
+        &mut self,
+        index: ValueId,
+        length: ValueId,
+        dynamic_error: Option<ConstrainError>,
+    ) {
         let index = self.make_array_index(index);
         // We convert the length as an array index type for comparison
         let array_len = self.make_array_index(length);
-        let assert_message = Some("Index out of bounds".to_owned());
 
         let array_len_constant = self
             .builder
@@ -610,7 +628,10 @@ impl FunctionContext<'_> {
 
         // This optimization seems to cause regressions in brillig so we restrict it to ACIR.
         let runtime = self.builder.current_function.runtime();
-        if runtime.is_acir() && array_len_constant.is_some_and(u32::is_power_of_two) {
+        if dynamic_error.is_none()
+            && runtime.is_acir()
+            && array_len_constant.is_some_and(u32::is_power_of_two)
+        {
             // If the array length is a power of two then we can make use of the range check opcode
             // to assert that the index fits in the relevant number of bits.
             let array_len_constant = array_len_constant.expect("array checked to be constant");
@@ -619,21 +640,55 @@ impl FunctionContext<'_> {
             // TODO(https://github.com/noir-lang/noir/issues/9191): this cast results in better circuit generation.
             // There's an optimization here that we should find automatically.
             let index_as_field = self.builder.insert_cast(index, NumericType::NativeField);
-            self.builder.insert_range_check(index_as_field, array_len_bits, assert_message);
+            self.builder.insert_range_check(
+                index_as_field,
+                array_len_bits,
+                Some("Index out of bounds".to_owned()),
+            );
         } else {
             // If it's not a power of two then we need to do an explicit inequality and constraint.
             let is_offset_out_of_bounds =
                 self.builder.insert_binary(index, BinaryOp::Lt, array_len);
             let true_const = self.builder.numeric_constant(true, NumericType::bool());
+            let error = dynamic_error
+                .unwrap_or_else(|| ConstrainError::from("Index out of bounds".to_owned()));
 
-            self.builder.insert_constrain(
-                is_offset_out_of_bounds,
-                true_const,
-                assert_message.map(ConstrainError::from),
-            );
+            self.builder.insert_constrain(is_offset_out_of_bounds, true_const, Some(error));
         }
     }
 
+    /// Build a dynamic (format-string) assertion error that renders as
+    /// `Index out of bounds, array has size <array_len>, but index was <index>`, where `index`
+    /// is a runtime value and `array_len` is the logical array length (a compile-time constant).
+    ///
+    /// This matches the message ACVM produces for simple (non-composite) arrays, but reports the
+    /// logical index and length rather than the flattened memory coordinates.
+    fn out_of_bounds_error(&mut self, index: ValueId, array_len: u32) -> ConstrainError {
+        // The template holds a single `{}` interpolation for the runtime index; the logical length
+        // is a compile-time constant so it is baked directly into the static text.
+        let template =
+            format!("Index out of bounds, array has size {array_len}, but index was {{}}");
+        let template_len = template.len() as u32;
+
+        // A format string is represented by the message string, the number of fields to be
+        // formatted, and then the fields themselves.
+        let string = self.codegen_string(template.as_bytes());
+        let field_count = self.builder.numeric_constant(1_u128, NumericType::NativeField);
+        // Render the index as the array-index type (u32) to match the `HirType::u32()` field below.
+        let index = self.make_array_index(index);
+        let values =
+            Tree::Branch(vec![string, field_count.into(), index.into()]).into_value_list(self);
+
+        let hir_type = HirType::FmtString(
+            Box::new(HirType::constant_u32(template_len)),
+            Box::new(HirType::Tuple(vec![HirType::u32()])),
+        );
+        let selector = ErrorType::Dynamic(hir_type.clone()).selector();
+        self.builder.record_error_type(selector, hir_type);
+
+        ConstrainError::Dynamic(selector, false, values)
+    }
+
     fn codegen_cast(&mut self, cast: &ast::Cast) -> Result<Values, RuntimeError> {
         let lhs = self.codegen_non_tuple_expression(&cast.lhs)?;
         let typ = Self::convert_non_tuple_type(&cast.r#type).unwrap_numeric();
@@ -1390,10 +1445,10 @@ impl FunctionContext<'_> {
                         one,
                     );
 
-                    self.codegen_access_check(arguments[2], len_plus_one);
+                    self.codegen_access_check(arguments[2], len_plus_one, None);
                 }
                 Intrinsic::VectorRemove => {
-                    self.codegen_access_check(arguments[2], arguments[0]);
+                    self.codegen_access_check(arguments[2], arguments[0], None);
                 }
                 Intrinsic::VectorPopFront | Intrinsic::VectorPopBack
                     if self.builder.current_function.runtime().is_brillig() =>
@@ -1407,7 +1462,7 @@ impl FunctionContext<'_> {
                     // By doing this in the SSA we might be able to optimize this away later.
                     let zero =
                         self.builder.numeric_constant(0u32, NumericType::Unsigned { bit_size: 32 });
-                    self.codegen_access_check(zero, arguments[0]);
+                    self.codegen_access_check(zero, arguments[0], None);
                 }
                 _ => {
                     // Do nothing as the other intrinsics do not require checks
```

### test_programs/execution_failure/dynamic_index_composite_failure/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "dynamic_index_composite_failure"
+type = "bin"
+authors = [""]
+
+[dependencies]
```

### test_programs/execution_failure/dynamic_index_composite_failure/Prover.toml
```diff
@@ -0,0 +1 @@
+i = "10"
```

### test_programs/execution_failure/dynamic_index_composite_failure/src/main.nr
```diff
@@ -0,0 +1,4 @@
+fn main(i: u32) -> pub bool {
+    let a: [(Field, bool); 2] = [(10, false), (22, true)];
+    a[i].1
+}
```

### tooling/ast_fuzzer/src/compare/compiled.rs
```diff
@@ -9,6 +9,7 @@ use color_eyre::eyre::{self, WrapErr};
 use nargo::{NargoError, errors::ExecutionError, foreign_calls::DefaultForeignCallBuilder};
 use noirc_abi::{Abi, InputMap, input_parser::InputValue};
 use noirc_evaluator::{ErrorType, ssa::SsaProgramArtifact};
+use noirc_frontend::hir_def::types::Type as HirType;
 use noirc_frontend::monomorphization::ast::Program;
 
 use crate::{Config, arb_inputs, arb_program, compare::logging, program_abi};
@@ -52,15 +53,28 @@ impl NargoErrorWithTypes {
                     if let Some(ssa_type) = self.1.get(&raw.selector) {
                         match ssa_type {
                             ErrorType::String(message) => Some(message.clone()),
-                            ErrorType::Dynamic(_hir_type) => {
+                            ErrorType::Dynamic(hir_type) => {
                                 // A non-literal assert message — for example an `if`-expression that
                                 // produces a string, as the metamorphic rewriter can introduce — is
                                 // recorded by `codegen_constrain_error` as `ErrorType::Dynamic`, even
                                 // when its type is a plain string. Recover the message from the raw
                                 // payload bytes when they encode a string, matching the encoding of
-                                // `ConstrainError::Dynamic { is_string_type: true, .. }`. Genuine
-                                // format strings need the raw payload decoded as an ABI type, which the
-                                // mapper in `crate::abi` doesn't handle yet, so they fall back to `None`.
+                                // `ConstrainError::Dynamic { is_string_type: true, .. }`.
+                                //
+                                // A format string (as synthesized for the composite-array
+                                // out-of-bounds error) encodes its template text in the leading
+                                // `length` fields, followed by the field count and the formatted
+                                // values. Decode just the template — it is enough to match the error
+                                // textually and avoids needing full ABI formatting of the values.
+                                if let HirType::FmtString(length, _) = hir_type
+                                    && let HirType::Constant(int) = length.as_ref()
+                                    && let Some(len) = int.as_field().try_to_u64()
+                                {
+                                    return raw
+                                        .data
+                                        .get(..len as usize)
+                                        .and_then(decode_raw_string_payload);
+                                }
                                 decode_raw_string_payload(&raw.data)
                             }
                         }
@@ -594,4 +608,58 @@ mod tests {
 
         assert!(NargoErrorWithTypes::equivalent(&dynamic_error, &static_string_error));
     }
+
+    #[test]
+    fn matches_acir_dynamic_fmtstr_oob_with_brillig_string() {
+        // Regression test for the `acir_vs_brillig` failure with seed 0x6c3ad1760003227e.
+        //
+        // A dynamic read of a composite array (element size > 1) out of bounds is reported in
+        // ACIR by a synthesized format-string assertion carrying the logical index and length
+        // (`ConstrainError::Dynamic` with an `ErrorType::Dynamic(fmtstr<_, (u32,)>)`). Its raw
+        // payload is the template bytes, followed by the field count and the formatted index
+        // value. In Brillig the same access surfaces as a plain `"Index out of bounds"` string.
+        // Extracting the template message from the fmtstr payload is what lets the comparator
+        // treat the two as equivalent.
+        let template = "Index out of bounds, array has size 4, but index was {}";
+        let mut data: Vec<FieldElement> =
+            template.bytes().map(|b| FieldElement::from(u32::from(b))).collect();
+        // Format string layout: template bytes, then the field count, then the formatted values.
+        data.push(FieldElement::from(1u32));
+        data.push(FieldElement::from(869191887u32));
+
+        let fmtstr_type = HirType::FmtString(
+            Box::new(HirType::Constant(Integer::U32(template.len() as u32))),
+            Box::new(HirType::Tuple(vec![HirType::u32()])),
+        );
+        let acir_selector = ErrorSelector::new(9034042597070725729);
+        let acir_error = NargoErrorWithTypes(
+            nargo::NargoError::ExecutionError(ExecutionError::AssertionFailed(
+                ResolvedAssertionPayload::Raw(RawAssertionPayload {
+                    selector: acir_selector,
+                    data,
+                }),
+                Vec::new(),
+                None,
+            )),
+            BTreeMap::from_iter([(acir_selector, ErrorType::Dynamic(fmtstr_type))]),
+        );
+
+        let brillig_selector = ErrorSelector::new(16431471497789672479);
+        let brillig_error = NargoErrorWithTypes(
+            nargo::NargoError::ExecutionError(ExecutionError::AssertionFailed(
+                ResolvedAssertionPayload::Raw(RawAssertionPayload {
+                    selector: brillig_selector,
+                    data: vec![],
+                }),
+                Vec::new(),
+                Some(BrilligFunctionId::new(0)),
+            )),
+            BTreeMap::from_iter([(
+                brillig_selector,
+                ErrorType::String("Index out of bounds".to_string()),
+            )]),
+        );
+
+        assert!(NargoErrorWithTypes::equivalent(&acir_error, &brillig_error));
+    }
 }
```

### tooling/nargo_cli/tests/snapshots/execution_failure/dyn_index_fail_nested_array/execute__tests__acir_stderr.snap
```diff
@@ -2,7 +2,7 @@
 source: tooling/nargo_cli/tests/execute.rs
 expression: stderr
 ---
-error: Index out of bounds, array has size 6, but index was 8
+error: Assertion failed: Index out of bounds, array has size 3, but index was 4
   ┌─ src/main.nr:7:12
   │
 7 │     assert(x[y + 2].a == 5);
@@ -12,4 +12,4 @@ error: Index out of bounds, array has size 6, but index was 8
     1: main
             at src/main.nr:7:12
 
-Failed to solve program: 'Index out of bounds, array has size 6, but index was 8'
+Failed assertion
```

### tooling/nargo_cli/tests/snapshots/execution_failure/dynamic_index_composite_failure/execute__tests__acir_stderr.snap
```diff
@@ -0,0 +1,15 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Assertion failed: Index out of bounds, array has size 2, but index was 10
+  ┌─ src/main.nr:3:5
+  │
+3 │     a[i].1
+  │     ----
+  │
+  = Call stack:
+    1: main
+            at src/main.nr:3:5
+
+Failed assertion
```

### tooling/nargo_cli/tests/snapshots/execution_failure/dynamic_index_composite_failure/execute__tests__brillig_stderr.snap
```diff
@@ -0,0 +1,15 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Assertion failed: Index out of bounds
+  ┌─ src/main.nr:3:5
+  │
+3 │     a[i].1
+  │     ----
+  │
+  = Call stack:
+    1: main
+            at src/main.nr:3:5
+
+Failed assertion
```

### tooling/nargo_cli/tests/snapshots/execution_failure/dynamic_index_composite_failure/execute__tests__comptime_stderr.snap
```diff
@@ -0,0 +1,12 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Index out of bounds: 10 is out of bounds for the array of length 2
+  ┌─ src/main.nr:3:5
+  │
+3 │     a[i].1
+  │     ----
+  │
+
+Error interpreting main function
```

### tooling/nargo_cli/tests/snapshots/execution_failure/lambda_from_empty_array_dyn_index/execute__tests__acir_stderr.snap
```diff
@@ -2,7 +2,7 @@
 source: tooling/nargo_cli/tests/execute.rs
 expression: stderr
 ---
-bug: Assertion is always false: Index out of bounds
+bug: Assertion is always false
   ┌─ src/main.nr:5:5
   │
 5 │     lambdas[x - 1](());
@@ -12,7 +12,7 @@ bug: Assertion is always false: Index out of bounds
     1: main
             at src/main.nr:5:5
 
-error: Assertion failed: Index out of bounds
+error: Assertion failed: Index out of bounds, array has size 0, but index was 0
   ┌─ src/main.nr:5:5
   │
 5 │     lambdas[x - 1](());
```

### tooling/nargo_cli/tests/snapshots/execution_failure/regression_7759/execute__tests__acir_stderr.snap
```diff
@@ -2,7 +2,7 @@
 source: tooling/nargo_cli/tests/execute.rs
 expression: stderr
 ---
-error: Index out of bounds, array has size 4, but index was 4294967296
+error: Assertion failed: Index out of bounds, array has size 2, but index was 2147483648
   ┌─ src/main.nr:3:5
   │
 3 │     v7[index]
@@ -12,4 +12,4 @@ error: Index out of bounds, array has size 4, but index was 4294967296
     1: main
             at src/main.nr:3:5
 
-Failed to solve program: 'Index out of bounds, array has size 4, but index was 4294967296'
+Failed assertion
```
