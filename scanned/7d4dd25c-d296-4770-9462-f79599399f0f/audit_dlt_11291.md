# [?] fix: left bit shift u128 would overflow Field (#9723)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-09-08
Source: https://github.com/noir-lang/noir/commit/216737dd6dd0cb4e0f4c2c4a0c1c872e30dbb0fe
Type: security-commit

## Details
fix: left bit shift u128 would overflow Field (#9723)

## Patch
### compiler/noirc_evaluator/src/ssa/opt/remove_bit_shifts.rs
```diff
@@ -118,6 +118,8 @@ impl Function {
             let old_result = *context.dfg.instruction_results(instruction_id).first().unwrap();
 
             let mut bitshift_context = Context { context };
+            bitshift_context.enforce_bitshift_rhs_lt_bit_size(rhs);
+
             let new_result = if operator == BinaryOp::Shl {
                 bitshift_context.insert_wrapping_shift_left(lhs, rhs)
             } else {
@@ -154,8 +156,6 @@ impl Context<'_, '_, '_> {
             },
         );
 
-        let pow = self.two_pow(rhs);
-
         // We cap the maximum number of bits here to ensure that we don't try and truncate using a
         // `max_bit_size` greater than what's allowable by the underlying `FieldElement` as this is meaningless.
         //
@@ -166,15 +166,47 @@ impl Context<'_, '_, '_> {
             FieldElement::max_num_bits(),
         );
         if max_bit <= typ.bit_size() {
+            // If the result is guaranteed to fit in the target type we can simply multiply
+            let pow = self.two_pow(rhs);
             let pow = self.insert_cast(pow, typ);
             // Unchecked mul as it can't overflow
             self.insert_binary(lhs, BinaryOp::Mul { unchecked: true }, pow)
-        } else {
+        } else if max_bit < FieldElement::max_num_bits() {
+            // If the result fits in a FieldElement we can multiply in Field, then truncate
+            let pow = self.two_pow(rhs);
             let lhs_field = self.insert_cast(lhs, NumericType::NativeField);
             // Unchecked mul as this is a wrapping operation that we later truncate
             let result = self.insert_binary(lhs_field, BinaryOp::Mul { unchecked: true }, pow);
             let result = self.insert_truncate(result, typ.bit_size(), max_bit);
             self.insert_cast(result, typ)
+        } else {
+            // Otherwise, the result might not bit in a FieldElement.
+            // For this, if we have to do `lhs << rhs` we can first shift by half of `rhs`, truncate,
+            // then shift by `rhs - half_of_rhs` and truncate again.
+            assert!(typ.bit_size() <= 128);
+
+            let two = self.numeric_constant(FieldElement::from(2_u32), typ);
+
+            // rhs_divided_by_two = rhs / 2
+            let rhs_divided_by_two = self.insert_binary(rhs, BinaryOp::Div, two);
+
+            // rhs_remainder = rhs - rhs_remainder
+            let rhs_remainder =
+                self.insert_binary(rhs, BinaryOp::Sub { unchecked: true }, rhs_divided_by_two);
+
+            // pow1 = 2^rhs_divided_by_two
+            // pow2 = r^rhs_remainder
+            let pow1 = self.two_pow(rhs_divided_by_two);
+            let pow2 = self.two_pow(rhs_remainder);
+
+            // result = lhs * pow1 * pow2 = lhs * 2^rhs_divided_by_two * 2^rhs_remainder
+            //        = lhs * 2^(rhs_divided_by_two + rhs_remainder) = lhs * 2^rhs
+            let lhs_field = self.insert_cast(lhs, NumericType::NativeField);
+            let result = self.insert_binary(lhs_field, BinaryOp::Mul { unchecked: true }, pow1);
+            let result = self.insert_truncate(result, typ.bit_size(), max_bit);
+            let result = self.insert_binary(result, BinaryOp::Mul { unchecked: true }, pow2);
+            let result = self.insert_truncate(result, typ.bit_size(), max_bit);
+            self.insert_cast(result, typ)
         }
     }
 
@@ -242,7 +274,7 @@ impl Context<'_, '_, '_> {
     /// }
     fn two_pow(&mut self, exponent: ValueId) -> ValueId {
         // Require that exponent < bit_size, ensuring that `pow` returns a value consistent with `lhs`'s type.
-        let max_bit_size = self.enforce_bitshift_rhs_lt_bit_size(exponent);
+        let max_bit_size = self.context.dfg.type_of_value(exponent).bit_size();
 
         if let Some(exponent_const) = self.context.dfg.get_numeric_constant(exponent) {
             let exponent_const_as_u32 = exponent_const.try_to_u32();
@@ -310,30 +342,20 @@ impl Context<'_, '_, '_> {
 
     /// Insert constraints ensuring that the right-hand side of a bit-shift operation
     /// is less than the bit size of the left-hand side.
-    /// Returns the maximum bit size allowed for `rhs`.
-    fn enforce_bitshift_rhs_lt_bit_size(&mut self, rhs: ValueId) -> u32 {
+    fn enforce_bitshift_rhs_lt_bit_size(&mut self, rhs: ValueId) {
         let one = self.numeric_constant(FieldElement::one(), NumericType::bool());
         let rhs_type = self.context.dfg.type_of_value(rhs);
 
         let assert_message = Some("attempt to bit-shift with overflow".to_owned());
 
-        let bit_size = match rhs_type {
-            Type::Numeric(NumericType::Unsigned { bit_size }) => bit_size,
-            Type::Numeric(NumericType::Signed { bit_size }) => {
-                assert!(bit_size > 1, "ICE - i1 is not a valid type");
-                bit_size
-            }
-            _ => unreachable!("check_shift_overflow called with non-numeric type"),
-        };
+        let bit_size = rhs_type.bit_size();
         let bit_size_field = FieldElement::from(bit_size);
 
         let unsigned_typ = NumericType::unsigned(bit_size);
         let max = self.numeric_constant(bit_size_field, unsigned_typ);
         let rhs = self.insert_cast(rhs, unsigned_typ);
         let overflow = self.insert_binary(rhs, BinaryOp::Lt, max);
         self.insert_constrain(overflow, one, assert_message.map(Into::into));
-
-        bit_size
     }
 
     pub(crate) fn field_constant(&mut self, constant: FieldElement) -> ValueId {
@@ -948,4 +970,29 @@ mod tests {
         }
         "#);
     }
+
+    #[test]
+    fn left_bit_shift_u128_overflow_field() {
+        let src = "
+        acir(inline) fn main f0 {
+          b0(v0: u128):
+            v2 = shl v0, u128 127
+            return v2
+        }
+        ";
+        let ssa = Ssa::from_str(src).unwrap();
+        let ssa = ssa.remove_bit_shifts();
+        assert_ssa_snapshot!(ssa, @r"
+        acir(inline) fn main f0 {
+          b0(v0: u128):
+            v1 = cast v0 as Field
+            v3 = mul v1, Field 9223372036854775808
+            v4 = truncate v3 to 128 bits, max_bit_size: 254
+            v6 = mul v4, Field 18446744073709551616
+            v7 = truncate v6 to 128 bits, max_bit_size: 254
+            v8 = cast v7 as u128
+            return v8
+        }
+        ");
+    }
 }
```

### test_programs/execution_success/bit_shifts_u128/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "bit_shifts_u128"
+type = "bin"
+authors = [""]
+
+[dependencies]
```

### test_programs/execution_success/bit_shifts_u128/Prover.toml
```diff
@@ -0,0 +1 @@
+x = "340282366920938463463374607431768211455"
```

### test_programs/execution_success/bit_shifts_u128/src/main.nr
```diff
@@ -0,0 +1,23 @@
+fn main(x: u128) {
+    let const: u128 = 340282366920938463463374607431768211455;
+    for y in 0..127 {
+        let dynamic = x << y;
+        let static = const << y;
+        assert_eq(dynamic, static, f"shift: {y}, static: {static}, dynamic: {dynamic}");
+
+        let dynamic = x >> y;
+        let static = const >> y;
+        assert_eq(dynamic, static, f"shift: {y}, static: {static}, dynamic: {dynamic}");
+    }
+
+    comptime {
+        assert_eq(
+            340282366920938463463374607431768211455_u128 << 126,
+            255211775190703847597530955573826158592,
+        );
+        assert_eq(
+            340282366920938463463374607431768211455_u128 << 127,
+            170141183460469231731687303715884105728,
+        );
+    }
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_u128/execute__tests__expanded.snap
```diff
@@ -0,0 +1,16 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: expanded_code
+---
+fn main(x: u128) {
+    let const: u128 = 340282366920938463463374607431768211455_u128;
+    for y in 0_u128..127_u128 {
+        let dynamic: u128 = x << y;
+        let static: u128 = const << y;
+        assert(dynamic == static, f"shift: {y}, static: {static}, dynamic: {dynamic}");
+        let dynamic: u128 = x >> y;
+        let static: u128 = const >> y;
+        assert(dynamic == static, f"shift: {y}, static: {static}, dynamic: {dynamic}");
+    }
+    ()
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_u128/execute__tests__force_brillig_false_inliner_-9223372036854775808.snap
```diff
@@ -0,0 +1,59 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: artifact
+---
+{
+  "noir_version": "[noir_version]",
+  "hash": "[hash]",
+  "abi": {
+    "parameters": [
+      {
+        "name": "x",
+        "type": {
+          "kind": "integer",
+          "sign": "unsigned",
+          "width": 128
+        },
+        "visibility": "private"
+      }
+    ],
+    "return_type": null,
+    "error_types": {
+      "9578317322825858581": {
+        "error_kind": "fmtstring",
+        "length": 48,
+        "item_types": [
+          {
+            "kind": "integer",
+            "sign": "unsigned",
+            "width": 128
+          },
+          {
+            "kind": "integer",
+            "sign": "unsigned",
+            "width": 128
+          },
+          {
+            "kind": "integer",
+            "sign": "unsigned",
+            "width": 128
+          }
+        ]
+      }
+    }
+  },
+  "bytecode": [
+    "func 0",
+    "current witness index : _0",
+    "private parameters indices : [_0]",
+    "public parameters indices : []",
+    "return value indices : []",
+    "EXPR [ (1, _0) -340282366920938463463374607431768211455 ]"
+  ],
+  "debug_symbols": "[debug_symbols]",
+  "file_map": "[file_map]",
+  "names": [
+    "main"
+  ],
+  "brillig_names": []
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_u128/execute__tests__force_brillig_false_inliner_0.snap
```diff
@@ -0,0 +1,59 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: artifact
+---
+{
+  "noir_version": "[noir_version]",
+  "hash": "[hash]",
+  "abi": {
+    "parameters": [
+      {
+        "name": "x",
+        "type": {
+          "kind": "integer",
+          "sign": "unsigned",
+          "width": 128
+        },
+        "visibility": "private"
+      }
+    ],
+    "return_type": null,
+    "error_types": {
+      "9578317322825858581": {
+        "error_kind": "fmtstring",
+        "length": 48,
+        "item_types": [
+          {
+            "kind": "integer",
+            "sign": "unsigned",
+            "width": 128
+          },
+          {
+            "kind": "integer",
+            "sign": "unsigned",
+            "width": 128
+          },
+          {
+            "kind": "integer",
+            "sign": "unsigned",
+            "width": 128
+          }
+        ]
+      }
+    }
+  },
+  "bytecode": [
+    "func 0",
+    "current witness index : _0",
+    "private parameters indices : [_0]",
+    "public parameters indices : []",
+    "return value indices : []",
+    "EXPR [ (1, _0) -340282366920938463463374607431768211455 ]"
+  ],
+  "debug_symbols": "[debug_symbols]",
+  "file_map": "[file_map]",
+  "names": [
+    "main"
+  ],
+  "brillig_names": []
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_u128/execute__tests__force_brillig_false_inliner_9223372036854775807.snap
```diff
@@ -0,0 +1,59 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: artifact
+---
+{
+  "noir_version": "[noir_version]",
+  "hash": "[hash]",
+  "abi": {
+    "parameters": [
+      {
+        "name": "x",
+        "type": {
+          "kind": "integer",
+          "sign": "unsigned",
+          "width": 128
+        },
+        "visibility": "private"
+      }
+    ],
+    "return_type": null,
+    "error_types": {
+      "9578317322825858581": {
+        "error_kind": "fmtstring",
+        "length": 48,
+        "item_types": [
+          {
+            "kind": "integer",
+            "sign": "unsigned",
+            "width": 128
+          },
+          {
+            "kind": "integer",
+            "sign": "unsigned",
+            "width": 128
+          },
+          {
+            "kind": "integer",
+            "sign": "unsigned",
+            "width": 128
+          }
+        ]
+      }
+    }
+  },
+  "bytecode": [
+    "func 0",
+    "current witness index : _0",
+    "private parameters indices : [_0]",
+    "public parameters indices : []",
+    "return value indices : []",
+    "EXPR [ (1, _0) -340282366920938463463374607431768211455 ]"
+  ],
+  "debug_symbols": "[debug_symbols]",
+  "file_map": "[file_map]",
+  "names": [
+    "main"
+  ],
+  "brillig_names": []
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_u128/execute__tests__force_brillig_true_inliner_-9223372036854775808.snap
```diff
@@ -0,0 +1,67 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: artifact
+---
+{
+  "noir_version": "[noir_version]",
+  "hash": "[hash]",
+  "abi": {
+    "parameters": [
+      {
+        "name": "x",
+        "type": {
+          "kind": "integer",
+          "sign": "unsigned",
+          "width": 128
+        },
+        "visibility": "private"
+      }
+    ],
+    "return_type": null,
+    "error_types": {
+      "9578317322825858581": {
+        "error_kind": "fmtstring",
+        "length": 48,
+        "item_types": [
+          {
+            "kind": "integer",
+            "sign": "unsigned",
+            "width": 128
+          },
+          {
+            "kind": "integer",
+            "sign": "unsigned",
+            "width": 128
+          },
+          {
+            "kind": "integer",
+            "sign": "unsigned",
+            "width": 128
+          }
+        ]
+      },
+      "17843811134343075018": {
+        "error_kind": "string",
+        "string": "Stack too deep"
+      }
+    }
+  },
+  "bytecode": [
+    "func 0",
+    "current witness index : _0",
+    "private parameters indices : [_0]",
+    "public parameters indices : []",
+    "return value indices : []",
+    "BRILLIG CALL func 0: inputs: [EXPR [ (1, _0) 0 ]], outputs: []",
+    "unconstrained func 0",
+    "[Const { destination: Direct(2), bit_size: Integer(U32), value: 1 }, Const { destination: Direct(1), bit_size: Integer(U32), value: 32837 }, Const { destination: Direct(0), bit_size: Integer(U32), value: 3 }, Const { destination: Relative(2), bit_size: Integer(U32), value: 1 }, Const { destination: Relative(3), bit_size: Integer(U32), value: 0 }, CalldataCopy { destination_address: Direct(32836), size_address: Relative(2), offset_address: Relative(3) }, Cast { destination: Direct(32836), source: Direct(32836), bit_size: Integer(U128) }, Mov { destination: Relative(1), source: Direct(32836) }, Call { location: 13 }, Call { location: 14 }, Const { destination: Relative(1), bit_size: Integer(U32), value: 32837 }, Const { destination: Relative(2), bit_size: Integer(U32), value: 0 }, Stop { return_data: HeapVector { pointer: Relative(1), size: Relative(2) } }, Return, Call { location: 202 }, Const { destination: Relative(3), bit_size: Integer(U8), value: 115 }, Const { destination: Relative(4), bit_size: Integer(U8), value: 104 }, Const { destination: Relative(5), bit_size: Integer(U8), value: 105 }, Const { destination: Relative(6), bit_size: Integer(U8), value: 102 }, Const { destination: Relative(7), bit_size: Integer(U8), value: 116 }, Const { destination: Relative(8), bit_size: Integer(U8), value: 58 }, Const { destination: Relative(9), bit_size: Integer(U8), value: 32 }, Const { destination: Relative(10), bit_size: Integer(U8), value: 123 }, Const { destination: Relative(11), bit_size: Integer(U8), value: 121 }, Const { destination: Relative(12), bit_size: Integer(U8), value: 125 }, Const { destination: Relative(13), bit_size: Integer(U8), value: 44 }, Const { destination: Relative(14), bit_size: Integer(U8), value: 97 }, Const { destination: Relative(15), bit_size: Integer(U8), value: 99 }, Const { destination: Relative(16), bit_size: Integer(U8), value: 100 }, Const { destination: Relative(17), bit_size: Integer(U8), value: 110 }, Const { destination: Relative(18), bit_size: Integer(U8), value: 109 }, Mov { destination: Relative(19), source: Direct(1) }, Const { destination: Relative(20), bit_size: Integer(U32), value: 49 }, BinaryIntOp { destination: Direct(1), op: Add, bit_size: U32, lhs: Direct(1), rhs: Relative(20) }, IndirectConst { destination_pointer: Relative(19), bit_size: Integer(U32), value: 1 }, BinaryIntOp { destination: Relative(20), op: Add, bit_size: U32, lhs: Relative(19), rhs: Direct(2) }, Mov { destination: Relative(21), source: Relative(20) }, Store { destination_pointer: Relative(21), source: Relative(3) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(4) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(5) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(6) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(7) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(8) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(9) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(10) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(11) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(12) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(13) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(9) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(3) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(7) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(14) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(7) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(5) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(15) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(8) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(9) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(10) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(3) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(7) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(14) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(7) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(5) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(15) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(12) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(13) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(9) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(16) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(11) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(17) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(14) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(18) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(5) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(15) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(8) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(9) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(10) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(16) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(11) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(17) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(14) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(18) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(5) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(15) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(12) }, Const { destination: Relative(3), bit_size: Integer(U128), value: 0 }, Const { destination: Relative(4), bit_size: Integer(U128), value: 127 }, Const { destination: Relative(5), bit_size: Integer(U128), value: 340282366920938463463374607431768211455 }, Const { destination: Relative(6), bit_size: Field, value: 3 }, Const { destination: Relative(7), bit_size: Integer(U128), value: 1 }, Mov { destination: Relative(2), source: Relative(3) }, Jump { location: 139 }, BinaryIntOp { destination: Relative(3), op: LessThan, bit_size: U128, lhs: Relative(2), rhs: Relative(4) }, JumpIf { condition: Relative(3), location: 143 }, Jump { location: 142 }, Return, BinaryIntOp { destination: Relative(3), op: Shl, bit_size: U128, lhs: Relative(1), rhs: Relative(2) }, BinaryIntOp { destination: Relative(8), op: Shl, bit_size: U128, lhs: Relative(5), rhs: Relative(2) }, BinaryIntOp { destination: Relative(9), op: Equals, bit_size: U128, lhs: Relative(3), rhs: Relative(8) }, JumpIf { condition: Relative(9), location: 171 }, Const { destination: Relative(10), bit_size: Integer(U32), value: 53 }, Mov { destination: Relative(11), source: Direct(1) }, Const { destination: Relative(12), bit_size: Integer(U32), value: 53 }, BinaryIntOp { destination: Direct(1), op: Add, bit_size: U32, lhs: Direct(1), rhs: Relative(12) }, Mov { destination: Relative(12), source: Relative(11) }, IndirectConst { destination_pointer: Relative(12), bit_size: Integer(U64), value: 9578317322825858581 }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, BinaryIntOp { destination: Relative(13), op: Add, bit_size: U32, lhs: Relative(19), rhs: Direct(2) }, Const { destination: Relative(14), bit_size: Integer(U32), value: 48 }, Mov { destination: Direct(32771), source: Relative(13) }, Mov { destination: Direct(32772), source: Relative(12) }, Mov { destination: Direct(32773), source: Relative(14) }, Call { location: 208 }, Const { destination: Relative(13), bit_size: Integer(U32), value: 48 }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Relative(13) }, Store { destination_pointer: Relative(12), source: Relative(6) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Store { destination_pointer: Relative(12), source: Relative(2) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Store { destination_pointer: Relative(12), source: Relative(8) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Store { destination_pointer: Relative(12), source: Relative(3) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Trap { revert_data: HeapVector { pointer: Relative(11), size: Relative(10) } }, BinaryIntOp { destination: Relative(3), op: Shr, bit_size: U128, lhs: Relative(1), rhs: Relative(2) }, BinaryIntOp { destination: Relative(8), op: Shr, bit_size: U128, lhs: Relative(5), rhs: Relative(2) }, BinaryIntOp { destination: Relative(9), op: Equals, bit_size: U128, lhs: Relative(3), rhs: Relative(8) }, JumpIf { condition: Relative(9), location: 199 }, Const { destination: Relative(10), bit_size: Integer(U32), value: 53 }, Mov { destination: Relative(11), source: Direct(1) }, Const { destination: Relative(12), bit_size: Integer(U32), value: 53 }, BinaryIntOp { destination: Direct(1), op: Add, bit_size: U32, lhs: Direct(1), rhs: Relative(12) }, Mov { destination: Relative(12), source: Relative(11) }, IndirectConst { destination_pointer: Relative(12), bit_size: Integer(U64), value: 9578317322825858581 }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, BinaryIntOp { destination: Relative(13), op: Add, bit_size: U32, lhs: Relative(19), rhs: Direct(2) }, Const { destination: Relative(14), bit_size: Integer(U32), value: 48 }, Mov { destination: Direct(32771), source: Relative(13) }, Mov { destination: Direct(32772), source: Relative(12) }, Mov { destination: Direct(32773), source: Relative(14) }, Call { location: 208 }, Const { destination: Relative(13), bit_size: Integer(U32), value: 48 }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Relative(13) }, Store { destination_pointer: Relative(12), source: Relative(6) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Store { destination_pointer: Relative(12), source: Relative(2) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Store { destination_pointer: Relative(12), source: Relative(8) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Store { destination_pointer: Relative(12), source: Relative(3) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Trap { revert_data: HeapVector { pointer: Relative(11), size: Relative(10) } }, BinaryIntOp { destination: Relative(3), op: Add, bit_size: U128, lhs: Relative(2), rhs: Relative(7) }, Mov { destination: Relative(2), source: Relative(3) }, Jump { location: 139 }, Const { destination: Direct(32772), bit_size: Integer(U32), value: 30720 }, BinaryIntOp { destination: Direct(32771), op: LessThan, bit_size: U32, lhs: Direct(0), rhs: Direct(32772) }, JumpIf { condition: Direct(32771), location: 207 }, IndirectConst { destination_pointer: Direct(1), bit_size: Integer(U64), value: 17843811134343075018 }, Trap { revert_data: HeapVector { pointer: Direct(1), size: Direct(2) } }, Return, BinaryIntOp { destination: Direct(32775), op: Add, bit_size: U32, lhs: Direct(32771), rhs: Direct(32773) }, Mov { destination: Direct(32776), source: Direct(32771) }, Mov { destination: Direct(32777), source: Direct(32772) }, BinaryIntOp { destination: Direct(32778), op: Equals, bit_size: U32, lhs: Direct(32776), rhs: Direct(32775) }, JumpIf { condition: Direct(32778), location: 218 }, Load { destination: Direct(32774), source_pointer: Direct(32776) }, Store { destination_pointer: Direct(32777), source: Direct(32774) }, BinaryIntOp { destination: Direct(32776), op: Add, bit_size: U32, lhs: Direct(32776), rhs: Direct(2) }, BinaryIntOp { destination: Direct(32777), op: Add, bit_size: U32, lhs: Direct(32777), rhs: Direct(2) }, Jump { location: 211 }, Return]"
+  ],
+  "debug_symbols": "[debug_symbols]",
+  "file_map": "[file_map]",
+  "names": [
+    "main"
+  ],
+  "brillig_names": [
+    "main"
+  ]
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_u128/execute__tests__force_brillig_true_inliner_0.snap
```diff
@@ -0,0 +1,67 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: artifact
+---
+{
+  "noir_version": "[noir_version]",
+  "hash": "[hash]",
+  "abi": {
+    "parameters": [
+      {
+        "name": "x",
+        "type": {
+          "kind": "integer",
+          "sign": "unsigned",
+          "width": 128
+        },
+        "visibility": "private"
+      }
+    ],
+    "return_type": null,
+    "error_types": {
+      "9578317322825858581": {
+        "error_kind": "fmtstring",
+        "length": 48,
+        "item_types": [
+          {
+            "kind": "integer",
+            "sign": "unsigned",
+            "width": 128
+          },
+          {
+            "kind": "integer",
+            "sign": "unsigned",
+            "width": 128
+          },
+          {
+            "kind": "integer",
+            "sign": "unsigned",
+            "width": 128
+          }
+        ]
+      },
+      "17843811134343075018": {
+        "error_kind": "string",
+        "string": "Stack too deep"
+      }
+    }
+  },
+  "bytecode": [
+    "func 0",
+    "current witness index : _0",
+    "private parameters indices : [_0]",
+    "public parameters indices : []",
+    "return value indices : []",
+    "BRILLIG CALL func 0: inputs: [EXPR [ (1, _0) 0 ]], outputs: []",
+    "unconstrained func 0",
+    "[Const { destination: Direct(2), bit_size: Integer(U32), value: 1 }, Const { destination: Direct(1), bit_size: Integer(U32), value: 32837 }, Const { destination: Direct(0), bit_size: Integer(U32), value: 3 }, Const { destination: Relative(2), bit_size: Integer(U32), value: 1 }, Const { destination: Relative(3), bit_size: Integer(U32), value: 0 }, CalldataCopy { destination_address: Direct(32836), size_address: Relative(2), offset_address: Relative(3) }, Cast { destination: Direct(32836), source: Direct(32836), bit_size: Integer(U128) }, Mov { destination: Relative(1), source: Direct(32836) }, Call { location: 13 }, Call { location: 14 }, Const { destination: Relative(1), bit_size: Integer(U32), value: 32837 }, Const { destination: Relative(2), bit_size: Integer(U32), value: 0 }, Stop { return_data: HeapVector { pointer: Relative(1), size: Relative(2) } }, Return, Call { location: 202 }, Const { destination: Relative(3), bit_size: Integer(U8), value: 115 }, Const { destination: Relative(4), bit_size: Integer(U8), value: 104 }, Const { destination: Relative(5), bit_size: Integer(U8), value: 105 }, Const { destination: Relative(6), bit_size: Integer(U8), value: 102 }, Const { destination: Relative(7), bit_size: Integer(U8), value: 116 }, Const { destination: Relative(8), bit_size: Integer(U8), value: 58 }, Const { destination: Relative(9), bit_size: Integer(U8), value: 32 }, Const { destination: Relative(10), bit_size: Integer(U8), value: 123 }, Const { destination: Relative(11), bit_size: Integer(U8), value: 121 }, Const { destination: Relative(12), bit_size: Integer(U8), value: 125 }, Const { destination: Relative(13), bit_size: Integer(U8), value: 44 }, Const { destination: Relative(14), bit_size: Integer(U8), value: 97 }, Const { destination: Relative(15), bit_size: Integer(U8), value: 99 }, Const { destination: Relative(16), bit_size: Integer(U8), value: 100 }, Const { destination: Relative(17), bit_size: Integer(U8), value: 110 }, Const { destination: Relative(18), bit_size: Integer(U8), value: 109 }, Mov { destination: Relative(19), source: Direct(1) }, Const { destination: Relative(20), bit_size: Integer(U32), value: 49 }, BinaryIntOp { destination: Direct(1), op: Add, bit_size: U32, lhs: Direct(1), rhs: Relative(20) }, IndirectConst { destination_pointer: Relative(19), bit_size: Integer(U32), value: 1 }, BinaryIntOp { destination: Relative(20), op: Add, bit_size: U32, lhs: Relative(19), rhs: Direct(2) }, Mov { destination: Relative(21), source: Relative(20) }, Store { destination_pointer: Relative(21), source: Relative(3) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(4) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(5) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(6) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(7) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(8) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(9) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(10) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(11) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(12) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(13) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(9) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(3) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(7) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(14) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(7) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(5) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(15) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(8) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(9) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(10) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(3) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(7) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(14) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(7) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(5) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(15) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(12) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(13) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(9) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(16) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(11) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(17) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(14) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(18) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(5) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(15) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(8) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(9) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(10) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(16) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(11) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(17) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(14) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(18) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(5) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(15) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(12) }, Const { destination: Relative(3), bit_size: Integer(U128), value: 0 }, Const { destination: Relative(4), bit_size: Integer(U128), value: 127 }, Const { destination: Relative(5), bit_size: Integer(U128), value: 340282366920938463463374607431768211455 }, Const { destination: Relative(6), bit_size: Field, value: 3 }, Const { destination: Relative(7), bit_size: Integer(U128), value: 1 }, Mov { destination: Relative(2), source: Relative(3) }, Jump { location: 139 }, BinaryIntOp { destination: Relative(3), op: LessThan, bit_size: U128, lhs: Relative(2), rhs: Relative(4) }, JumpIf { condition: Relative(3), location: 143 }, Jump { location: 142 }, Return, BinaryIntOp { destination: Relative(3), op: Shl, bit_size: U128, lhs: Relative(1), rhs: Relative(2) }, BinaryIntOp { destination: Relative(8), op: Shl, bit_size: U128, lhs: Relative(5), rhs: Relative(2) }, BinaryIntOp { destination: Relative(9), op: Equals, bit_size: U128, lhs: Relative(3), rhs: Relative(8) }, JumpIf { condition: Relative(9), location: 171 }, Const { destination: Relative(10), bit_size: Integer(U32), value: 53 }, Mov { destination: Relative(11), source: Direct(1) }, Const { destination: Relative(12), bit_size: Integer(U32), value: 53 }, BinaryIntOp { destination: Direct(1), op: Add, bit_size: U32, lhs: Direct(1), rhs: Relative(12) }, Mov { destination: Relative(12), source: Relative(11) }, IndirectConst { destination_pointer: Relative(12), bit_size: Integer(U64), value: 9578317322825858581 }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, BinaryIntOp { destination: Relative(13), op: Add, bit_size: U32, lhs: Relative(19), rhs: Direct(2) }, Const { destination: Relative(14), bit_size: Integer(U32), value: 48 }, Mov { destination: Direct(32771), source: Relative(13) }, Mov { destination: Direct(32772), source: Relative(12) }, Mov { destination: Direct(32773), source: Relative(14) }, Call { location: 208 }, Const { destination: Relative(13), bit_size: Integer(U32), value: 48 }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Relative(13) }, Store { destination_pointer: Relative(12), source: Relative(6) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Store { destination_pointer: Relative(12), source: Relative(2) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Store { destination_pointer: Relative(12), source: Relative(8) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Store { destination_pointer: Relative(12), source: Relative(3) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Trap { revert_data: HeapVector { pointer: Relative(11), size: Relative(10) } }, BinaryIntOp { destination: Relative(3), op: Shr, bit_size: U128, lhs: Relative(1), rhs: Relative(2) }, BinaryIntOp { destination: Relative(8), op: Shr, bit_size: U128, lhs: Relative(5), rhs: Relative(2) }, BinaryIntOp { destination: Relative(9), op: Equals, bit_size: U128, lhs: Relative(3), rhs: Relative(8) }, JumpIf { condition: Relative(9), location: 199 }, Const { destination: Relative(10), bit_size: Integer(U32), value: 53 }, Mov { destination: Relative(11), source: Direct(1) }, Const { destination: Relative(12), bit_size: Integer(U32), value: 53 }, BinaryIntOp { destination: Direct(1), op: Add, bit_size: U32, lhs: Direct(1), rhs: Relative(12) }, Mov { destination: Relative(12), source: Relative(11) }, IndirectConst { destination_pointer: Relative(12), bit_size: Integer(U64), value: 9578317322825858581 }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, BinaryIntOp { destination: Relative(13), op: Add, bit_size: U32, lhs: Relative(19), rhs: Direct(2) }, Const { destination: Relative(14), bit_size: Integer(U32), value: 48 }, Mov { destination: Direct(32771), source: Relative(13) }, Mov { destination: Direct(32772), source: Relative(12) }, Mov { destination: Direct(32773), source: Relative(14) }, Call { location: 208 }, Const { destination: Relative(13), bit_size: Integer(U32), value: 48 }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Relative(13) }, Store { destination_pointer: Relative(12), source: Relative(6) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Store { destination_pointer: Relative(12), source: Relative(2) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Store { destination_pointer: Relative(12), source: Relative(8) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Store { destination_pointer: Relative(12), source: Relative(3) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Trap { revert_data: HeapVector { pointer: Relative(11), size: Relative(10) } }, BinaryIntOp { destination: Relative(3), op: Add, bit_size: U128, lhs: Relative(2), rhs: Relative(7) }, Mov { destination: Relative(2), source: Relative(3) }, Jump { location: 139 }, Const { destination: Direct(32772), bit_size: Integer(U32), value: 30720 }, BinaryIntOp { destination: Direct(32771), op: LessThan, bit_size: U32, lhs: Direct(0), rhs: Direct(32772) }, JumpIf { condition: Direct(32771), location: 207 }, IndirectConst { destination_pointer: Direct(1), bit_size: Integer(U64), value: 17843811134343075018 }, Trap { revert_data: HeapVector { pointer: Direct(1), size: Direct(2) } }, Return, BinaryIntOp { destination: Direct(32775), op: Add, bit_size: U32, lhs: Direct(32771), rhs: Direct(32773) }, Mov { destination: Direct(32776), source: Direct(32771) }, Mov { destination: Direct(32777), source: Direct(32772) }, BinaryIntOp { destination: Direct(32778), op: Equals, bit_size: U32, lhs: Direct(32776), rhs: Direct(32775) }, JumpIf { condition: Direct(32778), location: 218 }, Load { destination: Direct(32774), source_pointer: Direct(32776) }, Store { destination_pointer: Direct(32777), source: Direct(32774) }, BinaryIntOp { destination: Direct(32776), op: Add, bit_size: U32, lhs: Direct(32776), rhs: Direct(2) }, BinaryIntOp { destination: Direct(32777), op: Add, bit_size: U32, lhs: Direct(32777), rhs: Direct(2) }, Jump { location: 211 }, Return]"
+  ],
+  "debug_symbols": "[debug_symbols]",
+  "file_map": "[file_map]",
+  "names": [
+    "main"
+  ],
+  "brillig_names": [
+    "main"
+  ]
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_u128/execute__tests__force_brillig_true_inliner_9223372036854775807.snap
```diff
@@ -0,0 +1,67 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: artifact
+---
+{
+  "noir_version": "[noir_version]",
+  "hash": "[hash]",
+  "abi": {
+    "parameters": [
+      {
+        "name": "x",
+        "type": {
+          "kind": "integer",
+          "sign": "unsigned",
+          "width": 128
+        },
+        "visibility": "private"
+      }
+    ],
+    "return_type": null,
+    "error_types": {
+      "9578317322825858581": {
+        "error_kind": "fmtstring",
+        "length": 48,
+        "item_types": [
+          {
+            "kind": "integer",
+            "sign": "unsigned",
+            "width": 128
+          },
+          {
+            "kind": "integer",
+            "sign": "unsigned",
+            "width": 128
+          },
+          {
+            "kind": "integer",
+            "sign": "unsigned",
+            "width": 128
+          }
+        ]
+      },
+      "17843811134343075018": {
+        "error_kind": "string",
+        "string": "Stack too deep"
+      }
+    }
+  },
+  "bytecode": [
+    "func 0",
+    "current witness index : _0",
+    "private parameters indices : [_0]",
+    "public parameters indices : []",
+    "return value indices : []",
+    "BRILLIG CALL func 0: inputs: [EXPR [ (1, _0) 0 ]], outputs: []",
+    "unconstrained func 0",
+    "[Const { destination: Direct(2), bit_size: Integer(U32), value: 1 }, Const { destination: Direct(1), bit_size: Integer(U32), value: 32837 }, Const { destination: Direct(0), bit_size: Integer(U32), value: 3 }, Const { destination: Relative(2), bit_size: Integer(U32), value: 1 }, Const { destination: Relative(3), bit_size: Integer(U32), value: 0 }, CalldataCopy { destination_address: Direct(32836), size_address: Relative(2), offset_address: Relative(3) }, Cast { destination: Direct(32836), source: Direct(32836), bit_size: Integer(U128) }, Mov { destination: Relative(1), source: Direct(32836) }, Call { location: 13 }, Call { location: 14 }, Const { destination: Relative(1), bit_size: Integer(U32), value: 32837 }, Const { destination: Relative(2), bit_size: Integer(U32), value: 0 }, Stop { return_data: HeapVector { pointer: Relative(1), size: Relative(2) } }, Return, Call { location: 202 }, Const { destination: Relative(3), bit_size: Integer(U8), value: 115 }, Const { destination: Relative(4), bit_size: Integer(U8), value: 104 }, Const { destination: Relative(5), bit_size: Integer(U8), value: 105 }, Const { destination: Relative(6), bit_size: Integer(U8), value: 102 }, Const { destination: Relative(7), bit_size: Integer(U8), value: 116 }, Const { destination: Relative(8), bit_size: Integer(U8), value: 58 }, Const { destination: Relative(9), bit_size: Integer(U8), value: 32 }, Const { destination: Relative(10), bit_size: Integer(U8), value: 123 }, Const { destination: Relative(11), bit_size: Integer(U8), value: 121 }, Const { destination: Relative(12), bit_size: Integer(U8), value: 125 }, Const { destination: Relative(13), bit_size: Integer(U8), value: 44 }, Const { destination: Relative(14), bit_size: Integer(U8), value: 97 }, Const { destination: Relative(15), bit_size: Integer(U8), value: 99 }, Const { destination: Relative(16), bit_size: Integer(U8), value: 100 }, Const { destination: Relative(17), bit_size: Integer(U8), value: 110 }, Const { destination: Relative(18), bit_size: Integer(U8), value: 109 }, Mov { destination: Relative(19), source: Direct(1) }, Const { destination: Relative(20), bit_size: Integer(U32), value: 49 }, BinaryIntOp { destination: Direct(1), op: Add, bit_size: U32, lhs: Direct(1), rhs: Relative(20) }, IndirectConst { destination_pointer: Relative(19), bit_size: Integer(U32), value: 1 }, BinaryIntOp { destination: Relative(20), op: Add, bit_size: U32, lhs: Relative(19), rhs: Direct(2) }, Mov { destination: Relative(21), source: Relative(20) }, Store { destination_pointer: Relative(21), source: Relative(3) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(4) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(5) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(6) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(7) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(8) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(9) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(10) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(11) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(12) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(13) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(9) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(3) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(7) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(14) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(7) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(5) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(15) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(8) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(9) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(10) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(3) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(7) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(14) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(7) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(5) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(15) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(12) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(13) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(9) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(16) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(11) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(17) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(14) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(18) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(5) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(15) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(8) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(9) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(10) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(16) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(11) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(17) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(14) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(18) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(5) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(15) }, BinaryIntOp { destination: Relative(21), op: Add, bit_size: U32, lhs: Relative(21), rhs: Direct(2) }, Store { destination_pointer: Relative(21), source: Relative(12) }, Const { destination: Relative(3), bit_size: Integer(U128), value: 0 }, Const { destination: Relative(4), bit_size: Integer(U128), value: 127 }, Const { destination: Relative(5), bit_size: Integer(U128), value: 340282366920938463463374607431768211455 }, Const { destination: Relative(6), bit_size: Field, value: 3 }, Const { destination: Relative(7), bit_size: Integer(U128), value: 1 }, Mov { destination: Relative(2), source: Relative(3) }, Jump { location: 139 }, BinaryIntOp { destination: Relative(3), op: LessThan, bit_size: U128, lhs: Relative(2), rhs: Relative(4) }, JumpIf { condition: Relative(3), location: 143 }, Jump { location: 142 }, Return, BinaryIntOp { destination: Relative(3), op: Shl, bit_size: U128, lhs: Relative(1), rhs: Relative(2) }, BinaryIntOp { destination: Relative(8), op: Shl, bit_size: U128, lhs: Relative(5), rhs: Relative(2) }, BinaryIntOp { destination: Relative(9), op: Equals, bit_size: U128, lhs: Relative(3), rhs: Relative(8) }, JumpIf { condition: Relative(9), location: 171 }, Const { destination: Relative(10), bit_size: Integer(U32), value: 53 }, Mov { destination: Relative(11), source: Direct(1) }, Const { destination: Relative(12), bit_size: Integer(U32), value: 53 }, BinaryIntOp { destination: Direct(1), op: Add, bit_size: U32, lhs: Direct(1), rhs: Relative(12) }, Mov { destination: Relative(12), source: Relative(11) }, IndirectConst { destination_pointer: Relative(12), bit_size: Integer(U64), value: 9578317322825858581 }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, BinaryIntOp { destination: Relative(13), op: Add, bit_size: U32, lhs: Relative(19), rhs: Direct(2) }, Const { destination: Relative(14), bit_size: Integer(U32), value: 48 }, Mov { destination: Direct(32771), source: Relative(13) }, Mov { destination: Direct(32772), source: Relative(12) }, Mov { destination: Direct(32773), source: Relative(14) }, Call { location: 208 }, Const { destination: Relative(13), bit_size: Integer(U32), value: 48 }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Relative(13) }, Store { destination_pointer: Relative(12), source: Relative(6) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Store { destination_pointer: Relative(12), source: Relative(2) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Store { destination_pointer: Relative(12), source: Relative(8) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Store { destination_pointer: Relative(12), source: Relative(3) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Trap { revert_data: HeapVector { pointer: Relative(11), size: Relative(10) } }, BinaryIntOp { destination: Relative(3), op: Shr, bit_size: U128, lhs: Relative(1), rhs: Relative(2) }, BinaryIntOp { destination: Relative(8), op: Shr, bit_size: U128, lhs: Relative(5), rhs: Relative(2) }, BinaryIntOp { destination: Relative(9), op: Equals, bit_size: U128, lhs: Relative(3), rhs: Relative(8) }, JumpIf { condition: Relative(9), location: 199 }, Const { destination: Relative(10), bit_size: Integer(U32), value: 53 }, Mov { destination: Relative(11), source: Direct(1) }, Const { destination: Relative(12), bit_size: Integer(U32), value: 53 }, BinaryIntOp { destination: Direct(1), op: Add, bit_size: U32, lhs: Direct(1), rhs: Relative(12) }, Mov { destination: Relative(12), source: Relative(11) }, IndirectConst { destination_pointer: Relative(12), bit_size: Integer(U64), value: 9578317322825858581 }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, BinaryIntOp { destination: Relative(13), op: Add, bit_size: U32, lhs: Relative(19), rhs: Direct(2) }, Const { destination: Relative(14), bit_size: Integer(U32), value: 48 }, Mov { destination: Direct(32771), source: Relative(13) }, Mov { destination: Direct(32772), source: Relative(12) }, Mov { destination: Direct(32773), source: Relative(14) }, Call { location: 208 }, Const { destination: Relative(13), bit_size: Integer(U32), value: 48 }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Relative(13) }, Store { destination_pointer: Relative(12), source: Relative(6) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Store { destination_pointer: Relative(12), source: Relative(2) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Store { destination_pointer: Relative(12), source: Relative(8) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Store { destination_pointer: Relative(12), source: Relative(3) }, BinaryIntOp { destination: Relative(12), op: Add, bit_size: U32, lhs: Relative(12), rhs: Direct(2) }, Trap { revert_data: HeapVector { pointer: Relative(11), size: Relative(10) } }, BinaryIntOp { destination: Relative(3), op: Add, bit_size: U128, lhs: Relative(2), rhs: Relative(7) }, Mov { destination: Relative(2), source: Relative(3) }, Jump { location: 139 }, Const { destination: Direct(32772), bit_size: Integer(U32), value: 30720 }, BinaryIntOp { destination: Direct(32771), op: LessThan, bit_size: U32, lhs: Direct(0), rhs: Direct(32772) }, JumpIf { condition: Direct(32771), location: 207 }, IndirectConst { destination_pointer: Direct(1), bit_size: Integer(U64), value: 17843811134343075018 }, Trap { revert_data: HeapVector { pointer: Direct(1), size: Direct(2) } }, Return, BinaryIntOp { destination: Direct(32775), op: Add, bit_size: U32, lhs: Direct(32771), rhs: Direct(32773) }, Mov { destination: Direct(32776), source: Direct(32771) }, Mov { destination: Direct(32777), source: Direct(32772) }, BinaryIntOp { destination: Direct(32778), op: Equals, bit_size: U32, lhs: Direct(32776), rhs: Direct(32775) }, JumpIf { condition: Direct(32778), location: 218 }, Load { destination: Direct(32774), source_pointer: Direct(32776) }, Store { destination_pointer: Direct(32777), source: Direct(32774) }, BinaryIntOp { destination: Direct(32776), op: Add, bit_size: U32, lhs: Direct(32776), rhs: Direct(2) }, BinaryIntOp { destination: Direct(32777), op: Add, bit_size: U32, lhs: Direct(32777), rhs: Direct(2) }, Jump { location: 211 }, Return]"
+  ],
+  "debug_symbols": "[debug_symbols]",
+  "file_map": "[file_map]",
+  "names": [
+    "main"
+  ],
+  "brillig_names": [
+    "main"
+  ]
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/bit_shifts_u128/execute__tests__stdout.snap
```diff
@@ -0,0 +1,5 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stdout
+---
+
```
