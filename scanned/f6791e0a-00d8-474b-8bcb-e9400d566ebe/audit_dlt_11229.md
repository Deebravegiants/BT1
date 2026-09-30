# [?] fix(ssa): keep out-of-bounds constant array-get well-typed for arrays of tuples (#13178)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-06-25
Source: https://github.com/noir-lang/noir/commit/932383b37b859bbf2c914711caaaef68e59e8731
Type: security-commit

## Details
fix(ssa): keep out-of-bounds constant array-get well-typed for arrays of tuples (#13178)

## Patch
### compiler/noirc_evaluator/src/ssa/ir/dfg/simplify.rs
```diff
@@ -174,13 +174,14 @@ pub(crate) fn simplify(
         Instruction::ConstrainNotEqual(..) => None,
         Instruction::ArrayGet { array, index } => {
             if trap_on_constant_out_of_bounds(dfg, block, call_stack, *array, *index) {
-                // The result is dead (the trap aborts first), but must stay well-typed, so read
-                // index 0 instead of the out-of-bounds offset.
-                let zero = dfg.make_constant(FieldElement::zero(), NumericType::length_type());
-                return SimplifiedToInstruction(Instruction::ArrayGet {
-                    array: *array,
-                    index: zero,
-                });
+                // The result is dead (the trap aborts first) but must stay well-typed. Reading a
+                // fixed slot such as index 0 is unsound for arrays whose element type flattens to
+                // several differently-typed fields (tuples/structs): slot 0 holds the first
+                // field's type, which need not match the type this `array_get` produces. Collapse
+                // the out-of-bounds index onto an in-bounds slot of the *same* flattened field.
+                let in_bounds = in_bounds_index_of_same_field(dfg, *array, *index);
+                let index = dfg.make_constant(in_bounds.into(), NumericType::length_type());
+                return SimplifiedToInstruction(Instruction::ArrayGet { array: *array, index });
             }
 
             if let Some(index) = dfg.get_numeric_constant(*index) {
@@ -480,6 +481,33 @@ fn trap_on_constant_out_of_bounds(
     true
 }
 
+/// Map a statically out-of-bounds constant `array_get` index onto an in-bounds index that selects
+/// a slot of the *same flattened field type*.
+///
+/// An array of `N` elements whose element type flattens to `element_size` fields lays those fields
+/// out as `element_size` repeating slots, so the flattened slot at index `i` has the same type as
+/// the slot at `i % element_size`. Collapsing the out-of-bounds index into the first element —
+/// `offset + (i - offset) % element_size` — preserves that field type while guaranteeing the result
+/// is in bounds, since every array has at least one element. This keeps the (dead) result of an
+/// out-of-bounds access well-typed even for arrays of tuples/structs, where reading a fixed slot
+/// such as index 0 would change the result type.
+///
+/// The index is required to be a constant; this is only called once
+/// [`trap_on_constant_out_of_bounds`] has confirmed a constant, out-of-bounds index.
+fn in_bounds_index_of_same_field(dfg: &DataFlowGraph, array: ValueId, index: ValueId) -> u128 {
+    let element_size = u128::from(dfg.type_of_value(array).element_size().0);
+    let offset = u128::from(dfg.array_offset(array, index).to_u32());
+    let index = dfg
+        .get_numeric_constant(index)
+        .expect("trap_on_constant_out_of_bounds only returns true for constant indices")
+        .to_u128();
+    // An empty element type has no slots to read; there is no field type to preserve.
+    if element_size == 0 {
+        return offset;
+    }
+    offset + (index.saturating_sub(offset) % element_size)
+}
+
 /// See [`crate::ssa::opt::try_optimize_array_get_from_previous_instructions`] for more information.
 fn try_optimize_array_get_from_previous_instructions(
     dfg: &mut DataFlowGraph,
@@ -635,6 +663,37 @@ mod tests {
         let _ = Ssa::from_str_simplifying(src).unwrap();
     }
 
+    /// Regression for a type-unsoundness in the constant out-of-bounds Brillig array-get
+    /// handling. When a constant index is statically out of bounds the access is preceded by
+    /// an "Index out of bounds" trap, so its result is dead — but it must still be well-typed.
+    /// The handling rewrote the access to read flattened index 0, which only has the right
+    /// type when every element field shares a type. For an array of tuples (heterogeneous
+    /// flattened fields) index 0 has the *first* field's type, so a `[u8; 1]` (or any non-first
+    /// field) access folded to the leading `u64`, producing a `jmp` argument whose type no
+    /// longer matched its destination block parameter (fuzzer seeds 0xc8d17dd100100000 and
+    /// 0xfa4515e400100000).
+    ///
+    /// `from_str_simplifying` performs the out-of-bounds rewrite; `array_get_optimization` then
+    /// folds the in-bounds constant-index get to its element, which is where a wrongly-typed slot
+    /// would surface. Validating the SSA afterwards must not panic.
+    #[test]
+    fn oob_constant_array_get_on_tuple_array_stays_well_typed() {
+        let src = "
+        brillig(inline) fn main f0 {
+          b0():
+            v0 = make_array b\"A\"
+            v1 = make_array [u64 0, v0] : [(u64, [u8; 1]); 1]
+            v2 = array_get v1, index u32 3 -> [u8; 1]
+            jmp b1(v2)
+          b1(v3: [u8; 1]):
+            return v3
+        }
+        ";
+        let ssa = Ssa::from_str_simplifying(src).unwrap();
+        let ssa = ssa.array_get_optimization();
+        crate::ssa::ssa_gen::validate_ssa(&ssa);
+    }
+
     #[test]
     fn removes_range_constraints_on_constants() {
         let src = r#"
```
