# [?] fix: don't overflow when casting signed value to u128 (#8526)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-05-15
Source: https://github.com/noir-lang/noir/commit/bc002e0721c8b6847b182fdf2233e70dd86b16bf
Type: security-commit

## Details
fix: don't overflow when casting signed value to u128 (#8526)

## Patch
### compiler/noirc_evaluator/src/ssa/function_builder/mod.rs
```diff
@@ -549,10 +549,10 @@ impl std::ops::Index<BasicBlockId> for FunctionBuilder {
 fn validate_numeric_type(typ: &NumericType) {
     match &typ {
         NumericType::Signed { bit_size } => match bit_size {
-            8 | 16 | 32 | 64 => (),
+            8 | 16 | 32 | 64 | 128 => (),
             _ => {
                 panic!(
-                    "Invalid bit size for signed numeric type: {bit_size}. Expected one of 8, 16, 32 or 64."
+                    "Invalid bit size for signed numeric type: {bit_size}. Expected one of 8, 16, 32, 64 or 128."
                 );
             }
         },
```

### compiler/noirc_evaluator/src/ssa/ssa_gen/context.rs
```diff
@@ -665,10 +665,19 @@ impl<'a> FunctionContext<'a> {
                         // value_sign is 1 if the value is positive, 0 otherwise
                         let value_sign =
                             self.builder.insert_binary(value_as_unsigned, BinaryOp::Lt, half_width);
-
+                        let max_for_incoming_type_size = if *incoming_type_size == 128 {
+                            u128::MAX
+                        } else {
+                            2_u128.pow(*incoming_type_size) - 1
+                        };
+                        let max_for_target_type_size = if target_type_size == 128 {
+                            u128::MAX
+                        } else {
+                            2_u128.pow(target_type_size) - 1
+                        };
                         let patch = self.builder.numeric_constant(
                             FieldElement::from(
-                                2_u128.pow(target_type_size) - 2_u128.pow(*incoming_type_size),
+                                max_for_target_type_size - max_for_incoming_type_size,
                             ),
                             NumericType::unsigned(target_type_size),
                         );
```

