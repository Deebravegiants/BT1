# [?] fix: signed right shift overflows to 0 or -1 (#8805)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-06-06
Source: https://github.com/noir-lang/noir/commit/a03782e881d808b6f9ef9eaaa6e474959318832d
Type: security-commit

## Details
fix: signed right shift overflows to 0 or -1 (#8805)

## Patch
### compiler/noirc_evaluator/src/brillig/brillig_gen/brillig_block.rs
```diff
@@ -1652,7 +1652,7 @@ impl<'block, Registers: RegisterAllocator> BrilligBlock<'block, Registers> {
 
         self.brillig_context.codegen_branch(left_is_negative.address, |ctx, is_negative| {
             if is_negative {
-                // If right value is greater than the left bit size, return 0
+                // If right value is greater than the left bit size, return -1
                 let rhs_does_not_overflow = SingleAddrVariable::new(ctx.allocate_register(), 1);
                 let lhs_bit_size =
                     ctx.make_constant_instruction(left.bit_size.into(), right.bit_size);
@@ -1688,7 +1688,7 @@ impl<'block, Registers: RegisterAllocator> BrilligBlock<'block, Registers> {
                         ctx.deallocate_single_addr(two_pow);
                         ctx.deallocate_single_addr(right_u32);
                     } else {
-                        ctx.const_instruction(result, 0_u128.into());
+                        ctx.const_instruction(result, ((1_u128 << left.bit_size) - 1).into());
                     }
                 });
 
```

### compiler/noirc_evaluator/src/ssa/ir/dfg/simplify/binary.rs
```diff
@@ -293,9 +293,11 @@ pub(super) fn simplify_binary(binary: &Binary, dfg: &mut DataFlowGraph) -> Simpl
             // Bit shifts by constants can be treated as divisions.
             if let Some(rhs_const) = rhs_value {
                 if rhs_const >= FieldElement::from(lhs_type.bit_size() as u128) {
-                    // Shifting by the full width of the operand type, any `lhs` goes to zero.
-                    let zero = dfg.make_constant(FieldElement::zero(), lhs_type);
-                    return SimplifyResult::SimplifiedTo(zero);
+                    // Shifting by the full width of the operand type, any unsigned `lhs` goes to zero.
+                    if lhs_type.is_unsigned() {
+                        let zero = dfg.make_constant(FieldElement::zero(), lhs_type);
+                        return SimplifyResult::SimplifiedTo(zero);
+                    }
                 }
                 return SimplifyResult::SimplifiedToInstruction(simplified);
             }
```

### compiler/noirc_evaluator/src/ssa/ir/instruction/binary.rs
```diff
@@ -143,7 +143,7 @@ pub(crate) fn eval_constant_binary_op(
                 }
                 BinaryOp::Shr => {
                     if rhs >= bit_size as i128 {
-                        0
+                        if lhs >= 0 { 0 } else { -1 }
                     } else {
                         result?
                     }
```

### compiler/noirc_evaluator/src/ssa/opt/remove_bit_shifts.rs
```diff
@@ -170,6 +170,8 @@ impl Context<'_, '_, '_> {
         let rhs_is_less_than_bit_size = self.insert_binary(rhs, BinaryOp::Lt, bit_size_value);
         let rhs_is_less_than_bit_size_with_rhs_typ =
             self.insert_cast(rhs_is_less_than_bit_size, rhs_typ);
+        let rhs_is_less_than_bit_size_with_lhs_typ =
+            self.insert_cast(rhs_is_less_than_bit_size, lhs_typ);
         // Nullify rhs in case of overflow, to ensure that pow returns a value compatible with lhs
         let rhs = self.insert_binary(
             rhs_is_less_than_bit_size_with_rhs_typ,
@@ -178,49 +180,75 @@ impl Context<'_, '_, '_> {
         );
         let pow = self.pow(base, rhs);
         let pow = self.insert_cast(pow, lhs_typ);
-        let result = if lhs_typ.is_unsigned() {
+
+        if lhs_typ.is_unsigned() {
             // unsigned right bit shift is just a normal division
-            self.insert_binary(lhs, BinaryOp::Div, pow)
-        } else {
-            // Get the sign of the operand; positive signed operand will just do a division as well
-            let zero = self.numeric_constant(FieldElement::zero(), NumericType::signed(bit_size));
-            let lhs_sign = self.insert_binary(lhs, BinaryOp::Lt, zero);
-            let lhs_sign_as_field = self.insert_cast(lhs_sign, NumericType::NativeField);
-            let lhs_as_field = self.insert_cast(lhs, NumericType::NativeField);
-            // For negative numbers, convert to 1-complement using wrapping addition of a + 1
-            // Unchecked add as these are fields
-            let one_complement = self.insert_binary(
-                lhs_sign_as_field,
-                BinaryOp::Add { unchecked: true },
-                lhs_as_field,
-            );
-            let one_complement = self.insert_truncate(one_complement, bit_size, bit_size + 1);
-            let one_complement = self.insert_cast(one_complement, NumericType::signed(bit_size));
-            // Performs the division on the 1-complement (or the operand if positive)
-            let shifted_complement = self.insert_binary(one_complement, BinaryOp::Div, pow);
-            // Convert back to 2-complement representation if operand is negative
-            let lhs_sign_as_int = self.insert_cast(lhs_sign, lhs_typ);
-
-            // The requirements for this to underflow are all of these:
-            // - lhs < 0
-            // - ones_complement(lhs) / (2^rhs) == 0
-            // As the upper bit is set for the ones complement of negative numbers we'd need 2^rhs
-            // to be larger than the lhs bitsize for this to overflow.
-            let shifted = self.insert_binary(
-                shifted_complement,
-                BinaryOp::Sub { unchecked: true },
-                lhs_sign_as_int,
+            let result = self.insert_binary(lhs, BinaryOp::Div, pow);
+            // In  case of overflow, pow is 1, because rhs was nullified, so we return explicitly 0.
+            return self.insert_binary(
+                rhs_is_less_than_bit_size_with_lhs_typ,
+                BinaryOp::Mul { unchecked: true },
+                result,
             );
-            self.insert_truncate(shifted, bit_size, bit_size + 1)
-        };
-        // Returns 0 in case of overflow
-        let rhs_is_less_than_bit_size_with_lhs_typ =
-            self.insert_cast(rhs_is_less_than_bit_size, lhs_typ);
-        self.insert_binary(
+        }
+        // Get the sign of the operand; positive signed operand will just do a division as well
+        let zero = self.numeric_constant(FieldElement::zero(), NumericType::signed(bit_size));
+        let lhs_sign = self.insert_binary(lhs, BinaryOp::Lt, zero);
+        let lhs_sign_as_field = self.insert_cast(lhs_sign, NumericType::NativeField);
+        let lhs_as_field = self.insert_cast(lhs, NumericType::NativeField);
+        // For negative numbers, convert to 1-complement using wrapping addition of a + 1
+        // Unchecked add as these are fields
+        let one_complement =
+            self.insert_binary(lhs_sign_as_field, BinaryOp::Add { unchecked: true }, lhs_as_field);
+        let one_complement = self.insert_truncate(one_complement, bit_size, bit_size + 1);
+        let one_complement = self.insert_cast(one_complement, NumericType::signed(bit_size));
+        // Performs the division on the 1-complement (or the operand if positive)
+        let shifted_complement = self.insert_binary(one_complement, BinaryOp::Div, pow);
+        // Convert back to 2-complement representation if operand is negative
+        let lhs_sign_as_int = self.insert_cast(lhs_sign, lhs_typ);
+
+        // The requirements for this to underflow are all of these:
+        // - lhs < 0
+        // - ones_complement(lhs) / (2^rhs) == 0
+        // As the upper bit is set for the ones complement of negative numbers we'd need 2^rhs
+        // to be larger than the lhs bitsize for this to overflow.
+        let shifted = self.insert_binary(
+            shifted_complement,
+            BinaryOp::Sub { unchecked: true },
+            lhs_sign_as_int,
+        );
+        let result = self.insert_truncate(shifted, bit_size, bit_size + 1);
+
+        // Returns 0 or -1 in case of overflow:
+        // In  case of overflow, and because rhs was nullified, we need to
+        // return the correct value, which is 0 or -1 depending on the sign of lhs
+
+        // Computes -1, or 0 if lhs is positive: is the expected result if there is an overflow
+        let minus_one = self.numeric_constant(
+            NumericType::Unsigned { bit_size }.max_value().expect("Invalid bit size"),
+            lhs_typ,
+        );
+        let minus_one_or_zero =
+            self.insert_binary(minus_one, BinaryOp::Mul { unchecked: true }, lhs_sign_as_int);
+        // -1, or 0 if lhs is positve or if there is no overflow
+        let one = self.numeric_constant(FieldElement::one(), lhs_typ);
+        let no_overflow = self.insert_binary(
+            one,
+            BinaryOp::Sub { unchecked: true },
+            rhs_is_less_than_bit_size_with_lhs_typ,
+        );
+        let minus_one_or_zero =
+            self.insert_binary(minus_one_or_zero, BinaryOp::Mul { unchecked: true }, no_overflow);
+
+        // predicated result: 0 if overflow, else: result
+        let result = self.insert_binary(
             rhs_is_less_than_bit_size_with_lhs_typ,
             BinaryOp::Mul { unchecked: true },
             result,
-        )
+        );
+
+        // result + minus_one_or_zero gives the expected result in all cases
+        self.insert_binary(result, BinaryOp::Add { unchecked: true }, minus_one_or_zero)
     }
 
     /// Computes lhs^rhs via square&multiply, using the bits decomposition of rhs
```

### compiler/noirc_frontend/src/hir/comptime/interpreter/infix.rs
```diff
@@ -196,8 +196,7 @@ pub(super) fn evaluate_infix(
             (lhs_value as lhs "^" rhs_value as rhs) => lhs ^ rhs
         },
         BinaryOpKind::ShiftRight => match_bitshift! {
-            // Overflow on shift-right returns 0 in Noir
-            (lhs_value as lhs ">>" rhs_value as rhs) => lhs.checked_shr(rhs.into()).or(Some(0))
+            (lhs_value as lhs ">>" rhs_value as rhs) => Some(lhs.wrapping_shr(rhs.into()))
         },
         BinaryOpKind::ShiftLeft => match_bitshift! {
             (lhs_value as lhs "<<" rhs_value as rhs) => lhs.checked_shl(rhs.into()).or(Some(0))
```

### test_programs/execution_success/bit_shifts_comptime/src/main.nr
```diff
@@ -21,6 +21,10 @@ fn main(x: u64) {
     assert_eq(a >> 3, -97);
 
     regression_8310();
+
+    //regression 8791
+    assert(-(x as i64) >> 63 == -1);
+    assert(a >> 27 == -1);
 }
 
 fn regression_2250() {
@@ -34,5 +38,5 @@ fn regression_2250() {
 fn regression_8310() {
     let x: i64 = -356710612598522715;
     let b = x >> 64;
-    assert(b == 0);
+    assert(b == -1);
 }
```

### test_programs/execution_success/bit_shifts_runtime/src/main.nr
```diff
@@ -5,9 +5,9 @@ fn main(x: u64, y: u8, z: i16, u: i64) {
     // runtime shifts on runtime values
     assert(x << y == 128);
     assert(x >> y == 32);
-    // regression tests for issue #8176
-    assert(u >> (x as u8) == 0);
-    assert(z >> (x as u8) == 0);
+    // regression tests for issue #8176, superseded by issue #8791
+    assert(u >> (x as u8) == -1);
+    assert(z >> (x as u8) == -1);
 
     // Bit-shift with signed integers
     let mut a: i8 = y as i8;
@@ -22,4 +22,7 @@ fn main(x: u64, y: u8, z: i16, u: i64) {
     assert(x >> (x as u8) == 0);
 
     assert_eq(z >> 3, -97);
+
+    assert(z >> 16 == -1);
+    assert(-z >> x as u8 == 0);
 }
```

### tooling/nargo_cli/tests/snapshots/compile_success_no_bug/comptime_right_shift_no_overflow/execute__tests__expanded.snap
```diff
@@ -3,6 +3,6 @@ source: tooling/nargo_cli/tests/execute.rs
 expression: expanded_code
 ---
 fn main(x: Field) -> pub Field {
-    let y: Field = 0;
+    let y: Field = 1;
     x + y
 }
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_comptime/execute__tests__expanded.snap
```diff
@@ -16,6 +16,8 @@ fn main(x: u64) {
     let a: i16 = -769;
     assert((a >> 3) == -97);
     regression_8310();
+    assert((-(x as i64) >> 63) == -1);
+    assert((a >> 27) == -1);
 }
 
 fn regression_2250() {
@@ -28,5 +30,5 @@ fn regression_2250() {
 fn regression_8310() {
     let x: i64 = -356710612598522715;
     let b: i64 = x >> 64;
-    assert(b == 0);
+    assert(b == -1);
 }
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_comptime/execute__tests__force_brillig_false_inliner_-9223372036854775808.snap
```diff
@@ -18,11 +18,16 @@ expression: artifact
       }
     ],
     "return_type": null,
-    "error_types": {}
+    "error_types": {
+      "2920182694213909827": {
+        "error_kind": "string",
+        "string": "attempt to subtract with overflow"
+      }
+    }
   },
   "bytecode": [
     "func 0",
-    "current witness index : _6",
+    "current witness index : _32",
     "private parameters indices : [_0]",
     "public parameters indices : []",
     "return value indices : []",
@@ -39,20 +44,70 @@ expression: artifact
     "BLACKBOX::RANGE [(_5, 63)] []",
     "EXPR [ (9223372036854775808, _0) (-18446744073709551616, _5) (-1, _6) 0 ]",
     "EXPR [ (1, _6) 0 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(0))], q_c: 36893488147419103232 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 18446744073709551616 })], outputs: [Simple(Witness(7)), Simple(Witness(8))]",
+    "BLACKBOX::RANGE [(_7, 2)] []",
+    "BLACKBOX::RANGE [(_8, 64)] []",
+    "EXPR [ (-1, _0) (-18446744073709551616, _7) (-1, _8) 36893488147419103232 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(0))], q_c: 9223372036854775808 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 18446744073709551616 })], outputs: [Simple(Witness(9)), Simple(Witness(10))]",
+    "BLACKBOX::RANGE [(_9, 1)] []",
+    "BLACKBOX::RANGE [(_10, 64)] []",
+    "EXPR [ (1, _0) (-18446744073709551616, _9) (-1, _10) 9223372036854775808 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(8))], q_c: 9223372036854775808 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 18446744073709551616 })], outputs: [Simple(Witness(11)), Simple(Witness(12))]",
+    "BLACKBOX::RANGE [(_11, 1)] []",
+    "BLACKBOX::RANGE [(_12, 64)] []",
+    "EXPR [ (1, _8) (-18446744073709551616, _11) (-1, _12) 9223372036854775808 ]",
+    "EXPR [ (-1, _9, _11) 0 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(8))], q_c: 0 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 9223372036854775808 })], outputs: [Simple(Witness(13)), Simple(Witness(14))]",
+    "BLACKBOX::RANGE [(_13, 1)] []",
+    "BLACKBOX::RANGE [(_14, 63)] []",
+    "EXPR [ (1, _8) (-9223372036854775808, _13) (-1, _14) 0 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(8))], q_c: 36893488147419103232 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 36893488147419103232 })], outputs: [Simple(Witness(15)), Simple(Witness(16))]",
+    "BLACKBOX::RANGE [(_15, 1)] []",
+    "BLACKBOX::RANGE [(_16, 65)] []",
+    "EXPR [ (1, _8) (-36893488147419103232, _15) (-1, _16) 36893488147419103232 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(2, Witness(15), Witness(13))], linear_combinations: [(1, Witness(8)), (-1, Witness(13)), (-1, Witness(15))], q_c: 1 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 18446744073709551616 })], outputs: [Simple(Witness(17)), Simple(Witness(18))]",
+    "BLACKBOX::RANGE [(_17, 1)] []",
+    "BLACKBOX::RANGE [(_18, 64)] []",
+    "EXPR [ (2, _13, _15) (1, _8) (-1, _13) (-1, _15) (-18446744073709551616, _17) (-1, _18) 1 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(18))], q_c: 0 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 9223372036854775808 })], outputs: [Simple(Witness(19)), Simple(Witness(20))]",
+    "BLACKBOX::RANGE [(_19, 1)] []",
+    "BLACKBOX::RANGE [(_20, 63)] []",
+    "EXPR [ (1, _18) (-9223372036854775808, _19) (-1, _20) 0 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(18), Witness(19))], linear_combinations: [(1, Witness(18)), (18446744073709551616, Witness(19))], q_c: 0 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 9223372036854775808 })], outputs: [Simple(Witness(21)), Simple(Witness(22))]",
+    "BLACKBOX::RANGE [(_21, 1)] []",
+    "BLACKBOX::RANGE [(_22, 63)] []",
+    "EXPR [ (-2, _18, _19) (1, _18) (18446744073709551616, _19) (-9223372036854775808, _21) (-1, _22) 0 ]",
+    "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(21))], q_c: 0 })], outputs: [Simple(Witness(23))]",
+    "EXPR [ (1, _21, _23) (1, _24) -1 ]",
+    "EXPR [ (1, _21, _24) 0 ]",
+    "EXPR [ (2, _19, _21) (-18446744073709551616, _19) (-1, _21) (-1, _25) 18446744073709551616 ]",
+    "EXPR [ (-1, _24) (-1, _26) 1 ]",
+    "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(22))], q_c: 0 })], outputs: [Simple(Witness(27))]",
+    "EXPR [ (1, _22, _27) (1, _28) -1 ]",
+    "EXPR [ (1, _22, _28) 0 ]",
+    "EXPR [ (-2, _19, _22) (18446744073709551616, _19) (1, _22) (-1, _29) 0 ]",
+    "EXPR [ (-1, _28) (-1, _30) 1 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(15), Witness(13)), (1, Witness(25), Witness(26))], linear_combinations: [(1, Witness(13)), (1, Witness(15))], q_c: 36893488147419103231 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 18446744073709551616 })], outputs: [Simple(Witness(31)), Simple(Witness(32))]",
+    "BLACKBOX::RANGE [(_31, 2)] []",
+    "EXPR [ (-2, _13, _15) (1, _25, _26) (1, _13) (1, _15) (-18446744073709551616, _31) (-1, _32) 36893488147419103231 ]",
+    "EXPR [ (1, _32) -18446744073709551615 ]",
     "unconstrained func 0",
-    "[Const { destination: Direct(10), bit_size: Integer(U32), value: 2 }, Const { destination: Direct(11), bit_size: Integer(U32), value: 0 }, CalldataCopy { destination_address: Direct(0), size_address: Direct(10), offset_address: Direct(11) }, BinaryFieldOp { destination: Direct(2), op: IntegerDiv, lhs: Direct(0), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Mul, lhs: Direct(2), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Sub, lhs: Direct(0), rhs: Direct(1) }, Mov { destination: Direct(0), source: Direct(2) }, Stop { return_data: HeapVector { pointer: Direct(11), size: Direct(10) } }]"
+    "[Const { destination: Direct(10), bit_size: Integer(U32), value: 2 }, Const { destination: Direct(11), bit_size: Integer(U32), value: 0 }, CalldataCopy { destination_address: Direct(0), size_address: Direct(10), offset_address: Direct(11) }, BinaryFieldOp { destination: Direct(2), op: IntegerDiv, lhs: Direct(0), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Mul, lhs: Direct(2), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Sub, lhs: Direct(0), rhs: Direct(1) }, Mov { destination: Direct(0), source: Direct(2) }, Stop { return_data: HeapVector { pointer: Direct(11), size: Direct(10) } }]",
+    "unconstrained func 1",
+    "[Const { destination: Direct(21), bit_size: Integer(U32), value: 1 }, Const { destination: Direct(20), bit_size: Integer(U32), value: 0 }, CalldataCopy { destination_address: Direct(0), size_address: Direct(21), offset_address: Direct(20) }, Const { destination: Direct(2), bit_size: Field, value: 0 }, BinaryFieldOp { destination: Direct(3), op: Equals, lhs: Direct(0), rhs: Direct(2) }, JumpIf { condition: Direct(3), location: 8 }, Const { destination: Direct(1), bit_size: Field, value: 1 }, BinaryFieldOp { destination: Direct(0), op: Div, lhs: Direct(1), rhs: Direct(0) }, Stop { return_data: HeapVector { pointer: Direct(20), size: Direct(21) } }]"
   ],
-  "debug_symbols": "pZLPDoIwDMbfpeceYJugvIoxZEAxS5ZB5mZiiO9umeCfgxe8tFu//ZovXSfoqInn2rh+uEB1nKDxxlpzru3Q6mAGx9XpjrBe6+CJuAQfOlOj9uQCVC5ai3DVNqZHl1G7lIP2rGYI5DrO3LA3lubTHd909hsVUi6wkIcXvtvCq2ILX6zmRfEnX4oNvJTlwkul/uS/53fim26N//pxyKHKEUSKMkXF1hF23AChSLFMcQ+VQjhwM4Q8e6b8mRifZ3XV3ujG0rJKfXTtx2aF27gq6+6Nfmipi55mT0ljlw8=",
+  "debug_symbols": "pZTNjoIwFEbfpesuaHsvf68ymRjEakgaIBVMJsZ3n2s/cHQxG9j0CPUcpSW9q5M/zpdD15+Hq6q/7uoYuxC6yyEMbTN1Qy937w+t1svDFL2XW+ptXqyxib6fVN3PIWh1a8KcvnQdmz5xaqLMZlr5/iSU4LkL/vnpof/s7H/VOrfI1lUvnbf4lG/x8/XP23ynX9gNvnPF4juinf6W9WNXLj5vWj92+csv9vnsdvqfz/8tV03bxY83XhlVG61sGl0aSbZOK5YF1CpPY5HGUtWkVSUxrUwGGEB0+VUjviyeIYCBHCiAEqgSbAYYwAKoWFQsKlYqlaAASqBKcBlgAAs4gAAGUHGoOFQcKoQKoUKoECqECqFCqBAqhAqhwqgwKowKo8KoMCqMCqPCqLBUzPPQuDWxa47BL4fSee7btzNq+hnXmfUUG+PQ+tMc/XN305zs9y8=",
   "file_map": {
     "50": {
-      "source": "fn main(x: u64) {\n    let two: u64 = 2;\n    let three: u64 = 3;\n    // shifts on constant values\n    assert(two << 2 == 8);\n    assert((two << 3) / 8 == two);\n    assert((three >> 1) == 1);\n    // shifts on runtime values\n    assert(x << 1 == 128);\n    assert(x >> 2 == 16);\n\n    regression_2250();\n\n    //regression for 3481\n    assert(x << 63 == 0);\n\n    assert_eq((1 as u64) << 32, 0x0100000000);\n\n    //regression for 6201\n    let a: i16 = -769;\n    assert_eq(a >> 3, -97);\n\n    regression_8310();\n}\n\nfn regression_2250() {\n    let a: u1 = 1 >> 1;\n    assert(a == 0);\n\n    let b: u32 = 1 >> 32;\n    assert(b == 0);\n}\n\nfn regression_8310() {\n    let x: i64 = -356710612598522715;\n    let b = x >> 64;\n    assert(b == 0);\n}\n",
+      "source": "fn main(x: u64) {\n    let two: u64 = 2;\n    let three: u64 = 3;\n    // shifts on constant values\n    assert(two << 2 == 8);\n    assert((two << 3) / 8 == two);\n    assert((three >> 1) == 1);\n    // shifts on runtime values\n    assert(x << 1 == 128);\n    assert(x >> 2 == 16);\n\n    regression_2250();\n\n    //regression for 3481\n    assert(x << 63 == 0);\n\n    assert_eq((1 as u64) << 32, 0x0100000000);\n\n    //regression for 6201\n    let a: i16 = -769;\n    assert_eq(a >> 3, -97);\n\n    regression_8310();\n\n    //regression 8791\n    assert(-(x as i64) >> 63 == -1);\n    assert(a >> 27 == -1);\n}\n\nfn regression_2250() {\n    let a: u1 = 1 >> 1;\n    assert(a == 0);\n\n    let b: u32 = 1 >> 32;\n    assert(b == 0);\n}\n\nfn regression_8310() {\n    let x: i64 = -356710612598522715;\n    let b = x >> 64;\n    assert(b == -1);\n}\n",
       "path": ""
     }
   },
   "names": [
     "main"
   ],
   "brillig_names": [
-    "directive_integer_quotient"
+    "directive_integer_quotient",
+    "directive_invert"
   ]
 }
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_comptime/execute__tests__force_brillig_false_inliner_0.snap
```diff
@@ -18,11 +18,16 @@ expression: artifact
       }
     ],
     "return_type": null,
-    "error_types": {}
+    "error_types": {
+      "2920182694213909827": {
+        "error_kind": "string",
+        "string": "attempt to subtract with overflow"
+      }
+    }
   },
   "bytecode": [
     "func 0",
-    "current witness index : _6",
+    "current witness index : _32",
     "private parameters indices : [_0]",
     "public parameters indices : []",
     "return value indices : []",
@@ -39,20 +44,70 @@ expression: artifact
     "BLACKBOX::RANGE [(_5, 63)] []",
     "EXPR [ (9223372036854775808, _0) (-18446744073709551616, _5) (-1, _6) 0 ]",
     "EXPR [ (1, _6) 0 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(0))], q_c: 36893488147419103232 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 18446744073709551616 })], outputs: [Simple(Witness(7)), Simple(Witness(8))]",
+    "BLACKBOX::RANGE [(_7, 2)] []",
+    "BLACKBOX::RANGE [(_8, 64)] []",
+    "EXPR [ (-1, _0) (-18446744073709551616, _7) (-1, _8) 36893488147419103232 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(0))], q_c: 9223372036854775808 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 18446744073709551616 })], outputs: [Simple(Witness(9)), Simple(Witness(10))]",
+    "BLACKBOX::RANGE [(_9, 1)] []",
+    "BLACKBOX::RANGE [(_10, 64)] []",
+    "EXPR [ (1, _0) (-18446744073709551616, _9) (-1, _10) 9223372036854775808 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(8))], q_c: 9223372036854775808 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 18446744073709551616 })], outputs: [Simple(Witness(11)), Simple(Witness(12))]",
+    "BLACKBOX::RANGE [(_11, 1)] []",
+    "BLACKBOX::RANGE [(_12, 64)] []",
+    "EXPR [ (1, _8) (-18446744073709551616, _11) (-1, _12) 9223372036854775808 ]",
+    "EXPR [ (-1, _9, _11) 0 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(8))], q_c: 0 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 9223372036854775808 })], outputs: [Simple(Witness(13)), Simple(Witness(14))]",
+    "BLACKBOX::RANGE [(_13, 1)] []",
+    "BLACKBOX::RANGE [(_14, 63)] []",
+    "EXPR [ (1, _8) (-9223372036854775808, _13) (-1, _14) 0 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(8))], q_c: 36893488147419103232 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 36893488147419103232 })], outputs: [Simple(Witness(15)), Simple(Witness(16))]",
+    "BLACKBOX::RANGE [(_15, 1)] []",
+    "BLACKBOX::RANGE [(_16, 65)] []",
+    "EXPR [ (1, _8) (-36893488147419103232, _15) (-1, _16) 36893488147419103232 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(2, Witness(15), Witness(13))], linear_combinations: [(1, Witness(8)), (-1, Witness(13)), (-1, Witness(15))], q_c: 1 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 18446744073709551616 })], outputs: [Simple(Witness(17)), Simple(Witness(18))]",
+    "BLACKBOX::RANGE [(_17, 1)] []",
+    "BLACKBOX::RANGE [(_18, 64)] []",
+    "EXPR [ (2, _13, _15) (1, _8) (-1, _13) (-1, _15) (-18446744073709551616, _17) (-1, _18) 1 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(18))], q_c: 0 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 9223372036854775808 })], outputs: [Simple(Witness(19)), Simple(Witness(20))]",
+    "BLACKBOX::RANGE [(_19, 1)] []",
+    "BLACKBOX::RANGE [(_20, 63)] []",
+    "EXPR [ (1, _18) (-9223372036854775808, _19) (-1, _20) 0 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(18), Witness(19))], linear_combinations: [(1, Witness(18)), (18446744073709551616, Witness(19))], q_c: 0 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 9223372036854775808 })], outputs: [Simple(Witness(21)), Simple(Witness(22))]",
+    "BLACKBOX::RANGE [(_21, 1)] []",
+    "BLACKBOX::RANGE [(_22, 63)] []",
+    "EXPR [ (-2, _18, _19) (1, _18) (18446744073709551616, _19) (-9223372036854775808, _21) (-1, _22) 0 ]",
+    "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(21))], q_c: 0 })], outputs: [Simple(Witness(23))]",
+    "EXPR [ (1, _21, _23) (1, _24) -1 ]",
+    "EXPR [ (1, _21, _24) 0 ]",
+    "EXPR [ (2, _19, _21) (-18446744073709551616, _19) (-1, _21) (-1, _25) 18446744073709551616 ]",
+    "EXPR [ (-1, _24) (-1, _26) 1 ]",
+    "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(22))], q_c: 0 })], outputs: [Simple(Witness(27))]",
+    "EXPR [ (1, _22, _27) (1, _28) -1 ]",
+    "EXPR [ (1, _22, _28) 0 ]",
+    "EXPR [ (-2, _19, _22) (18446744073709551616, _19) (1, _22) (-1, _29) 0 ]",
+    "EXPR [ (-1, _28) (-1, _30) 1 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(15), Witness(13)), (1, Witness(25), Witness(26))], linear_combinations: [(1, Witness(13)), (1, Witness(15))], q_c: 36893488147419103231 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 18446744073709551616 })], outputs: [Simple(Witness(31)), Simple(Witness(32))]",
+    "BLACKBOX::RANGE [(_31, 2)] []",
+    "EXPR [ (-2, _13, _15) (1, _25, _26) (1, _13) (1, _15) (-18446744073709551616, _31) (-1, _32) 36893488147419103231 ]",
+    "EXPR [ (1, _32) -18446744073709551615 ]",
     "unconstrained func 0",
-    "[Const { destination: Direct(10), bit_size: Integer(U32), value: 2 }, Const { destination: Direct(11), bit_size: Integer(U32), value: 0 }, CalldataCopy { destination_address: Direct(0), size_address: Direct(10), offset_address: Direct(11) }, BinaryFieldOp { destination: Direct(2), op: IntegerDiv, lhs: Direct(0), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Mul, lhs: Direct(2), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Sub, lhs: Direct(0), rhs: Direct(1) }, Mov { destination: Direct(0), source: Direct(2) }, Stop { return_data: HeapVector { pointer: Direct(11), size: Direct(10) } }]"
+    "[Const { destination: Direct(10), bit_size: Integer(U32), value: 2 }, Const { destination: Direct(11), bit_size: Integer(U32), value: 0 }, CalldataCopy { destination_address: Direct(0), size_address: Direct(10), offset_address: Direct(11) }, BinaryFieldOp { destination: Direct(2), op: IntegerDiv, lhs: Direct(0), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Mul, lhs: Direct(2), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Sub, lhs: Direct(0), rhs: Direct(1) }, Mov { destination: Direct(0), source: Direct(2) }, Stop { return_data: HeapVector { pointer: Direct(11), size: Direct(10) } }]",
+    "unconstrained func 1",
+    "[Const { destination: Direct(21), bit_size: Integer(U32), value: 1 }, Const { destination: Direct(20), bit_size: Integer(U32), value: 0 }, CalldataCopy { destination_address: Direct(0), size_address: Direct(21), offset_address: Direct(20) }, Const { destination: Direct(2), bit_size: Field, value: 0 }, BinaryFieldOp { destination: Direct(3), op: Equals, lhs: Direct(0), rhs: Direct(2) }, JumpIf { condition: Direct(3), location: 8 }, Const { destination: Direct(1), bit_size: Field, value: 1 }, BinaryFieldOp { destination: Direct(0), op: Div, lhs: Direct(1), rhs: Direct(0) }, Stop { return_data: HeapVector { pointer: Direct(20), size: Direct(21) } }]"
   ],
