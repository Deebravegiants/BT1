# [?] fix(ssa): Cast to `u64` when inserting OOB checks in DIE (#10463)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-11-11
Source: https://github.com/noir-lang/noir/commit/bb32d34e16bdcf69fe258cf693dd142095979dec
Type: security-commit

## Details
fix(ssa): Cast to `u64` when inserting OOB checks in DIE (#10463)

## Patch
### compiler/noirc_evaluator/src/ssa/interpreter/mod.rs
```diff
@@ -1551,23 +1551,32 @@ fn evaluate_binary(
         ),
         BinaryOp::Eq => apply_int_comparison_op!(lhs, rhs, binary, |a, b| a == b, |a, b| a == b),
         BinaryOp::Lt => {
-            apply_int_comparison_op!(lhs, rhs, binary, |a, b| a < b, |_, _| unreachable!(
-                "unfit lt: fit types should have been restored already"
-            ))
+            apply_int_comparison_op!(lhs, rhs, binary, |a, b| a < b, |_, _| {
+                // This could be the result of the DIE pass removing an `ArrayGet` and leaving a `LessThan`
+                // and a `Constrain` in its place. `LessThan` implicitly includes a `RangeCheck` on
+                // the operands during ACIR generation, which an `Unfit` value would fail, so we
+                // cannot treat them differently here, even if we could compare the values as `u128` or `i128`.
+                //
+                // Instead we `Cast` the values in SSA, which should have converted our `Unfit` value
+                // back to a `Fit` one with an acceptable number of bits.
+                //
+                // If we still hit this case, we have a problem.
+                unreachable!("unfit 'lt': fit types should have been restored already")
+            })
         }
         BinaryOp::And => {
             apply_int_binop!(lhs, rhs, binary, |a, b| Some(a & b), |_, _| unreachable!(
-                "unfit and: fit types should have been restored already"
+                "unfit 'and': fit types should have been restored already"
             ))
         }
         BinaryOp::Or => {
             apply_int_binop!(lhs, rhs, binary, |a, b| Some(a | b), |_, _| unreachable!(
-                "unfit or: fit types should have been restored already"
+                "unfit 'or': fit types should have been restored already"
             ))
         }
         BinaryOp::Xor => {
             apply_int_binop!(lhs, rhs, binary, |a, b| Some(a ^ b), |_, _| unreachable!(
-                "unfit xor: fit types should have been restored already"
+                "unfit 'xor': fit types should have been restored already"
             ))
         }
         BinaryOp::Shl => {
```

### compiler/noirc_evaluator/src/ssa/opt/die.rs
```diff
@@ -1103,8 +1103,9 @@ mod test {
           b0(v0: u32):
             v2 = make_array [u32 0, u32 0] : [u32; 2]
             v3 = array_get v2, index v0 -> u32
-            v5 = lt v3, u32 2
-            constrain v5 == u1 1, "Index out of bounds"
+            v4 = cast v3 as u64
+            v6 = lt v4, u64 2
+            constrain v6 == u1 1, "Index out of bounds"
             return
         }
         "#);
```

### compiler/noirc_evaluator/src/ssa/opt/die/array_oob_checks.rs
```diff
@@ -92,10 +92,18 @@ impl Context {
                 };
                 // `index` will be relative to the flattened array length, so we need to take that into account
                 let array_length = element_size * len;
-                // let array_length = function.dfg.type_of_value(*array).flattened_size();
 
-                // If we are here it means the index is dynamic, so let's add a check that it's less than length
-                let length_type = NumericType::length_type();
+                // If we are here it means the index is dynamic, so let's add a check that it's less than length.
+
+                // Normally the indexes are expected to be u32, however if the array element is a composite type,
+                // the value could have overflown due to the unchecked multiplication with the element size.
+                // In ACIR, we rely on the array operation itself to fail the circuit if it encounters an overflown value,
+                // however we are just removing the array operation and replacing it with a LessThan, which in ACIR gen
+                // lays down an RangeCheck that would fail if the value doesn't fit 32 bits. As a workaround,
+                // instead of finding the index instruction and changing into a checked multiplication,
+                // we cast to a higher bitsize, which we expect should fit any overflown index type.
+                let length_type = NumericType::unsigned(64);
+
                 let index = function.dfg.insert_instruction_and_results(
                     Instruction::Cast(*index, length_type),
                     block_id,
```

### test_programs/execution_success/regression_10307/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "regression_10307"
+type = "bin"
+authors = [""]
+
+[dependencies]
\ No newline at end of file
```

### test_programs/execution_success/regression_10307/Prover.toml
```diff
@@ -0,0 +1,4 @@
+a = [[true, false], [false, false], [false, true]]
+b = "0x00000000000000000000000000000000000000000000000000000000d98e8c43"
+c = false
+return = false
```

### test_programs/execution_success/regression_10307/src/main.nr
```diff
@@ -0,0 +1,6 @@
+fn main(mut a: [(bool, bool); 3], b: u32, c: bool) -> pub bool {
+    for _ in 0..1 {
+        let _ = if c { a[b] } else { a[0] };
+    }
+    false
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/regression_10307/execute__tests__expanded.snap
```diff
@@ -0,0 +1,10 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: expanded_code
+---
+fn main(mut a: [(bool, bool); 3], b: u32, c: bool) -> pub bool {
+    for _ in 0_u32..1_u32 {
+        let _: (bool, bool) = if c { a[b] } else { a[0_u32] };
+    }
+    false
+}
```

### tooling/nargo_cli/tests/snapshots/execution_success/regression_10307/execute__tests__stdout.snap
```diff
@@ -0,0 +1,5 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stdout
+---
+[regression_10307] Circuit output: false
```