### test_programs/execution_success/cast_to_u128/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+[package]
+name = "cast_to_u128"
+version = "0.1.0"
+type = "bin"
+authors = [""]
+
+[dependencies]
```

### test_programs/execution_success/cast_to_u128/Prover.toml
```diff
@@ -0,0 +1 @@
+x = -1
```

### test_programs/execution_success/cast_to_u128/src/main.nr
```diff
@@ -0,0 +1,6 @@
+fn main(x: i8) {
+    let y: i8 = -1;
+
+    assert_eq(x as u128, 340282366920938463463374607431768211455);
+    assert_eq(y as u128, 340282366920938463463374607431768211455);
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/cast_to_u128/execute__tests__force_brillig_false_inliner_-9223372036854775808.snap
```diff
@@ -0,0 +1,51 @@
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
+          "sign": "signed",
+          "width": 8
+        },
+        "visibility": "private"
+      }
+    ],
+    "return_type": null,
+    "error_types": {}
+  },
+  "bytecode": [
+    "func 0",
+    "current witness index : _2",
+    "private parameters indices : [_0]",
+    "public parameters indices : []",
+    "return value indices : []",
+    "BLACKBOX::RANGE [(_0, 8)] []",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(0))], q_c: 128 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(1)), Simple(Witness(2))]",
+    "BLACKBOX::RANGE [(_1, 1)] []",
+    "BLACKBOX::RANGE [(_2, 8)] []",
+    "EXPR [ (1, _0) (-256, _1) (-1, _2) 128 ]",
+    "EXPR [ (1, _0) (340282366920938463463374607431768211200, _1) -340282366920938463463374607431768211455 ]",
+    "unconstrained func 0",
+    "[Const { destination: Direct(10), bit_size: Integer(U32), value: 2 }, Const { destination: Direct(11), bit_size: Integer(U32), value: 0 }, CalldataCopy { destination_address: Direct(0), size_address: Direct(10), offset_address: Direct(11) }, BinaryFieldOp { destination: Direct(2), op: IntegerDiv, lhs: Direct(0), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Mul, lhs: Direct(2), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Sub, lhs: Direct(0), rhs: Direct(1) }, Mov { destination: Direct(0), source: Direct(2) }, Stop { return_data: HeapVector { pointer: Direct(11), size: Direct(10) } }]"
+  ],
+  "debug_symbols": "lZDBCoMwDIbfJece1M0dfJUxpNY4CqEtsRWG+O6LRTc97LBL0uTP15B/hh679GytG/wIzX2Gji2RfbbkjY7WO+nOi4K9bCMjSgsOulBBM7oIjUtECiZNKQ+NQbuco2ZRCwXoesny4WAJ19eivnTxG62rjb2VH7j+ny6L6oQ/pNLG8ulcKGVQQZXjJcdrjjU0Kz5ptroj3KwZkjMHp+Ir7MruZWBvsE+M65qsyeI3",
+  "file_map": {
+    "50": {
+      "source": "fn main(x: i8) {\n    let y: i8 = -1;\n\n    assert_eq(x as u128, 340282366920938463463374607431768211455);\n    assert_eq(y as u128, 340282366920938463463374607431768211455);\n}\n",
+      "path": ""
+    }
+  },
+  "names": [
+    "main"
+  ],
+  "brillig_names": [
+    "directive_integer_quotient"
+  ]
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/cast_to_u128/execute__tests__force_brillig_false_inliner_0.snap
```diff
@@ -0,0 +1,51 @@
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
+          "sign": "signed",
+          "width": 8
+        },
+        "visibility": "private"
+      }
+    ],
+    "return_type": null,
+    "error_types": {}
+  },
+  "bytecode": [
+    "func 0",
+    "current witness index : _2",
+    "private parameters indices : [_0]",
+    "public parameters indices : []",
+    "return value indices : []",
+    "BLACKBOX::RANGE [(_0, 8)] []",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(0))], q_c: 128 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(1)), Simple(Witness(2))]",
+    "BLACKBOX::RANGE [(_1, 1)] []",
+    "BLACKBOX::RANGE [(_2, 8)] []",
+    "EXPR [ (1, _0) (-256, _1) (-1, _2) 128 ]",
+    "EXPR [ (1, _0) (340282366920938463463374607431768211200, _1) -340282366920938463463374607431768211455 ]",
+    "unconstrained func 0",
+    "[Const { destination: Direct(10), bit_size: Integer(U32), value: 2 }, Const { destination: Direct(11), bit_size: Integer(U32), value: 0 }, CalldataCopy { destination_address: Direct(0), size_address: Direct(10), offset_address: Direct(11) }, BinaryFieldOp { destination: Direct(2), op: IntegerDiv, lhs: Direct(0), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Mul, lhs: Direct(2), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Sub, lhs: Direct(0), rhs: Direct(1) }, Mov { destination: Direct(0), source: Direct(2) }, Stop { return_data: HeapVector { pointer: Direct(11), size: Direct(10) } }]"
+  ],
+  "debug_symbols": "lZDBCoMwDIbfJece1M0dfJUxpNY4CqEtsRWG+O6LRTc97LBL0uTP15B/hh679GytG/wIzX2Gji2RfbbkjY7WO+nOi4K9bCMjSgsOulBBM7oIjUtECiZNKQ+NQbuco2ZRCwXoesny4WAJ19eivnTxG62rjb2VH7j+ny6L6oQ/pNLG8ulcKGVQQZXjJcdrjjU0Kz5ptroj3KwZkjMHp+Ir7MruZWBvsE+M65qsyeI3",
+  "file_map": {
+    "50": {
+      "source": "fn main(x: i8) {\n    let y: i8 = -1;\n\n    assert_eq(x as u128, 340282366920938463463374607431768211455);\n    assert_eq(y as u128, 340282366920938463463374607431768211455);\n}\n",
+      "path": ""
+    }
+  },
+  "names": [
+    "main"
+  ],
+  "brillig_names": [
+    "directive_integer_quotient"
+  ]
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/cast_to_u128/execute__tests__force_brillig_false_inliner_9223372036854775807.snap
```diff
@@ -0,0 +1,51 @@
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
+          "sign": "signed",
+          "width": 8
+        },
+        "visibility": "private"
+      }
+    ],
+    "return_type": null,
+    "error_types": {}
+  },
+  "bytecode": [
+    "func 0",
+    "current witness index : _2",
+    "private parameters indices : [_0]",
+    "public parameters indices : []",
+    "return value indices : []",
+    "BLACKBOX::RANGE [(_0, 8)] []",
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(0))], q_c: 128 }), Single(Expression { mul_terms: [], linear_combinations: [], q_c: 256 })], outputs: [Simple(Witness(1)), Simple(Witness(2))]",
+    "BLACKBOX::RANGE [(_1, 1)] []",
+    "BLACKBOX::RANGE [(_2, 8)] []",
+    "EXPR [ (1, _0) (-256, _1) (-1, _2) 128 ]",
+    "EXPR [ (1, _0) (340282366920938463463374607431768211200, _1) -340282366920938463463374607431768211455 ]",
+    "unconstrained func 0",
+    "[Const { destination: Direct(10), bit_size: Integer(U32), value: 2 }, Const { destination: Direct(11), bit_size: Integer(U32), value: 0 }, CalldataCopy { destination_address: Direct(0), size_address: Direct(10), offset_address: Direct(11) }, BinaryFieldOp { destination: Direct(2), op: IntegerDiv, lhs: Direct(0), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Mul, lhs: Direct(2), rhs: Direct(1) }, BinaryFieldOp { destination: Direct(1), op: Sub, lhs: Direct(0), rhs: Direct(1) }, Mov { destination: Direct(0), source: Direct(2) }, Stop { return_data: HeapVector { pointer: Direct(11), size: Direct(10) } }]"
+  ],
+  "debug_symbols": "lZDBCoMwDIbfJece1M0dfJUxpNY4CqEtsRWG+O6LRTc97LBL0uTP15B/hh679GytG/wIzX2Gji2RfbbkjY7WO+nOi4K9bCMjSgsOulBBM7oIjUtECiZNKQ+NQbuco2ZRCwXoesny4WAJ19eivnTxG62rjb2VH7j+ny6L6oQ/pNLG8ulcKGVQQZXjJcdrjjU0Kz5ptroj3KwZkjMHp+Ir7MruZWBvsE+M65qsyeI3",
+  "file_map": {
+    "50": {
+      "source": "fn main(x: i8) {\n    let y: i8 = -1;\n\n    assert_eq(x as u128, 340282366920938463463374607431768211455);\n    assert_eq(y as u128, 340282366920938463463374607431768211455);\n}\n",
+      "path": ""
+    }
+  },
+  "names": [
+    "main"
+  ],
+  "brillig_names": [
+    "directive_integer_quotient"
+  ]
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/cast_to_u128/execute__tests__force_brillig_true_inliner_-9223372036854775808.snap
```diff
@@ -0,0 +1,51 @@
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
+          "sign": "signed",
+          "width": 8
+        },
+        "visibility": "private"
+      }
+    ],
+    "return_type": null,
+    "error_types": {
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
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(0))], q_c: 0 })], outputs: []",
+    "unconstrained func 0",
+    "[Const { destination: Direct(2), bit_size: Integer(U32), value: 1 }, Const { destination: Direct(1), bit_size: Integer(U32), value: 32837 }, Const { destination: Direct(0), bit_size: Integer(U32), value: 3 }, Const { destination: Relative(2), bit_size: Integer(U32), value: 1 }, Const { destination: Relative(3), bit_size: Integer(U32), value: 0 }, CalldataCopy { destination_address: Direct(32836), size_address: Relative(2), offset_address: Relative(3) }, Cast { destination: Direct(32836), source: Direct(32836), bit_size: Integer(U8) }, Mov { destination: Relative(1), source: Direct(32836) }, Call { location: 13 }, Call { location: 14 }, Const { destination: Relative(1), bit_size: Integer(U32), value: 32837 }, Const { destination: Relative(2), bit_size: Integer(U32), value: 0 }, Stop { return_data: HeapVector { pointer: Relative(1), size: Relative(2) } }, Return, Call { location: 30 }, Cast { destination: Relative(2), source: Relative(1), bit_size: Integer(U8) }, Const { destination: Relative(3), bit_size: Integer(U8), value: 128 }, BinaryIntOp { destination: Relative(4), op: LessThan, bit_size: U8, lhs: Relative(2), rhs: Relative(3) }, Not { destination: Relative(2), source: Relative(4), bit_size: U1 }, Cast { destination: Relative(3), source: Relative(2), bit_size: Integer(U128) }, Const { destination: Relative(2), bit_size: Integer(U128), value: 340282366920938463463374607431768211200 }, BinaryIntOp { destination: Relative(4), op: Mul, bit_size: U128, lhs: Relative(2), rhs: Relative(3) }, Cast { destination: Relative(2), source: Relative(1), bit_size: Integer(U128) }, BinaryIntOp { destination: Relative(1), op: Add, bit_size: U128, lhs: Relative(4), rhs: Relative(2) }, Const { destination: Relative(2), bit_size: Integer(U128), value: 340282366920938463463374607431768211455 }, BinaryIntOp { destination: Relative(3), op: Equals, bit_size: U128, lhs: Relative(1), rhs: Relative(2) }, JumpIf { condition: Relative(3), location: 29 }, Const { destination: Relative(4), bit_size: Integer(U32), value: 0 }, Trap { revert_data: HeapVector { pointer: Direct(1), size: Relative(4) } }, Return, Const { destination: Direct(32772), bit_size: Integer(U32), value: 30720 }, BinaryIntOp { destination: Direct(32771), op: LessThan, bit_size: U32, lhs: Direct(0), rhs: Direct(32772) }, JumpIf { condition: Direct(32771), location: 35 }, IndirectConst { destination_pointer: Direct(1), bit_size: Integer(U64), value: 17843811134343075018 }, Trap { revert_data: HeapVector { pointer: Direct(1), size: Direct(2) } }, Return]"
+  ],
+  "debug_symbols": "lZHBbsMgDIbfxWcOQEa65VWqKiKJUyEhElGYNEW8+0zcbOlhh138Ycz/28IbTDjke+/CvDygu24wROe9u/d+GW1yS6DbDWQNykCnBKiWcWG8Mz52aMlQDM1oGG/QaYJhtIwLg1x0KQKOrn2KiLXpaQwabrURQ4IuZO8FfFqf90eP1YadyUaqSgEYJiIZzs5jPRXxq5Z/S41+alv1Izb/VyupX+Q3yuzo4suvlmoUnR08PtM5h/FUTV/rUTm2ssZlxClHrE6n1VC8NlI05lZqt28=",
+  "file_map": {
+    "50": {
+      "source": "fn main(x: i8) {\n    let y: i8 = -1;\n\n    assert_eq(x as u128, 340282366920938463463374607431768211455);\n    assert_eq(y as u128, 340282366920938463463374607431768211455);\n}\n",
+      "path": ""
+    }
+  },
+  "names": [
+    "main"
+  ],
+  "brillig_names": [
+    "main"
+  ]
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/cast_to_u128/execute__tests__force_brillig_true_inliner_0.snap
```diff
@@ -0,0 +1,51 @@
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
+          "sign": "signed",
+          "width": 8
+        },
+        "visibility": "private"
+      }
+    ],
+    "return_type": null,
+    "error_types": {
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
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(0))], q_c: 0 })], outputs: []",
+    "unconstrained func 0",
+    "[Const { destination: Direct(2), bit_size: Integer(U32), value: 1 }, Const { destination: Direct(1), bit_size: Integer(U32), value: 32837 }, Const { destination: Direct(0), bit_size: Integer(U32), value: 3 }, Const { destination: Relative(2), bit_size: Integer(U32), value: 1 }, Const { destination: Relative(3), bit_size: Integer(U32), value: 0 }, CalldataCopy { destination_address: Direct(32836), size_address: Relative(2), offset_address: Relative(3) }, Cast { destination: Direct(32836), source: Direct(32836), bit_size: Integer(U8) }, Mov { destination: Relative(1), source: Direct(32836) }, Call { location: 13 }, Call { location: 14 }, Const { destination: Relative(1), bit_size: Integer(U32), value: 32837 }, Const { destination: Relative(2), bit_size: Integer(U32), value: 0 }, Stop { return_data: HeapVector { pointer: Relative(1), size: Relative(2) } }, Return, Call { location: 30 }, Cast { destination: Relative(2), source: Relative(1), bit_size: Integer(U8) }, Const { destination: Relative(3), bit_size: Integer(U8), value: 128 }, BinaryIntOp { destination: Relative(4), op: LessThan, bit_size: U8, lhs: Relative(2), rhs: Relative(3) }, Not { destination: Relative(2), source: Relative(4), bit_size: U1 }, Cast { destination: Relative(3), source: Relative(2), bit_size: Integer(U128) }, Const { destination: Relative(2), bit_size: Integer(U128), value: 340282366920938463463374607431768211200 }, BinaryIntOp { destination: Relative(4), op: Mul, bit_size: U128, lhs: Relative(2), rhs: Relative(3) }, Cast { destination: Relative(2), source: Relative(1), bit_size: Integer(U128) }, BinaryIntOp { destination: Relative(1), op: Add, bit_size: U128, lhs: Relative(4), rhs: Relative(2) }, Const { destination: Relative(2), bit_size: Integer(U128), value: 340282366920938463463374607431768211455 }, BinaryIntOp { destination: Relative(3), op: Equals, bit_size: U128, lhs: Relative(1), rhs: Relative(2) }, JumpIf { condition: Relative(3), location: 29 }, Const { destination: Relative(4), bit_size: Integer(U32), value: 0 }, Trap { revert_data: HeapVector { pointer: Direct(1), size: Relative(4) } }, Return, Const { destination: Direct(32772), bit_size: Integer(U32), value: 30720 }, BinaryIntOp { destination: Direct(32771), op: LessThan, bit_size: U32, lhs: Direct(0), rhs: Direct(32772) }, JumpIf { condition: Direct(32771), location: 35 }, IndirectConst { destination_pointer: Direct(1), bit_size: Integer(U64), value: 17843811134343075018 }, Trap { revert_data: HeapVector { pointer: Direct(1), size: Direct(2) } }, Return]"
+  ],
+  "debug_symbols": "lZHBbsMgDIbfxWcOQEa65VWqKiKJUyEhElGYNEW8+0zcbOlhh138Ycz/28IbTDjke+/CvDygu24wROe9u/d+GW1yS6DbDWQNykCnBKiWcWG8Mz52aMlQDM1oGG/QaYJhtIwLg1x0KQKOrn2KiLXpaQwabrURQ4IuZO8FfFqf90eP1YadyUaqSgEYJiIZzs5jPRXxq5Z/S41+alv1Izb/VyupX+Q3yuzo4suvlmoUnR08PtM5h/FUTV/rUTm2ssZlxClHrE6n1VC8NlI05lZqt28=",
+  "file_map": {
+    "50": {
+      "source": "fn main(x: i8) {\n    let y: i8 = -1;\n\n    assert_eq(x as u128, 340282366920938463463374607431768211455);\n    assert_eq(y as u128, 340282366920938463463374607431768211455);\n}\n",
+      "path": ""
+    }
+  },
+  "names": [
+    "main"
+  ],
+  "brillig_names": [
+    "main"
+  ]
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/cast_to_u128/execute__tests__force_brillig_true_inliner_9223372036854775807.snap
```diff
@@ -0,0 +1,51 @@
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
+          "sign": "signed",
+          "width": 8
+        },
+        "visibility": "private"
+      }
+    ],
+    "return_type": null,
+    "error_types": {
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
+    "BRILLIG CALL func 0: inputs: [Single(Expression { mul_terms: [], linear_combinations: [(1, Witness(0))], q_c: 0 })], outputs: []",
+    "unconstrained func 0",
+    "[Const { destination: Direct(2), bit_size: Integer(U32), value: 1 }, Const { destination: Direct(1), bit_size: Integer(U32), value: 32837 }, Const { destination: Direct(0), bit_size: Integer(U32), value: 3 }, Const { destination: Relative(2), bit_size: Integer(U32), value: 1 }, Const { destination: Relative(3), bit_size: Integer(U32), value: 0 }, CalldataCopy { destination_address: Direct(32836), size_address: Relative(2), offset_address: Relative(3) }, Cast { destination: Direct(32836), source: Direct(32836), bit_size: Integer(U8) }, Mov { destination: Relative(1), source: Direct(32836) }, Call { location: 13 }, Call { location: 14 }, Const { destination: Relative(1), bit_size: Integer(U32), value: 32837 }, Const { destination: Relative(2), bit_size: Integer(U32), value: 0 }, Stop { return_data: HeapVector { pointer: Relative(1), size: Relative(2) } }, Return, Call { location: 30 }, Cast { destination: Relative(2), source: Relative(1), bit_size: Integer(U8) }, Const { destination: Relative(3), bit_size: Integer(U8), value: 128 }, BinaryIntOp { destination: Relative(4), op: LessThan, bit_size: U8, lhs: Relative(2), rhs: Relative(3) }, Not { destination: Relative(2), source: Relative(4), bit_size: U1 }, Cast { destination: Relative(3), source: Relative(2), bit_size: Integer(U128) }, Const { destination: Relative(2), bit_size: Integer(U128), value: 340282366920938463463374607431768211200 }, BinaryIntOp { destination: Relative(4), op: Mul, bit_size: U128, lhs: Relative(2), rhs: Relative(3) }, Cast { destination: Relative(2), source: Relative(1), bit_size: Integer(U128) }, BinaryIntOp { destination: Relative(1), op: Add, bit_size: U128, lhs: Relative(4), rhs: Relative(2) }, Const { destination: Relative(2), bit_size: Integer(U128), value: 340282366920938463463374607431768211455 }, BinaryIntOp { destination: Relative(3), op: Equals, bit_size: U128, lhs: Relative(1), rhs: Relative(2) }, JumpIf { condition: Relative(3), location: 29 }, Const { destination: Relative(4), bit_size: Integer(U32), value: 0 }, Trap { revert_data: HeapVector { pointer: Direct(1), size: Relative(4) } }, Return, Const { destination: Direct(32772), bit_size: Integer(U32), value: 30720 }, BinaryIntOp { destination: Direct(32771), op: LessThan, bit_size: U32, lhs: Direct(0), rhs: Direct(32772) }, JumpIf { condition: Direct(32771), location: 35 }, IndirectConst { destination_pointer: Direct(1), bit_size: Integer(U64), value: 17843811134343075018 }, Trap { revert_data: HeapVector { pointer: Direct(1), size: Direct(2) } }, Return]"
+  ],
+  "debug_symbols": "lZHBbsMgDIbfxWcOQEa65VWqKiKJUyEhElGYNEW8+0zcbOlhh138Ycz/28IbTDjke+/CvDygu24wROe9u/d+GW1yS6DbDWQNykCnBKiWcWG8Mz52aMlQDM1oGG/QaYJhtIwLg1x0KQKOrn2KiLXpaQwabrURQ4IuZO8FfFqf90eP1YadyUaqSgEYJiIZzs5jPRXxq5Z/S41+alv1Izb/VyupX+Q3yuzo4suvlmoUnR08PtM5h/FUTV/rUTm2ssZlxClHrE6n1VC8NlI05lZqt28=",
+  "file_map": {
+    "50": {
+      "source": "fn main(x: i8) {\n    let y: i8 = -1;\n\n    assert_eq(x as u128, 340282366920938463463374607431768211455);\n    assert_eq(y as u128, 340282366920938463463374607431768211455);\n}\n",
+      "path": ""
+    }
+  },
+  "names": [
+    "main"
+  ],
+  "brillig_names": [
+    "main"
+  ]
+}
```

### tooling/nargo_cli/tests/snapshots/expand/execution_success/cast_to_u128/execute__tests__expanded.snap
```diff
@@ -0,0 +1,9 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: expanded_code
+---
+fn main(x: i8) {
+    let y: i8 = -1;
+    assert((x as u128) == 340282366920938463463374607431768211455);
+    assert((y as u128) == 340282366920938463463374607431768211455);
+}
```