-  "debug_symbols": "pZLPDoIwDMbfpeceYJugvIoxZEAxS5ZB5mZiiO9umeCfgxe8tFu//ZovXSfoqInn2rh+uEB1nKDxxlpzru3Q6mAGx9XpjrBe6+CJuAQfOlOj9uQCVC5ai3DVNqZHl1G7lIP2rGYI5DrO3LA3lubTHd909hsVUi6wkIcXvtvCq2ILX6zmRfEnX4oNvJTlwkul/uS/53fim26N//pxyKHKEUSKMkXF1hF23AChSLFMcQ+VQjhwM4Q8e6b8mRifZ3XV3ujG0rJKfXTtx2aF27gq6+6Nfmipi55mT0ljlw8=",
+  "debug_symbols": "pZTNjoIwFEbfpesuaHsvf68ymRjEakgaIBVMJsZ3n2s/cHQxG9j0CPUcpSW9q5M/zpdD15+Hq6q/7uoYuxC6yyEMbTN1Qy937w+t1svDFL2XW+ptXqyxib6fVN3PIWh1a8KcvnQdmz5xaqLMZlr5/iSU4LkL/vnpof/s7H/VOrfI1lUvnbf4lG/x8/XP23ynX9gNvnPF4juinf6W9WNXLj5vWj92+csv9vnsdvqfz/8tV03bxY83XhlVG61sGl0aSbZOK5YF1CpPY5HGUtWkVSUxrUwGGEB0+VUjviyeIYCBHCiAEqgSbAYYwAKoWFQsKlYqlaAASqBKcBlgAAs4gAAGUHGoOFQcKoQKoUKoECqECqFCqBAqhAqhwqgwKowKo8KoMCqMCqPCqLBUzPPQuDWxa47BL4fSee7btzNq+hnXmfUUG+PQ+tMc/XN305zs9y8=",
   "file_map": {
     "50": {
-      "source": "fn main(x: u64) {\n    let two: u64 = 2;\n    let three: u64 = 3;\n    // shifts on constant values\n    assert(two << 2 == 8);\n    assert((two << 3) / 8 == two);\n    assert((three >> 1) == 1);\n    // shifts on runtime values\n    assert(x << 1 == 128);\n    assert(x >> 2 == 16);\n\n    regression_2250();\n\n    //regression for 3481\n    assert(x << 63 == 0);\n\n    assert_eq((1 as u64) << 32, 0x0100000000);\n\n    //regression for 6201\n    let a: i16 = -769;\n    assert_eq(a >> 3, -97);\n\n    regression_8310();\n}\n\nfn regression_2250() {\n    let a: u1 = 1 >> 1;\n    assert(a == 0);\n\n    let b: u32 = 1 >> 32;\n    assert(b == 0);\n}\n\nfn regression_8310() {\n    let x: i64 = -356710612598522715;\n    let b = x >> 64;\n    assert(b == 0);\n}\n",
+      "source": "fn main(x: u64) {\n    let two: u64 = 2;\n    let three: u64 = 3;\n    // shifts on constant values\n    assert(two << 2 == 8);\n    assert((two << 3) / 8 == two);\n    assert((three >> 1) == 1);\n    // shifts on runtime values\n    assert(x << 1 == 128);\n    assert(x >> 2 == 16);\n\n    regression_2250();\n\n    //regression for 3481\n    assert(x << 63 == 0);\n\n    assert_eq((1 as u64) << 32, 0x0100000000);\n\n    //regression for 6201\n    let a: i16 = -769;\n    assert_eq(a >> 3, -97);\n\n    regression_8310();\n\n    //regression 8791\n    assert(-(x as i64) >> 63 == -1);\n    assert(a >> 27 == -1);\n}\n\nfn regression_2250() {\n    let a: u1 = 1 >> 1;\n    assert(a == 0);\n\n    let b: u32 = 1 >> 32;\n    assert(b == 0);\n}\n\nfn regression_8310() {\n    let x: i64 = -356710612598522715;\n    let b = x >> 64;\n    assert(b == -1);\n}\n",
       "path": ""
     }
   },
   "names": [
     "main"
   ],
   "brillig_names": [
-    "directive_integer_quotient"
+    "directive_integer_quotient",
+    "directive_invert"
   ]
 }
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_comptime/execute__tests__force_brillig_false_inliner_9223372036854775807.snap
```diff
@@ -18,11 +18,16 @@ expression: artifact
       }
     ],
     "return_type": null,
-    "error_types": {}
+    "error_types": {
+      "2920182694213909827": {
+        "error_kind": "string",
+        "string": "attempt to subtract with overflow"
+      }
+    }
   },
   "bytecode": [
     "func 0",
-    "current witness index : _6",
+    "current witness index : _32",
     "private parameters indices : [_0]",
     "public parameters indices : []",
     "return value indices : []",
@@ -39,20 +44,70 @@ expression: artifact
     "BLACKBOX::RANGE [(_5, 63)] []",
     "EXPR [ (9223372036854775808, _0) (-18446744073709551616, _5) (-1, _6) 0 ]",
     "EXPR [ (1, _6) 0 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(-1, Witness(0))], q_c: 36893488147419103232 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 18446744073709551616 })], outputs: [Simple(Witness(7)), Simple(Witness(8))]",
+    "BLACKBOX::RANGE [(_7, 2)] []",
+    "BLACKBOX::RANGE [(_8, 64)] []",
+    "EXPR [ (-1, _0) (-18446744073709551616, _7) (-1, _8) 36893488147419103232 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(0))], q_c: 9223372036854775808 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 18446744073709551616 })], outputs: [Simple(Witness(9)), Simple(Witness(10))]",
+    "BLACKBOX::RANGE [(_9, 1)] []",
+    "BLACKBOX::RANGE [(_10, 64)] []",
+    "EXPR [ (1, _0) (-18446744073709551616, _9) (-1, _10) 9223372036854775808 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(8))], q_c: 9223372036854775808 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 18446744073709551616 })], outputs: [Simple(Witness(11)), Simple(Witness(12))]",
+    "BLACKBOX::RANGE [(_11, 1)] []",
+    "BLACKBOX::RANGE [(_12, 64)] []",
+    "EXPR [ (1, _8) (-18446744073709551616, _11) (-1, _12) 9223372036854775808 ]",
+    "EXPR [ (-1, _9, _11) 0 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(8))], q_c: 0 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 9223372036854775808 })], outputs: [Simple(Witness(13)), Simple(Witness(14))]",
+    "BLACKBOX::RANGE [(_13, 1)] []",
+    "BLACKBOX::RANGE [(_14, 63)] []",
+    "EXPR [ (1, _8) (-9223372036854775808, _13) (-1, _14) 0 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(8))], q_c: 36893488147419103232 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 36893488147419103232 })], outputs: [Simple(Witness(15)), Simple(Witness(16))]",
+    "BLACKBOX::RANGE [(_15, 1)] []",
+    "BLACKBOX::RANGE [(_16, 65)] []",
+    "EXPR [ (1, _8) (-36893488147419103232, _15) (-1, _16) 36893488147419103232 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(2, Witness(15), Witness(13))], linear_combinations: [(1, Witness(8)), (-1, Witness(13)), (-1, Witness(15))], q_c: 1 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 18446744073709551616 })], outputs: [Simple(Witness(17)), Simple(Witness(18))]",
+    "BLACKBOX::RANGE [(_17, 1)] []",
+    "BLACKBOX::RANGE [(_18, 64)] []",
+    "EXPR [ (2, _13, _15) (1, _8) (-1, _13) (-1, _15) (-18446744073709551616, _17) (-1, _18) 1 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(18))], q_c: 0 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 9223372036854775808 })], outputs: [Simple(Witness(19)), Simple(Witness(20))]",
+    "BLACKBOX::RANGE [(_19, 1)] []",
+    "BLACKBOX::RANGE [(_20, 63)] []",
+    "EXPR [ (1, _18) (-9223372036854775808, _19) (-1, _20) 0 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(18), Witness(19))], linear_combinations: [(1, Witness(18)), (18446744073709551616, Witness(19))], q_c: 0 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 9223372036854775808 })], outputs: [Simple(Witness(21)), Simple(Witness(22))]",
+    "BLACKBOX::RANGE [(_21, 1)] []",
+    "BLACKBOX::RANGE [(_22, 63)] []",
+    "EXPR [ (-2, _18, _19) (1, _18) (18446744073709551616, _19) (-9223372036854775808, _21) (-1, _22) 0 ]",
+    "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(21))], q_c: 0 })], outputs: [Simple(Witness(23))]",
+    "EXPR [ (1, _21, _23) (1, _24) -1 ]",
+    "EXPR [ (1, _21, _24) 0 ]",
+    "EXPR [ (2, _19, _21) (-18446744073709551616, _19) (-1, _21) (-1, _25) 18446744073709551616 ]",
+    "EXPR [ (-1, _24) (-1, _26) 1 ]",
+    "BRILLIG CALL func 1: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(22))], q_c: 0 })], outputs: [Simple(Witness(27))]",
+    "EXPR [ (1, _22, _27) (1, _28) -1 ]",
+    "EXPR [ (1, _22, _28) 0 ]",
+    "EXPR [ (-2, _19, _22) (18446744073709551616, _19) (1, _22) (-1, _29) 0 ]",
+    "EXPR [ (-1, _28) (-1, _30) 1 ]",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [(-2, Witness(15), Witness(13)), (1, Witness(25), Witness(26))], linear_combinations: [(1, Witness(13)), (1, Witness(15))], q_c: 36893488147419103231 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 18446744073709551616 })], outputs: [Simple(Witness(31)), Simple(Witness(32))]",
+    "BLACKBOX::RANGE [(_31, 2)] []",
+    "EXPR [ (-2, _13, _15) (1, _25, _26) (1, _13) (1, _15) (-18446744073709551616, _31) (-1, _32) 36893488147419103231 ]",
+    "EXPR [ (1, _32) -18446744073709551615 ]",
     "unconstrained func 0",
-    "[Const { destination: Direct(10), bit_size: Integer(U32), value: 2 }, Const { destination: Direct(11), bit_size: Integer(U32), value: 0 }, CalldataCopy { destination_address: Direct(0), size_address: Direct(10), offset_address: Direct(11) }, BinaryFieldOp { destination: Direct(2), op: IntegerDiv, lhs: Direct(0), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Mul, lhs: Direct(2), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Sub, lhs: Direct(0), rhs: Direct(1) }, Mov { destination: Direct(0), source: Direct(2) }, Stop { return_data: HeapVector { pointer: Direct(11), size: Direct(10) } }]"
+    "[Const { destination: Direct(10), bit_size: Integer(U32), value: 2 }, Const { destination: Direct(11), bit_size: Integer(U32), value: 0 }, CalldataCopy { destination_address: Direct(0), size_address: Direct(10), offset_address: Direct(11) }, BinaryFieldOp { destination: Direct(2), op: IntegerDiv, lhs: Direct(0), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Mul, lhs: Direct(2), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Sub, lhs: Direct(0), rhs: Direct(1) }, Mov { destination: Direct(0), source: Direct(2) }, Stop { return_data: HeapVector { pointer: Direct(11), size: Direct(10) } }]",
+    "unconstrained func 1",
+    "[Const { destination: Direct(21), bit_size: Integer(U32), value: 1 }, Const { destination: Direct(20), bit_size: Integer(U32), value: 0 }, CalldataCopy { destination_address: Direct(0), size_address: Direct(21), offset_address: Direct(20) }, Const { destination: Direct(2), bit_size: Field, value: 0 }, BinaryFieldOp { destination: Direct(3), op: Equals, lhs: Direct(0), rhs: Direct(2) }, JumpIf { condition: Direct(3), location: 8 }, Const { destination: Direct(1), bit_size: Field, value: 1 }, BinaryFieldOp { destination: Direct(0), op: Div, lhs: Direct(1), rhs: Direct(0) }, Stop { return_data: HeapVector { pointer: Direct(20), size: Direct(21) } }]"
   ],
-  "debug_symbols": "pZLPDoIwDMbfpeceYJugvIoxZEAxS5ZB5mZiiO9umeCfgxe8tFu//ZovXSfoqInn2rh+uEB1nKDxxlpzru3Q6mAGx9XpjrBe6+CJuAQfOlOj9uQCVC5ai3DVNqZHl1G7lIP2rGYI5DrO3LA3lubTHd909hsVUi6wkIcXvtvCq2ILX6zmRfEnX4oNvJTlwkul/uS/53fim26N//pxyKHKEUSKMkXF1hF23AChSLFMcQ+VQjhwM4Q8e6b8mRifZ3XV3ujG0rJKfXTtx2aF27gq6+6Nfmipi55mT0ljlw8=",
+  "debug_symbols": "pZTNjoIwFEbfpesuaHsvf68ymRjEakgaIBVMJsZ3n2s/cHQxG9j0CPUcpSW9q5M/zpdD15+Hq6q/7uoYuxC6yyEMbTN1Qy937w+t1svDFL2XW+ptXqyxib6fVN3PIWh1a8KcvnQdmz5xaqLMZlr5/iSU4LkL/vnpof/s7H/VOrfI1lUvnbf4lG/x8/XP23ynX9gNvnPF4juinf6W9WNXLj5vWj92+csv9vnsdvqfz/8tV03bxY83XhlVG61sGl0aSbZOK5YF1CpPY5HGUtWkVSUxrUwGGEB0+VUjviyeIYCBHCiAEqgSbAYYwAKoWFQsKlYqlaAASqBKcBlgAAs4gAAGUHGoOFQcKoQKoUKoECqECqFCqBAqhAqhwqgwKowKo8KoMCqMCqPCqLBUzPPQuDWxa47BL4fSee7btzNq+hnXmfUUG+PQ+tMc/XN305zs9y8=",
   "file_map": {
     "50": {
-      "source": "fn main(x: u64) {\n    let two: u64 = 2;\n    let three: u64 = 3;\n    // shifts on constant values\n    assert(two << 2 == 8);\n    assert((two << 3) / 8 == two);\n    assert((three >> 1) == 1);\n    // shifts on runtime values\n    assert(x << 1 == 128);\n    assert(x >> 2 == 16);\n\n    regression_2250();\n\n    //regression for 3481\n    assert(x << 63 == 0);\n\n    assert_eq((1 as u64) << 32, 0x0100000000);\n\n    //regression for 6201\n    let a: i16 = -769;\n    assert_eq(a >> 3, -97);\n\n    regression_8310();\n}\n\nfn regression_2250() {\n    let a: u1 = 1 >> 1;\n    assert(a == 0);\n\n    let b: u32 = 1 >> 32;\n    assert(b == 0);\n}\n\nfn regression_8310() {\n    let x: i64 = -356710612598522715;\n    let b = x >> 64;\n    assert(b == 0);\n}\n",
+      "source": "fn main(x: u64) {\n    let two: u64 = 2;\n    let three: u64 = 3;\n    // shifts on constant values\n    assert(two << 2 == 8);\n    assert((two << 3) / 8 == two);\n    assert((three >> 1) == 1);\n    // shifts on runtime values\n    assert(x << 1 == 128);\n    assert(x >> 2 == 16);\n\n    regression_2250();\n\n    //regression for 3481\n    assert(x << 63 == 0);\n\n    assert_eq((1 as u64) << 32, 0x0100000000);\n\n    //regression for 6201\n    let a: i16 = -769;\n    assert_eq(a >> 3, -97);\n\n    regression_8310();\n\n    //regression 8791\n    assert(-(x as i64) >> 63 == -1);\n    assert(a >> 27 == -1);\n}\n\nfn regression_2250() {\n    let a: u1 = 1 >> 1;\n    assert(a == 0);\n\n    let b: u32 = 1 >> 32;\n    assert(b == 0);\n}\n\nfn regression_8310() {\n    let x: i64 = -356710612598522715;\n    let b = x >> 64;\n    assert(b == -1);\n}\n",
       "path": ""
     }
   },
   "names": [
     "main"
   ],
   "brillig_names": [
-    "directive_integer_quotient"
+    "directive_integer_quotient",
+    "directive_invert"
   ]
 }
```
