# [?] fix(ssa): Remove OOB checks inserted during DIE (#7995)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-04-11
Source: https://github.com/noir-lang/noir/commit/d5cc0e23c2ab601d0f10b42ae819b2187c070811
Type: security-commit

## Details
fix(ssa): Remove OOB checks inserted during DIE (#7995)

Co-authored-by: Tom French <15848336+TomAFrench@users.noreply.github.com>

## Patch
### compiler/noirc_evaluator/src/ssa/opt/die.rs
```diff
@@ -7,12 +7,11 @@ use rayon::iter::{IntoParallelRefMutIterator, ParallelIterator};
 use crate::ssa::{
     ir::{
         basic_block::{BasicBlock, BasicBlockId},
-        call_stack::CallStackId,
         dfg::DataFlowGraph,
         function::Function,
         instruction::{BinaryOp, Instruction, InstructionId, Intrinsic},
         post_order::PostOrder,
-        types::{NumericType, Type},
+        types::Type,
         value::{Value, ValueId},
     },
     ssa_gen::Ssa,
@@ -41,7 +40,7 @@ impl Ssa {
             .functions
             .par_iter_mut()
             .filter_map(|(id, func)| {
-                let set = func.dead_instruction_elimination(true, flattened, skip_brillig);
+                let set = func.dead_instruction_elimination(flattened, skip_brillig);
                 if func.runtime().is_brillig() { Some((*id, set)) } else { None }
             })
             .collect();
@@ -80,7 +79,6 @@ impl Function {
     /// After processing all functions, the union of these sets enables determining the unused globals.
     pub(crate) fn dead_instruction_elimination(
         &mut self,
-        insert_out_of_bounds_checks: bool,
         flattened: bool,
         skip_brillig: bool,
     ) -> HashSet<ValueId> {
@@ -96,22 +94,9 @@ impl Function {
             context.mark_used_instruction_results(&self.dfg, call_data.array_id);
         }
 
-        let mut inserted_out_of_bounds_checks = false;
-
         let blocks = PostOrder::with_function(self);
         for block in blocks.as_slice() {
-            inserted_out_of_bounds_checks |= context.remove_unused_instructions_in_block(
-                self,
-                *block,
-                insert_out_of_bounds_checks,
-            );
-        }
-
-        // If we inserted out of bounds check, let's run the pass again with those new
-        // instructions (we don't want to remove those checks, or instructions that are
-        // dependencies of those checks)
-        if inserted_out_of_bounds_checks {
-            return self.dead_instruction_elimination(false, flattened, skip_brillig);
+            context.remove_unused_instructions_in_block(self, *block);
         }
 
         context.remove_rc_instructions(&mut self.dfg);
@@ -152,51 +137,23 @@ impl Context {
     /// values set. This allows DIE to identify whole chains of unused instructions. (If the
     /// values referenced by an unused instruction were considered to be used, only the head of
     /// such chains would be removed.)
-    ///
-    /// If `insert_out_of_bounds_checks` is true and there are unused ArrayGet/ArraySet that
-    /// might be out of bounds, this method will insert out of bounds checks instead of
-    /// removing unused instructions and return `true`. The idea then is to later call this
-    /// function again with `insert_out_of_bounds_checks` set to false to effectively remove
-    /// unused instructions but leave the out of bounds checks.
     fn remove_unused_instructions_in_block(
         &mut self,
         function: &mut Function,
         block_id: BasicBlockId,
-        insert_out_of_bounds_checks: bool,
-    ) -> bool {
+    ) {
         let block = &function.dfg[block_id];
         self.mark_terminator_values_as_used(function, block);
 
         self.rc_tracker.new_block();
         self.rc_tracker.mark_terminator_arrays_as_used(function, block);
 
-        let instructions_len = block.instructions().len();
-
-        // Indexes of instructions that might be out of bounds.
-        // We'll remove those, but before that we'll insert bounds checks for them.
-        let mut possible_index_out_of_bounds_indexes = Vec::new();
-
         // Going in reverse so we know if a result of an instruction was used.
-        for (instruction_index, instruction_id) in block.instructions().iter().rev().enumerate() {
+        for instruction_id in block.instructions().iter().rev() {
             let instruction = &function.dfg[*instruction_id];
 
             if self.is_unused(*instruction_id, function) {
                 self.instructions_to_remove.insert(*instruction_id);
-
-                if insert_out_of_bounds_checks
-                    && instruction_might_result_in_out_of_bounds(function, instruction)
-                {
-                    possible_index_out_of_bounds_indexes
-                        .push(instructions_len - instruction_index - 1);
-
-                    // We need to still mark the array index as used as we refer to it in the inserted bounds check.
-                    let (Instruction::ArrayGet { index, .. } | Instruction::ArraySet { index, .. }) =
-                        instruction
-                    else {
-                        unreachable!("Only enter this branch on array gets/sets")
-                    };
-                    self.mark_used_instruction_results(&function.dfg, *index);
-                }
             } else {
                 // We can't remove rc instructions if they're loaded from a reference
                 // since we'd have no way of knowing whether the reference is still used.
@@ -214,26 +171,10 @@ impl Context {
 
         self.instructions_to_remove.extend(self.rc_tracker.get_non_mutated_arrays(&function.dfg));
         self.instructions_to_remove.extend(self.rc_tracker.rc_pairs_to_remove.drain());
-        // If there are some instructions that might trigger an out of bounds error,
-        // first add constrain checks. Then run the DIE pass again, which will remove those
-        // but leave the constrains (any any value needed by those constrains)
-        if !possible_index_out_of_bounds_indexes.is_empty() {
-            let inserted_check = self.replace_array_instructions_with_out_of_bounds_checks(
-                function,
-                block_id,
-                &mut possible_index_out_of_bounds_indexes,
-            );
-            // There's a slight chance we didn't insert any checks, so we could proceed with DIE.
-            if inserted_check {
-                return true;
-            }
-        }
 
         function.dfg[block_id]
             .instructions_mut()
             .retain(|instruction| !self.instructions_to_remove.contains(instruction));
-
-        false
     }
 
     /// Returns true if an instruction can be removed.
@@ -318,127 +259,6 @@ impl Context {
         }
     }
 
-    /// Replaces unused ArrayGet/ArraySet instructions with out of bounds checks.
-    /// Returns `true` if at least one check was inserted.
-    /// Because some ArrayGet might happen in groups (for composite types), if just
-    /// some of the instructions in a group are used but not all of them, no check
-    /// is inserted, so this method might return `false`.
-    fn replace_array_instructions_with_out_of_bounds_checks(
-        &mut self,
-        function: &mut Function,
-        block_id: BasicBlockId,
-        possible_index_out_of_bounds_indexes: &mut Vec<usize>,
-    ) -> bool {
-        let mut inserted_check = false;
-
-        // Keep track of the current side effects condition
-        let mut side_effects_condition = None;
-
-        // Keep track of the next index we need to handle
-        let mut next_out_of_bounds_index = possible_index_out_of_bounds_indexes.pop();
-
-        let instructions = function.dfg[block_id].take_instructions();
-        for (index, instruction_id) in instructions.iter().enumerate() {
-            let instruction_id = *instruction_id;
-            let instruction = &function.dfg[instruction_id];
-
-            if let Instruction::EnableSideEffectsIf { condition } = instruction {
-                side_effects_condition = Some(*condition);
-
-                // We still need to keep the EnableSideEffects instruction
-                function.dfg[block_id].instructions_mut().push(instruction_id);
-                continue;
-            };
-
-            // If it's an ArrayGet we'll deal with groups of it in case the array type is a composite type,
-            // and adjust `next_out_of_bounds_index` and `possible_index_out_of_bounds_indexes` accordingly
-            if let Instruction::ArrayGet { array, .. } = instruction {
-                handle_array_get_group(
-                    function,
-                    array,
-                    index,
-                    &mut next_out_of_bounds_index,
-                    possible_index_out_of_bounds_indexes,
-                );
-            }
-
-            let Some(out_of_bounds_index) = next_out_of_bounds_index else {
-                // No more out of bounds instructions to insert, just push the current instruction
-                function.dfg[block_id].instructions_mut().push(instruction_id);
-                continue;
-            };
-
-            if index != out_of_bounds_index {
-                // This instruction is not out of bounds: let's just push it
-                function.dfg[block_id].instructions_mut().push(instruction_id);
-                continue;
-            }
-
-            // This is an instruction that might be out of bounds: let's add a constrain.
-            let (array, index) = match instruction {
-                Instruction::ArrayGet { array, index }
-                | Instruction::ArraySet { array, index, .. } => (array, index),
-                _ => panic!("Expected an ArrayGet or ArraySet instruction here"),
-            };
-
-            let call_stack = function.dfg.get_instruction_call_stack_id(instruction_id);
-
-            let (lhs, rhs) = if function.dfg.get_numeric_constant(*index).is_some() {
-                // If we are here it means the index is known but out of bounds. That's always an error!
-                let false_const = function.dfg.make_constant(false.into(), NumericType::bool());
-                let true_const = function.dfg.make_constant(true.into(), NumericType::bool());
-                (false_const, true_const)
-            } else {
-                // `index` will be relative to the flattened array length, so we need to take that into account
-                let array_length = function.dfg.type_of_value(*array).flattened_size();
-
-                // If we are here it means the index is dynamic, so let's add a check that it's less than length
-                let length_type = NumericType::length_type();
-                let index = function.dfg.insert_instruction_and_results(
-                    Instruction::Cast(*index, length_type),
-                    block_id,
-                    None,
-                    call_stack,
-                );
-                let index = index.first();
-
-                let array_length =
-                    function.dfg.make_constant((array_length as u128).into(), length_type);
-                let is_index_out_of_bounds = function.dfg.insert_instruction_and_results(
-                    Instruction::binary(BinaryOp::Lt, index, array_length),
-                    block_id,
-                    None,
-                    call_stack,
-                );
-                let is_index_out_of_bounds = is_index_out_of_bounds.first();
-                let true_const = function.dfg.make_constant(true.into(), NumericType::bool());
-                (is_index_out_of_bounds, true_const)
-            };
-
-            let (lhs, rhs) = apply_side_effects(
-                side_effects_condition,
-                lhs,
-                rhs,
-                function,
-                block_id,
-                call_stack,
-            );
-
-            let message = Some("Index out of bounds".to_owned().into());
-            function.dfg.insert_instruction_and_results(
-                Instruction::Constrain(lhs, rhs, message),
-                block_id,
-                None,
-                call_stack,
-            );
-            inserted_check = true;
-
-            next_out_of_bounds_index = possible_index_out_of_bounds_indexes.pop();
-        }
-
-        inserted_check
-    }
-
     /// True if this is a `Instruction::IncrementRc` or `Instruction::DecrementRc`
     /// operating on an array directly from a `Instruction::MakeArray` or an
     /// intrinsic known to return a fresh array.
@@ -532,164 +352,6 @@ fn can_be_eliminated_if_unused(
     }
 }
 
-fn instruction_might_result_in_out_of_bounds(
-    function: &Function,
-    instruction: &Instruction,
-) -> bool {
-    use Instruction::*;
-    match instruction {
-        ArrayGet { array, index } | ArraySet { array, index, .. } => {
-            if function.dfg.try_get_array_length(*array).is_some() {
-                if let Some(known_index) = function.dfg.get_numeric_constant(*index) {
-                    // `index` will be relative to the flattened array length, so we need to take that into account
-                    let typ = function.dfg.type_of_value(*array);
-                    let array_length = typ.flattened_size();
-                    known_index >= array_length.into()
-                } else {
-                    // A dynamic index might always be out of bounds
-                    true
-                }
-            } else {
-                // Slice operations might be out of bounds, but there's no way we
-                // can insert a check because we don't know a slice's length
-                false
-            }
-        }
-        _ => false,
-    }
-}
-
-fn handle_array_get_group(
-    function: &Function,
-    array: &ValueId,
-    index: usize,
-    next_out_of_bounds_index: &mut Option<usize>,
-    possible_index_out_of_bounds_indexes: &mut Vec<usize>,
-) {
-    if function.dfg.try_get_array_length(*array).is_none() {
-        // Nothing to do for slices
-        return;
-    };
-
-    let element_size = function.dfg.type_of_value(*array).element_size();
-    if element_size <= 1 {
-        // Not a composite type
-        return;
-    };
-
-    // It's a composite type.
-    // When doing ArrayGet on a composite type, this **always** results in instructions like these
-    // (assuming element_size == 3):
-    //
-    // 1.    v27 = array_get v1, index v26
-    // 2.    v28 = add v26, u32 1
-    // 3.    v29 = array_get v1, index v28
-    // 4.    v30 = add v26, u32 2
-    // 5.    v31 = array_get v1, index v30
-    //
-    // That means that after this instructions, (element_size - 1) instructions will be
-    // part of this composite array get, and they'll be two instructions apart.
-    //
-    // Now three things can happen:
-    // a) none of the array_get instructions are unused: in this case they won't be in
-    //    `possible_index_out_of_bounds_indexes` and they won't be removed, nothing to do here
-    // b) all of the array_get instructions are unused: in this case we can replace **all**
-    //    of them with just one constrain: no need to do one per array_get
-    // c) some of the array_get instructions are unused, but not all: in this case
-    //    we don't need to insert any constrain, because on a later stage array bound checks
-    //    will be performed anyway. We'll let DIE remove the unused ones, without replacing
-    //    them with bounds checks, and leave the used ones.
-    //
-    // To check in which scenario we are we can get from `possible_index_out_of_bounds_indexes`
-    // (starting from `next_out_of_bounds_index`) while we are in the group ranges
-    // (1..=5 in the example above)
-
-    let Some(out_of_bounds_index) = *next_out_of_bounds_index else {
-        // No next unused instruction, so this is case a) and nothing needs to be done here
-        return;
-    };
-
-    if index != out_of_bounds_index {
-        // The next index is not the one for the current instructions,
-        // so we are in case a), and nothing needs to be done here
-        return;
-    }
-
-    // What's the last instruction that's part of the group? (5 in the example above)
-    let last_instruction_index = index + 2 * (element_size - 1);
-    // How many unused instructions are in this group?
-    let mut unused_count = 1;
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
-                    break;
-                } else {
-                    continue;
-                }
-            }
-        }
-
-        // We are in case c): some of the instructions are unused.
-        // We don't need to insert any checks, and given that we already popped
-        // all of the indexes in the group, there's nothing else to do here.
-        break;
-    }
-}
-
-// Given `lhs` and `rhs` values, if there's a side effects condition this will
-// return (`lhs * condition`, `rhs * condition`), otherwise just (`lhs`, `rhs`)
-fn apply_side_effects(
-    side_effects_condition: Option<ValueId>,
-    lhs: ValueId,
-    rhs: ValueId,
-    function: &mut Function,
-    block_id: BasicBlockId,
-    call_stack: CallStackId,
-) -> (ValueId, ValueId) {
-    // See if there's an active "enable side effects" condition
-    let Some(condition) = side_effects_condition else {
-        return (lhs, rhs);
-    };
-
-    let dfg = &mut function.dfg;
-
-    // Condition needs to be cast to argument type in order to multiply them together.
-    // In our case, lhs is always a boolean.
-    let cast = Instruction::Cast(condition, NumericType::bool());
-    let casted_condition = dfg.insert_instruction_and_results(cast, block_id, None, call_stack);
-    let casted_condition = casted_condition.first();
-
-    // Unchecked mul because the side effects var is always 0 or 1
-    let lhs = dfg.insert_instruction_and_results(
-        Instruction::binary(BinaryOp::Mul { unchecked: true }, lhs, casted_condition),
-        block_id,
-        None,
-        call_stack,
-    );
-    let lhs = lhs.first();
-
-    // Unchecked mul because the side effects var is always 0 or 1
-    let rhs = dfg.insert_instruction_and_results(
-        Instruction::binary(BinaryOp::Mul { unchecked: true }, rhs, casted_condition),
-        block_id,
-        None,
-        call_stack,
-    );
-    let rhs = rhs.first();
-
-    (lhs, rhs)
-}
-
 #[derive(Default)]
 /// Per block RC tracker.
 struct RcTracker {
@@ -1227,61 +889,4 @@ mod test {
         }
         ");
     }
-
-    #[test]
-    fn correctly_handles_chains_of_array_gets() {
-        //! This test checks that if there's a chain of `array_get` instructions which use the result of the previous
-        //! read as the index of the next `array_get`, we only replace the final `array_get` and do not propagate
-        //! up the chain. Otherwise we remove instructions for which the instructions are still used.
-
-        // SSA generated from `compile_success_empty/regression_7785` (slightly modified)
-        let src = "
-        acir(inline) predicate_pure fn main f0 {
-          b0():
-            v1 = call f1() -> u32
-            v3 = make_array [u32 0, u32 0] : [u32; 2]
-            v4 = array_get v3, index v1 -> u32
-            v5 = array_get v3, index v4 -> u32
-            return
-        }
-        brillig(inline) predicate_pure fn inject_value f1 {
-          b0():
-            return u32 0
-        }
-        ";
-        let ssa = Ssa::from_str(src).unwrap();
-
-        let ssa = ssa.dead_instruction_elimination();
-
-        // Previously this would produce the SSA:
-        //
-        // acir(inline) predicate_pure fn main f0 {
-        //   b0():
-        //     v1 = call f1() -> u32
-        //     v3 = lt v1, u32 2
-        //     constrain v3 == u1 1, "Index out of bounds"
-        //     v5 = lt v4, u32 2  <-- Notice that `v4` has now been orphaned
-        //     constrain v5 == u1 1, "Index out of bounds"
-        //     return
-        //   }
-        // brillig(inline) predicate_pure fn inject_value f1 {
-        //   b0():
-        //     return u32 0
-        // }
-        assert_ssa_snapshot!(ssa, @r#"
-        acir(inline) predicate_pure fn main f0 {
-          b0():
-            v1 = call f1() -> u32
-            v3 = make_array [u32 0, u32 0] : [u32; 2]
-            v4 = array_get v3, index v1 -> u32
-            v6 = lt v4, u32 2
-            constrain v6 == u1 1, "Index out of bounds"
-            return
-        }
-        brillig(inline) predicate_pure fn inject_value f1 {
-          b0():
-            return u32 0
-        }
-        "#);
-    }
 }
```

### compiler/noirc_evaluator/src/ssa/opt/preprocess_fns.rs
```diff
@@ -59,7 +59,7 @@ impl Ssa {
             // Try to reduce the number of blocks.
             function.simplify_function();
             // Remove leftover instructions.
-            function.dead_instruction_elimination(true, false, false);
+            function.dead_instruction_elimination(false, false);
 
             // Put it back into the SSA, so the next functions can pick it up.
             self.functions.insert(id, function);
```

### compiler/noirc_evaluator/src/ssa/ssa_gen/context.rs
```diff
@@ -868,12 +868,34 @@ impl<'a> FunctionContext<'a> {
         match lvalue {
             LValue::Ident => unreachable!("Cannot assign to a variable without a reference"),
             LValue::Index { old_array: mut array, index, array_lvalue, location } => {
+                let array_type = &self.builder.type_of_value(array);
+
+                // Checks for index Out-of-bounds
+                match array_type {
+                    Type::Array(_, len) => {
+                        let len =
+                            self.builder.numeric_constant(*len as u128, NumericType::length_type());
+                        self.codegen_access_check(index, len);
+                    }
+                    _ => unreachable!("must have array or slice but got {array_type}"),
+                }
+
                 array = self.assign_lvalue_index(new_value, array, index, location);
                 self.assign_new_value(*array_lvalue, array.into());
             }
             LValue::SliceIndex { old_slice: slice, index, slice_lvalue, location } => {
                 let mut slice_values = slice.into_value_list(self);
 
+                let array_type = &self.builder.type_of_value(slice_values[1]);
+
+                // Checks for index Out-of-bounds
+                match array_type {
+                    Type::Slice(_) => {
+                        self.codegen_access_check(index, slice_values[0]);
+                    }
+                    _ => unreachable!("must have array or slice but got {array_type}"),
+                }
+
                 slice_values[1] =
                     self.assign_lvalue_index(new_value, slice_values[1], index, location);
 
```

### test_programs/execution_success/array_oob_regression_7952/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "array_oob_regression_7952"
+type = "bin"
+authors = [""]
+
+[dependencies]
\ No newline at end of file
```

### test_programs/execution_success/array_oob_regression_7952/Prover.toml
```diff
@@ -0,0 +1,2 @@
+a = [[]]
+b = 1
\ No newline at end of file
```

### test_programs/execution_success/array_oob_regression_7952/src/main.nr
```diff
@@ -0,0 +1,7 @@
+fn main(a: [[u32; 0]; 1], b: bool) -> pub [u32; 0] {
+    if (b) {
+        a[0]
+    } else {
+        a[0]
+    }
+}
```

### test_programs/execution_success/array_oob_regression_7952/stdout.txt
```diff
@@ -0,0 +1 @@
+[array_oob_regression_7952] Circuit output: Vec([])
\ No newline at end of file
```

### test_programs/execution_success/array_oob_regression_7965/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "array_oob_regression_7965"
+type = "bin"
+authors = [""]
+
+[dependencies]
\ No newline at end of file
```

### test_programs/execution_success/array_oob_regression_7965/Prover.toml
```diff
@@ -0,0 +1,2 @@
+a = 1
+b = [[0, 1, 0, "\\\t"], [0, 1, 1, "mp"], [0, 0, 0, "\t/"], [0, 0, 0, "ab"]]
\ No newline at end of file
```

### test_programs/execution_success/array_oob_regression_7965/src/main.nr
```diff
@@ -0,0 +1,9 @@
+global G_A: [[bool; 0]; 2] = [[], []];
+
+fn main(a: bool, b: [(u1, bool, u1, str<2>); 4]) -> pub [bool; 0] {
+    if (a) {
+        G_A[((((b[0].0 as u8) + (b[0].0 as u8)) as u32) % 2)]
+    } else {
+        G_A[((((b[0].0 as u8) + (b[0].0 as u8)) as u32) % 2)]
+    }
+}
```

### test_programs/execution_success/array_oob_regression_7965/stdout.txt
```diff
@@ -0,0 +1 @@
+[array_oob_regression_7965] Circuit output: Vec([])
\ No newline at end of file
```

### test_programs/execution_success/array_oob_regression_7975/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "array_oob_regression_7975"
+type = "bin"
+authors = [""]
+
+[dependencies]
\ No newline at end of file
```
