# [?] fix(ssa): Handle partially removed `ArrayGet` groups of complex type during OOB checks (#10027)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-09-30
Source: https://github.com/noir-lang/noir/commit/39f193cf14d97b200611dd6f6c9dac42f52b0b63
Type: security-commit

## Details
fix(ssa): Handle partially removed `ArrayGet` groups of complex type during OOB checks (#10027)

## Patch
### compiler/noirc_evaluator/src/ssa/opt/die.rs
```diff
@@ -318,7 +318,11 @@ impl Context {
                 block_id,
                 &mut possible_index_out_of_bounds_indexes,
             );
-            // There's a slight chance we didn't insert any checks, so we could proceed with DIE.
+            // There's a chance we didn't insert any checks, so we could proceed with DIE.
+            // This can happen for example with arrays of a complex type, where one part
+            // of the complex type is used, while the other is not, in which case no constraint
+            // is inserted, because the use itself will cause an OOB error.
+            // By proceeding, the unused access will be removed.
             if inserted_check {
                 return true;
             }
@@ -1163,4 +1167,31 @@ mod test {
         // Thus, when we later go to do `v22 = array_set v21, index u32 0, value v3` once more, we will be writing [1] rather than [2].
         assert_ssa_does_not_change(src, Ssa::dead_instruction_elimination);
     }
+
+    #[test]
+    fn replaces_oob_followed_by_safe_access_with_constraint() {
+        let src = r#"
+        acir(inline) predicate_pure fn main f0 {
+          b0():
+            v2 = make_array b"KO"
+            v4 = make_array [u1 0, v2] : [(u1, [u8; 2]); 1]
+            v6 = array_get v4, index u32 20 -> u1
+            v8 = array_get v4, index u32 1 -> [u8; 2]
+            return v8
+        }
+        "#;
+        let ssa = Ssa::from_str(src).unwrap();
+        let ssa = ssa.dead_instruction_elimination();
+
+        assert_ssa_snapshot!(ssa, @r#"
+        acir(inline) predicate_pure fn main f0 {
+          b0():
+            v2 = make_array b"KO"
+            v4 = make_array [u1 0, v2] : [(u1, [u8; 2]); 1]
+            constrain u1 0 == u1 1, "Index out of bounds"
+            v7 = array_get v4, index u32 1 -> [u8; 2]
+            return v7
+        }
+        "#);
+    }
 }
```

### compiler/noirc_evaluator/src/ssa/opt/die/array_oob_checks.rs
```diff
@@ -4,7 +4,7 @@ use crate::ssa::{
     ir::{
         basic_block::BasicBlockId,
         function::Function,
-        instruction::{BinaryOp, Instruction},
+        instruction::{Binary, BinaryOp, Instruction, InstructionId},
         types::{NumericType, Type},
         value::ValueId,
     },
@@ -53,6 +53,7 @@ impl Context {
                     index,
                     &mut next_out_of_bounds_index,
                     possible_index_out_of_bounds_indexes,
+                    &instructions,
                 );
             }
 
@@ -164,12 +165,28 @@ pub(super) fn should_insert_oob_check(function: &Function, instruction: &Instruc
     }
 }
 
-pub(super) fn handle_array_get_group(
+/// Handle the case when an `ArrayGet` is potentially out-of-bounds and the array contains composite types
+/// by figuring out whether all `ArrayGet` of different parts of the complex item are unused, and if so
+/// then insert a single constraint to replace all of them.
+///
+/// Consumes all items from `possible_index_out_of_bounds_indexes` that belong to the current group and
+/// sets `next_out_of_bounds_index` to the *current* index, expecting that `replace_array_instructions_with_out_of_bounds_checks`
+/// will see that as a signal that the current index is out of bounds and it should insert a constraint.
+/// Then, the next a `ArrayGet`s in the group will be re-inserted, but they won't be treated as potentially
+/// OOB any more, and shall be removed in the next DIE pass as simply unused.
+fn handle_array_get_group(
     function: &Function,
+    // The array from which we are getting an item.
     array: &ValueId,
+    // Index of the current instruction. If it's not the same as `Some(next_out_of_bounds_index)`
+    // then this instruction was not unsafe.
     index: usize,
+    // The last index popped from `possible_index_out_of_bounds_indexes`.
     next_out_of_bounds_index: &mut Option<usize>,
+    // Remaining out of bounds indexes, all of which are unused.
     possible_index_out_of_bounds_indexes: &mut Vec<usize>,
+    // All the instructions in this block.
+    instructions: &[InstructionId],
 ) {
     if function.dfg.try_get_array_length(*array).is_none() {
         // Nothing to do for slices
@@ -195,7 +212,11 @@ pub(super) fn handle_array_get_group(
     // That means that after this instructions, (element_size - 1) instructions will be
     // part of this composite array get, and they'll be two instructions apart.
     //
-    // Now three things can happen:
+    // However, that is only true for the initial SSA. After we run DIE, it might remove
+    // some of the instructions that were unused, leaving the ones which had uses, destroying
+    // the group, so in general we cannot assume to see all element_size instruction to be present.
+    //
+    // Assuming we have identified a group, three things can happen:
     // a) none of the array_get instructions are unused: in this case they won't be in
     //    `possible_index_out_of_bounds_indexes` and they won't be removed, nothing to do here
     // b) all of the array_get instructions are unused: in this case we can replace **all**
@@ -208,7 +229,6 @@ pub(super) fn handle_array_get_group(
     // To check in which scenario we are we can get from `possible_index_out_of_bounds_indexes`
     // (starting from `next_out_of_bounds_index`) while we are in the group ranges
     // (1..=5 in the example above)
-
     let Some(out_of_bounds_index) = *next_out_of_bounds_index else {
         // No next unused instruction, so this is case a) and nothing needs to be done here
         return;
@@ -220,39 +240,76 @@ pub(super) fn handle_array_get_group(
         return;
     }
 
-    // What's the last instruction that's part of the group? (5 in the example above)
-    let last_instruction_index = index + 2 * (element_size - 1);
-    // How many unused instructions are in this group?
+    // Initially we would expect the last index of the group (5 in the example above)
+    // to be `index + 2 * (element_size - 1)`, however, we can't expect this to hold
+    // after previous DIE passes have partially removed the group.
+    let last_possible_index = index + 2 * (element_size - 1);
+    // Instead we need to check how many `ArrayGet` and `Add` we have following this
+    // instruction that read the same array, and how many of these instructions are unused.
+    let max_index = last_possible_index.min(instructions.len() - 1);
+
+    // How many unused instructions are in this group? We know the current instruction is unused.
     let mut unused_count = 1;
-    loop {
-        *next_out_of_bounds_index = possible_index_out_of_bounds_indexes.pop();
-        if let Some(out_of_bounds_index) = *next_out_of_bounds_index {
-            if out_of_bounds_index <= last_instruction_index {
-                unused_count += 1;
-                if unused_count == element_size {
-                    // We are in case b): we need to insert just one constrain.
-                    // Since we popped all of the group indexes, and given that we
-                    // are analyzing the first instruction in the group, we can
-                    // set `next_out_of_bounds_index` to the current index:
-                    // then a check will be inserted, and no other check will be
-                    // inserted for the rest of the group.
-                    *next_out_of_bounds_index = Some(index);
+    let mut group_count = 1;
+
+    for (i, next_id) in instructions.iter().enumerate().take(max_index + 1).skip(index + 1) {
+        let next_instruction = &function.dfg[*next_id];
+        match next_instruction {
+            // Skip `Add`
+            Instruction::Binary(Binary { operator: BinaryOp::Add { .. }, .. }) => {
+                continue;
+            }
+            Instruction::ArrayGet { array: next_array, index: next_index }
+                if next_array == array =>
+            {
+                // Still reading the same array.
+                // There is a chance that *this* instruction is safe, which means the one before it
+                // needs to be replaced with a constraint, even if this does not.
+                if function.dfg.is_safe_index(*next_index, *next_array) {
                     break;
-                } else {
+                }
+                // This instruction is also OOB, so it belongs to the same group.
+                group_count += 1;
+                // Check if this result is also unused.
+                *next_out_of_bounds_index = possible_index_out_of_bounds_indexes.pop();
+                let Some(out_of_bounds_index) = *next_out_of_bounds_index else {
+                    // This ArrayGet is not recorded as a potential OOB; we know it's OOB, so this means it's not unused.
+                    // That means we can let the built-in OOB check take care of it.
+                    break;
+                };
+                if out_of_bounds_index == i {
+                    unused_count += 1;
                     continue;
+                } else {
+                    // The next OOB index is for some other array, not this one; the last array get
+                    // reading this array is not OOB or not unused.
+                    break;
                 }
             }
+            _ => {
+                // Some other instruction that doesn't belong to the group.
+                break;
+            }
         }
+    }
 
+    if unused_count == group_count {
+        // We are in case b): we need to insert just one constrain.
+        // Since we popped all of the group indexes, and given that we
+        // are analyzing the first instruction in the group, we can
+        // set `next_out_of_bounds_index` to the current index:
+        // then a check will be inserted, and no other check will be
+        // inserted for the rest of the group.
+        *next_out_of_bounds_index = Some(index);
+    } else {
         // We are in case c): some of the instructions are unused.
         // We don't need to insert any checks, and given that we already popped
         // all of the indexes in the group, there's nothing else to do here.
-        break;
     }
 }
 
-// Given `lhs` and `rhs` values, if there's a side effects condition this will
-// return (`lhs * condition`, `rhs * condition`), otherwise just (`lhs`, `rhs`)
+/// Given `lhs` and `rhs` values, if there's a side effects condition this will
+/// return (`lhs * condition`, `rhs * condition`), otherwise just (`lhs`, `rhs`)
 fn apply_side_effects(
     side_effects_condition: Option<ValueId>,
     lhs: ValueId,
```

### test_programs/execution_failure/regression_9851/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "regression_9851"
+type = "bin"
+authors = [""]
+
+[dependencies]
\ No newline at end of file
```

### test_programs/execution_failure/regression_9851/src/main.nr
```diff
@@ -0,0 +1,7 @@
+fn main() -> pub bool {
+    let mut _b = {
+        let g: [(bool, str<2>); 1] = { [(false, "KO")] };
+        g[10].0
+    };
+    true
+}
```
