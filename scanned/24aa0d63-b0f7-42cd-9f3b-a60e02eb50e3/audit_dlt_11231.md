# [?] fix(ssa): trap constant out-of-bounds Brillig array ops instead of al… (#13114)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-06-23
Source: https://github.com/noir-lang/noir/commit/4123bd2111aff3d3091187aa751f4fc41ec8d684
Type: security-commit

## Details
fix(ssa): trap constant out-of-bounds Brillig array ops instead of al… (#13114)

Co-authored-by: Aztec Bot <49558828+AztecBot@users.noreply.github.com>

## Patch
### compiler/noirc_evaluator/src/ssa/ir/dfg.rs
```diff
@@ -929,6 +929,31 @@ impl DataFlowGraph {
         }
     }
 
+    /// Returns `true` when `index` is a compile-time constant that is provably out of bounds for
+    /// `array`, given its statically known `length`. Returns `false` for non-constant indices and
+    /// for in-bounds accesses.
+    ///
+    /// In Brillig a constant array/vector index is shifted past the in-memory header (see
+    /// `brillig_array_gets`); [`Self::array_offset`] is that shift in Brillig and `None` (`0`) in
+    /// ACIR, so subtracting it recovers the logical index and the same check serves both runtimes.
+    pub(crate) fn constant_index_is_out_of_bounds(
+        &self,
+        array: ValueId,
+        index: ValueId,
+        length: SemanticLength,
+    ) -> bool {
+        let Some(index_constant) = self.get_numeric_constant(index) else {
+            return false;
+        };
+        let semi_flattened_length =
+            u128::from((length * self.type_of_value(array).element_size()).0);
+        let offset = u128::from(self.array_offset(array, index).to_u32());
+        index_constant
+            .to_u128()
+            .checked_sub(offset)
+            .is_none_or(|logical_index| logical_index >= semi_flattened_length)
+    }
+
     /// Check if the results of an instruction are used in the databus to return a value..
     ///
     /// This only applies to ACIR, as in Brillig the databus will always be empty.
```

### compiler/noirc_evaluator/src/ssa/ir/dfg/simplify.rs
```diff
@@ -173,6 +173,16 @@ pub(crate) fn simplify(
         }
         Instruction::ConstrainNotEqual(..) => None,
         Instruction::ArrayGet { array, index } => {
+            if trap_on_constant_out_of_bounds(dfg, block, call_stack, *array, *index) {
+                // The result is dead (the trap aborts first), but must stay well-typed, so read
+                // index 0 instead of the out-of-bounds offset.
+                let zero = dfg.make_constant(FieldElement::zero(), NumericType::length_type());
+                return SimplifiedToInstruction(Instruction::ArrayGet {
+                    array: *array,
+                    index: zero,
+                });
+            }
+
             if let Some(index) = dfg.get_numeric_constant(*index) {
                 return try_optimize_array_get_from_previous_instructions(dfg, *array, index);
             }
@@ -189,6 +199,11 @@ pub(crate) fn simplify(
             }
         }
         Instruction::ArraySet { array: array_id, index: index_id, value, .. } => {
+            if trap_on_constant_out_of_bounds(dfg, block, call_stack, *array_id, *index_id) {
+                // The result is dead (the trap aborts first); forward the unmodified source array
+                // so any downstream use stays well-typed.
+                return SimplifiedTo(*array_id);
+            }
             try_optimize_array_set_from_previous_get(dfg, *array_id, *index_id, *value)
         }
         Instruction::Truncate { value, bit_size, max_bit_size } => {
@@ -423,6 +438,48 @@ fn optimize_length_one_array_read(
     }
 }
 
+/// In a Brillig function, a constant index that is statically out of bounds for a known-length
+/// array can never be valid, so the array operation is replaced with an "Index out of bounds" trap.
+/// Without this, the operation reaches Brillig codegen as a plain memory access at the out-of-bounds
+/// offset, and the Brillig VM grows its memory to fit that offset — a large constant index requests
+/// gigabytes of memory before any check fires.
+///
+/// Returns `false` (leaving the instruction for the normal simplification path) for ACIR functions,
+/// whose memory model and the `array_oob_checks` DIE pass already cover this; for vectors, whose
+/// length is not known at compile time; for non-constant indices; and for in-bounds indices.
+///
+/// In Brillig there is no global side-effects predicate (`EnableSideEffectsIf` is stripped before
+/// codegen and conditionally-dead array operations are never flattened), so the inserted trap stays
+/// in the same branch as the original operation and inherits its exact reachability.
+fn trap_on_constant_out_of_bounds(
+    dfg: &mut DataFlowGraph,
+    block: BasicBlockId,
+    call_stack: CallStackId,
+    array: ValueId,
+    index: ValueId,
+) -> bool {
+    if !dfg.runtime().is_brillig() {
+        return false;
+    }
+    // Only known-length arrays have a compile-time bound; vectors do not.
+    let Some(length) = dfg.try_get_array_length(array) else {
+        return false;
+    };
+    if !dfg.constant_index_is_out_of_bounds(array, index, length) {
+        return false;
+    }
+
+    let false_const = dfg.make_constant(false.into(), NumericType::bool());
+    let true_const = dfg.make_constant(true.into(), NumericType::bool());
+    let trap = Instruction::Constrain(
+        false_const,
+        true_const,
+        Some(ConstrainError::from("Index out of bounds".to_string())),
+    );
+    dfg.insert_instruction_and_results(trap, block, None, call_stack);
+    true
+}
+
 /// See [`crate::ssa::opt::try_optimize_array_get_from_previous_instructions`] for more information.
 fn try_optimize_array_get_from_previous_instructions(
     dfg: &mut DataFlowGraph,
@@ -857,4 +914,97 @@ mod tests {
             "truncate of field division result was incorrectly simplified to the division result"
         );
     }
+
+    #[test]
+    fn brillig_array_set_with_constant_oob_index_traps() {
+        let src = "
+        brillig(inline) fn main f0 {
+          b0(v0: u32):
+            v1 = make_array [v0, v0, v0, v0] : [u32; 4]
+            v2 = array_set v1, index u32 1000000000, value v0
+            return v2
+        }
+        ";
+        let ssa = Ssa::from_str_simplifying(src).unwrap();
+
+        assert_ssa_snapshot!(ssa, @r#"
+        brillig(inline) fn main f0 {
+          b0(v0: u32):
+            v1 = make_array [v0, v0, v0, v0] : [u32; 4]
+            constrain u1 0 == u1 1, "Index out of bounds"
+            return v1
+        }
+        "#);
+    }
+
+    #[test]
+    fn brillig_array_get_with_constant_oob_index_traps() {
+        let src = "
+        brillig(inline) fn main f0 {
+          b0(v0: u32):
+            v1 = make_array [v0, v0, v0, v0] : [u32; 4]
+            v2 = array_get v1, index u32 1000000000 -> u32
+            return v2
+        }
+        ";
+        let ssa = Ssa::from_str_simplifying(src).unwrap();
+
+        assert_ssa_snapshot!(ssa, @r#"
+        brillig(inline) fn main f0 {
+          b0(v0: u32):
+            v1 = make_array [v0, v0, v0, v0] : [u32; 4]
+            constrain u1 0 == u1 1, "Index out of bounds"
+            v5 = array_get v1, index u32 0 -> u32
+            return v5
+        }
+        "#);
+    }
+
+    #[test]
+    fn acir_array_set_with_constant_oob_index_is_not_trapped_at_simplify() {
+        // The constant-OOB trap is Brillig-only: ACIR relies on its memory model and the
+        // dedicated `array_oob_checks` DIE pass, so simplification must leave ACIR untouched.
+        let src = "
+        acir(inline) fn main f0 {
+          b0(v0: u32):
+            v1 = make_array [v0, v0, v0, v0] : [u32; 4]
+            v2 = array_set v1, index u32 1000000000, value v0
+            return v2
+        }
+        ";
+        let ssa = Ssa::from_str_simplifying(src).unwrap();
+        assert_normalized_ssa_equals(ssa, src);
+    }
+
+    #[test]
+    fn brillig_in_bounds_offset_index_is_not_trapped() {
+        // After `brillig_array_get_and_set` shifts a constant index past the array header, a valid
+        // in-bounds access (here logical index 0, written as `1 minus 1`) must not be trapped: the
+        // out-of-bounds check has to undo the offset before comparing against the length.
+        let src = "
+        brillig(inline) fn main f0 {
+          b0(v0: u32):
+            v1 = make_array [v0, v0, v0, v0] : [u32; 4]
+            v3 = array_set v1, index u32 1 minus 1, value u32 9
+            return v3
+        }
+        ";
+        let ssa = Ssa::from_str_simplifying(src).unwrap();
+        assert_normalized_ssa_equals(ssa, src);
+    }
+
+    #[test]
+    fn brillig_array_set_with_constant_oob_index_on_vector_is_not_trapped() {
+        // Vectors have a dynamic length unknown at compile time, so a constant index can never
+        // be proven out of bounds here; only known-length arrays are trapped.
+        let src = "
+        brillig(inline) fn main f0 {
+          b0(v0: [u32]):
+            v2 = array_set v0, index u32 1000000000, value u32 0
+            return v2
+        }
+        ";
+        let ssa = Ssa::from_str_simplifying(src).unwrap();
+        assert_normalized_ssa_equals(ssa, src);
+    }
 }
```

### compiler/noirc_evaluator/src/ssa/opt/remove_unreachable_instructions.rs
```diff
@@ -347,9 +347,7 @@ impl Function {
                     };
 
                     let array_op_always_fails = len.0 == 0
-                        || context.dfg.get_numeric_constant(*index).is_some_and(|index| {
-                            (index.try_to_u32().unwrap()) >= (array_type.element_size() * len).0
-                        });
+                        || context.dfg.constant_index_is_out_of_bounds(*array, *index, len);
                     if !array_op_always_fails {
                         return;
                     }
```

### test_programs/execution_failure/brillig_constant_oob_array_set/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+[package]
+name = "brillig_constant_oob_array_set"
+type = "bin"
+authors = [""]
+compiler_version = ">=0.31.0"
+
+[dependencies]
```

### test_programs/execution_failure/brillig_constant_oob_array_set/Prover.toml
```diff
@@ -0,0 +1 @@
+value = "7"
```

### test_programs/execution_failure/brillig_constant_oob_array_set/src/main.nr
```diff
@@ -0,0 +1,14 @@
+// A constant out-of-bounds index into a known-length array in an unconstrained (Brillig)
+// function must fail with "Index out of bounds" rather than letting the Brillig VM grow its
+// memory to fit the out-of-bounds offset (see issue #10035).
+unconstrained fn main(value: u32) -> pub [u32; 4] {
+    let mut array: [u32; 4] = [value; 4];
+    array[index()] = value;
+    array
+}
+
+// Indirection so the index is a compile-time constant in SSA without being a literal array index
+// that the frontend would reject up front.
+fn index() -> u32 {
+    1000000000
+}
```

### tooling/nargo_cli/tests/snapshots/execution_failure/brillig_constant_oob_array_set/execute__tests__acir_stderr.snap
```diff
@@ -0,0 +1,15 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Assertion failed: Index out of bounds
+  ┌─ src/main.nr:6:5
+  │
+6 │     array[index()] = value;
+  │     --------------
+  │
+  = Call stack:
+    1: main
+            at src/main.nr:6:5
+
+Failed assertion
```

### tooling/nargo_cli/tests/snapshots/execution_failure/brillig_constant_oob_array_set/execute__tests__brillig_stderr.snap
```diff
@@ -0,0 +1,15 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Assertion failed: Index out of bounds
+  ┌─ src/main.nr:6:5
+  │
+6 │     array[index()] = value;
+  │     --------------
+  │
+  = Call stack:
+    1: main
+            at src/main.nr:6:5
+
+Failed assertion
```

### tooling/nargo_cli/tests/snapshots/execution_failure/brillig_constant_oob_array_set/execute__tests__comptime_stderr.snap
```diff
@@ -0,0 +1,12 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Index out of bounds: 1000000000 is out of bounds for the array of length 4
+  ┌─ src/main.nr:6:5
+  │
+6 │     array[index()] = value;
+  │     --------------
+  │
+
+Error interpreting main function
```
