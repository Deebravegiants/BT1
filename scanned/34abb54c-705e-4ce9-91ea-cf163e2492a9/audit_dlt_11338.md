# [?] fix: Replace unused ArrayGet/Set with constrain if possibly out of bounds (#5691)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-08-13
Source: https://github.com/noir-lang/noir/commit/a87d92629c49c91d47685dba9a2a6dce4440756d
Type: security-commit

## Details
fix: Replace unused ArrayGet/Set with constrain if possibly out of bounds (#5691)

# Description

## Problem

For #5296

## Summary

In DIE, when we find an `ArrayGet/Set` that we could remove, if that
instruction might be an index out of bounds we still remove it but leave
a constrain check too.

## Additional Context

For now the code is a bit messy, I just wanted to get it working first.

Also, it's not working for slices yet because we can't insert out of
bounds checks if we don't know the slice length. For that we'll need to
add the checks like we do for `ArrayGet` for slice (this could be done
in a separate PR, though).

## Documentation\*

Check one:
- [x] No documentation needed.
- [ ] Documentation included in this PR.
- [ ] **[For Experimental Features]** Documentation to be submitted in a
separate PR.

# PR Checklist\*

- [x] I have tested the changes locally.
- [x] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

## Patch
### compiler/noirc_evaluator/src/ssa/opt/die.rs
```diff
@@ -2,16 +2,20 @@
 //! which the results are unused.
 use std::collections::HashSet;
 
+use im::Vector;
+use noirc_errors::Location;
+
 use crate::ssa::{
     ir::{
         basic_block::{BasicBlock, BasicBlockId},
         dfg::DataFlowGraph,
         function::Function,
-        instruction::{Instruction, InstructionId, Intrinsic},
+        instruction::{BinaryOp, Instruction, InstructionId, Intrinsic},
         post_order::PostOrder,
+        types::Type,
         value::{Value, ValueId},
     },
-    ssa_gen::Ssa,
+    ssa_gen::{Ssa, SSA_WORD_SIZE},
 };
 
 impl Ssa {
@@ -20,7 +24,7 @@ impl Ssa {
     #[tracing::instrument(level = "trace", skip(self))]
     pub(crate) fn dead_instruction_elimination(mut self) -> Ssa {
         for function in self.functions.values_mut() {
-            dead_instruction_elimination(function);
+            dead_instruction_elimination(function, true);
         }
         self
     }
@@ -32,16 +36,29 @@ impl Ssa {
 /// instructions that reference results from an instruction in another block are evaluated first.
 /// If we did not iterate blocks in this order we could not safely say whether or not the results
 /// of its instructions are needed elsewhere.
-fn dead_instruction_elimination(function: &mut Function) {
+fn dead_instruction_elimination(function: &mut Function, insert_out_of_bounds_checks: bool) {
     let mut context = Context::default();
     for call_data in &function.dfg.data_bus.call_data {
         context.mark_used_instruction_results(&function.dfg, call_data.array_id);
     }
 
-    let blocks = PostOrder::with_function(function);
+    let mut inserted_out_of_bounds_checks = false;
 
+    let blocks = PostOrder::with_function(function);
     for block in blocks.as_slice() {
-        context.remove_unused_instructions_in_block(function, *block);
+        inserted_out_of_bounds_checks |= context.remove_unused_instructions_in_block(
+            function,
+            *block,
+            insert_out_of_bounds_checks,
+        );
+    }
+
+    // If we inserted out of bounds check, let's run the pass again with those new
+    // instructions (we don't want to remove those checks, or instructions that are
+    // dependencies of those checks)
+    if inserted_out_of_bounds_checks {
+        dead_instruction_elimination(function, false);
+        return;
     }
 
     context.remove_rc_instructions(&mut function.dfg);
@@ -71,20 +88,40 @@ impl Context {
     /// values set. This allows DIE to identify whole chains of unused instructions. (If the
     /// values referenced by an unused instruction were considered to be used, only the head of
     /// such chains would be removed.)
+    ///
+    /// If `insert_out_of_bounds_checks` is true and there are unused ArrayGet/ArraySet that
+    /// might be out of bounds, this method will insert out of bounds checks instead of
+    /// removing unused instructions and return `true`. The idea then is to later call this
+    /// function again with `insert_out_of_bounds_checks` set to false to effectively remove
+    /// unused instructions but leave the out of bounds checks.
     fn remove_unused_instructions_in_block(
         &mut self,
         function: &mut Function,
         block_id: BasicBlockId,
-    ) {
+        insert_out_of_bounds_checks: bool,
+    ) -> bool {
         let block = &function.dfg[block_id];
         self.mark_terminator_values_as_used(function, block);
 
-        for instruction_id in block.instructions().iter().rev() {
+        let instructions_len = block.instructions().len();
+
+        // Indexes of instructions that might be out of bounds.
+        // We'll remove those, but before that we'll insert bounds checks for them.
+        let mut possible_index_out_of_bounds_indexes = Vec::new();
+
+        for (instruction_index, instruction_id) in block.instructions().iter().rev().enumerate() {
+            let instruction = &function.dfg[*instruction_id];
+
             if self.is_unused(*instruction_id, function) {
                 self.instructions_to_remove.insert(*instruction_id);
-            } else {
-                let instruction = &function.dfg[*instruction_id];
 
+                if insert_out_of_bounds_checks
+                    && instruction_might_result_in_out_of_bounds(function, instruction)
+                {
+                    possible_index_out_of_bounds_indexes
+                        .push(instructions_len - instruction_index - 1);
+                }
+            } else {
                 use Instruction::*;
                 if matches!(instruction, IncrementRc { .. } | DecrementRc { .. }) {
                     self.rc_instructions.push((*instruction_id, block_id));
@@ -96,9 +133,26 @@ impl Context {
             }
         }
 
+        // If there are some instructions that might trigger an out of bounds error,
+        // first add constrain checks. Then run the DIE pass again, which will remove those
+        // but leave the constrains (any any value needed by those constrains)
+        if !possible_index_out_of_bounds_indexes.is_empty() {
+            let inserted_check = self.replace_array_instructions_with_out_of_bounds_checks(
+                function,
+                block_id,
+                &mut possible_index_out_of_bounds_indexes,
+            );
+            // There's a slight chance we didn't insert any checks, so we could proceed with DIE.
+            if inserted_check {
+                return true;
+            }
+        }
+
         function.dfg[block_id]
             .instructions_mut()
             .retain(|instruction| !self.instructions_to_remove.contains(instruction));
+
+        false
     }
 
     /// Returns true if an instruction can be removed.
@@ -166,6 +220,288 @@ impl Context {
             }
         }
     }
+
+    /// Replaces unused ArrayGet/ArraySet instructions with out of bounds checks.
+    /// Returns `true` if at least one check was inserted.
+    /// Because some ArrayGet might happen in groups (for composite types), if just
+    /// some of the instructions in a group are used but not all of them, no check
+    /// is inserted, so this method might return `false`.
+    fn replace_array_instructions_with_out_of_bounds_checks(
+        &mut self,
+        function: &mut Function,
+        block_id: BasicBlockId,
+        possible_index_out_of_bounds_indexes: &mut Vec<usize>,
+    ) -> bool {
+        let mut inserted_check = false;
+
+        // Keep track of the current side effects condition
+        let mut side_effects_condition = None;
+
+        // Keep track of the next index we need to handle
+        let mut next_out_of_bounds_index = possible_index_out_of_bounds_indexes.pop();
+
+        let instructions = function.dfg[block_id].take_instructions();
+        for (index, instruction_id) in instructions.iter().enumerate() {
+            let instruction_id = *instruction_id;
+            let instruction = &function.dfg[instruction_id];
+
+            if let Instruction::EnableSideEffects { condition } = instruction {
+                side_effects_condition = Some(*condition);
+
+                // We still need to keep the EnableSideEffects instruction
+                function.dfg[block_id].instructions_mut().push(instruction_id);
+                continue;
+            };
+
+            // If it's an ArrayGet we'll deal with groups of it in case the array type is a composite type,
+            // and adjust `next_out_of_bounds_index` and `possible_index_out_of_bounds_indexes` accordingly
+            if let Instruction::ArrayGet { array, .. } = instruction {
+                handle_array_get_group(
+                    function,
+                    array,
+                    index,
+                    &mut next_out_of_bounds_index,
+                    possible_index_out_of_bounds_indexes,
+                );
+            }
+
+            let Some(out_of_bounds_index) = next_out_of_bounds_index else {
+                // No more out of bounds instructions to insert, just push the current instruction
+                function.dfg[block_id].instructions_mut().push(instruction_id);
+                continue;
+            };
+
+            if index != out_of_bounds_index {
+                // This instruction is not out of bounds: let's just push it
+                function.dfg[block_id].instructions_mut().push(instruction_id);
+                continue;
+            }
+
+            // This is an instruction that might be out of bounds: let's add a constrain.
+            let (array, index) = match instruction {
+                Instruction::ArrayGet { array, index }
+                | Instruction::ArraySet { array, index, .. } => (array, index),
+                _ => panic!("Expected an ArrayGet or ArraySet instruction here"),
+            };
+
+            let call_stack = function.dfg.get_call_stack(instruction_id);
+
+            let (lhs, rhs) = if function.dfg.get_numeric_constant(*index).is_some() {
+                // If we are here it means the index is known but out of bounds. That's always an error!
+                let false_const = function.dfg.make_constant(false.into(), Type::bool());
+                let true_const = function.dfg.make_constant(true.into(), Type::bool());
+                (false_const, true_const)
+            } else {
+                // `index` will be relative to the flattened array length, so we need to take that into account
+                let array_length = function.dfg.type_of_value(*array).flattened_size();
+
+                // If we are here it means the index is dynamic, so let's add a check that it's less than length
+                let index = function.dfg.insert_instruction_and_results(
+                    Instruction::Cast(*index, Type::unsigned(SSA_WORD_SIZE)),
+                    block_id,
+                    None,
+                    call_stack.clone(),
+                );
+                let index = index.first();
+
+                let array_typ = Type::unsigned(SSA_WORD_SIZE);
+                let array_length =
+                    function.dfg.make_constant((array_length as u128).into(), array_typ);
+                let is_index_out_of_bounds = function.dfg.insert_instruction_and_results(
+                    Instruction::binary(BinaryOp::Lt, index, array_length),
+                    block_id,
+                    None,
+                    call_stack.clone(),
+                );
+                let is_index_out_of_bounds = is_index_out_of_bounds.first();
+                let true_const = function.dfg.make_constant(true.into(), Type::bool());
+                (is_index_out_of_bounds, true_const)
+            };
+
+            let (lhs, rhs) = apply_side_effects(
+                side_effects_condition,
+                lhs,
+                rhs,
+                function,
+                block_id,
+                call_stack.clone(),
+            );
+
+            let message = Some("Index out of bounds".to_owned().into());
+            function.dfg.insert_instruction_and_results(
+                Instruction::Constrain(lhs, rhs, message),
+                block_id,
+                None,
+                call_stack,
+            );
+            inserted_check = true;
+
+            next_out_of_bounds_index = possible_index_out_of_bounds_indexes.pop();
+        }
+
+        inserted_check
+    }
+}
+
+fn instruction_might_result_in_out_of_bounds(
+    function: &Function,
+    instruction: &Instruction,
+) -> bool {
+    use Instruction::*;
+    match instruction {
+        ArrayGet { array, index } | ArraySet { array, index, .. } => {
+            if function.dfg.try_get_array_length(*array).is_some() {
+                if let Some(known_index) = function.dfg.get_numeric_constant(*index) {
+                    // `index` will be relative to the flattened array length, so we need to take that into account
+                    let typ = function.dfg.type_of_value(*array);
+                    let array_length = typ.flattened_size();
+                    known_index >= array_length.into()
+                } else {
+                    // A dynamic index might always be out of bounds
+                    true
+                }
+            } else {
+                // Slice operations might be out of bounds, but there's no way we
+                // can insert a check because we don't know a slice's length
+                false
+            }
+        }
+        _ => false,
+    }
+}
+
+fn handle_array_get_group(
+    function: &Function,
+    array: &ValueId,
+    index: usize,
+    next_out_of_bounds_index: &mut Option<usize>,
+    possible_index_out_of_bounds_indexes: &mut Vec<usize>,
+) {
+    let Some(array_length) = function.dfg.try_get_array_length(*array) else {
+        // Nothing to do for slices
+        return;
+    };
+
+    let flattened_size = function.dfg.type_of_value(*array).flattened_size();
+    let element_size = flattened_size / array_length;
+    if element_size <= 1 {
+        // Not a composite type
+        return;
+    };
+
+    // It's a composite type.
+    // When doing ArrayGet on a composite type, this **always** results in instructions like these
+    // (assuming element_size == 3):
+    //
+    // 1.    v27 = array_get v1, index v26
+    // 2.    v28 = add v26, u32 1
+    // 3.    v29 = array_get v1, index v28
+    // 4.    v30 = add v26, u32 2
+    // 5.    v31 = array_get v1, index v30
+    //
+    // That means that after this instructions, (element_size - 1) instructions will be
+    // part of this composite array get, and they'll be two instructions apart.
+    //
+    // Now three things can happen:
+    // a) none of the array_get instructions are unused: in this case they won't be in
+    //    `possible_index_out_of_bounds_indexes` and they won't be removed, nothing to do here
+    // b) all of the array_get instructions are unused: in this case we can replace **all**
+    //    of them with just one constrain: no need to do one per array_get
+    // c) some of the array_get instructions are unused, but not all: in this case
+    //    we don't need to insert any constrain, because on a later stage array bound checks
+    //    will be performed anyway. We'll let DIE remove the unused ones, without replacing
+    //    them with bounds checks, and leave the used ones.
+    //
+    // To check in which scenario we are we can get from `possible_index_out_of_bounds_indexes`
+    // (starting from `next_out_of_bounds_index`) while we are in the group ranges
+    // (1..=5 in the example above)
+
+    let Some(out_of_bounds_index) = *next_out_of_bounds_index else {
+        // No next unused instruction, so this is case a) and nothing needs to be done here
+        return;
+    };
+
+    if index != out_of_bounds_index {
+        // The next index is not the one for the current instructions,
+        // so we are in case a), and nothing needs to be done here
+        return;
+    }
+
+    // What's the last instruction that's part of the group? (5 in the example above)
+    let last_instruction_index = index + 2 * (element_size - 1);
+    // How many unused instructions are in this group?
+    let mut unused_count = 1;
+    loop {
+        *next_out_of_bounds_index = possible_index_out_of_bounds_indexes.pop();
+        if let Some(out_of_bounds_index) = *next_out_of_bounds_index {
+            if out_of_bounds_index <= last_instruction_index {
+                unused_count += 1;
+                if unused_count == element_size {
+                    // We are in case b): we need to insert just one constrain.
+                    // Since we popped all of the group indexes, and given that we
+                    // are analyzing the first instruction in the group, we can
+                    // set `next_out_of_bounds_index` to the current index:
+                    // then a check will be inserted, and no other check will be
+                    // inserted for the rest of the group.
+                    *next_out_of_bounds_index = Some(index);
+                    break;
+                } else {
+                    continue;
+                }
+            }
+        }
+
+        // We are in case c): some of the instructions are unused.
+        // We don't need to insert any checks, and given that we already popped
+        // all of the indexes in the group, there's nothing else to do here.
+        break;
+    }
+}
+
+// Given `lhs` and `rhs` values, if there's a side effects condition this will
+// return (`lhs * condition`, `rhs * condition`), otherwise just (`lhs`, `rhs`)
+fn apply_side_effects(
+    side_effects_condition: Option<ValueId>,
+    lhs: ValueId,
+    rhs: ValueId,
+    function: &mut Function,
+    block_id: BasicBlockId,
+    call_stack: Vector<Location>,
+) -> (ValueId, ValueId) {
+    // See if there's an active "enable side effects" condition
+    let Some(condition) = side_effects_condition else {
+        return (lhs, rhs);
+    };
+
+    let dfg = &mut function.dfg;
+
+    // Condition needs to be cast to argument type in order to multiply them together.
+    // In our case, lhs is always a boolean.
+    let casted_condition = dfg.insert_instruction_and_results(
+        Instruction::Cast(condition, Type::bool()),
+        block_id,
+        None,
+        call_stack.clone(),
+    );
+    let casted_condition = casted_condition.first();
+
+    let lhs = dfg.insert_instruction_and_results(
+        Instruction::binary(BinaryOp::Mul, lhs, casted_condition),
+        block_id,
+        None,
+        call_stack.clone(),
+    );
+    let lhs = lhs.first();
+
+    let rhs = dfg.insert_instruction_and_results(
+        Instruction::binary(BinaryOp::Mul, rhs, casted_condition),
+        block_id,
+        None,
+        call_stack,
+    );
+    let rhs = rhs.first();
+
+    (lhs, rhs)
 }
 
 #[cfg(test)]
```

### test_programs/execution_failure/unused_array_get_known_index_out_of_bounds/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+[package]
+name = "unused_array_get_known_index_out_of_bounds"
+type = "bin"
+authors = [""]
+compiler_version = ">=0.31.0"
+
+[dependencies]
\ No newline at end of file
```

### test_programs/execution_failure/unused_array_get_known_index_out_of_bounds/src/main.nr
```diff
@@ -0,0 +1,4 @@
+fn main() {
+    let array = [1, 2, 3];
+    let _ = array[10]; // Index out of bounds
+}
```

### test_programs/execution_failure/unused_array_get_unknown_index_out_of_bounds/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+[package]
+name = "unused_array_get_unknown_index_out_of_bounds"
+type = "bin"
+authors = [""]
+compiler_version = ">=0.31.0"
+
+[dependencies]
\ No newline at end of file
```

### test_programs/execution_failure/unused_array_get_unknown_index_out_of_bounds/Prover.toml
```diff
@@ -0,0 +1 @@
+x = "10"
\ No newline at end of file
```

### test_programs/execution_failure/unused_array_get_unknown_index_out_of_bounds/src/main.nr
```diff
@@ -0,0 +1,4 @@
+fn main(x: Field) {
+    let array = [1, 2, 3];
+    let _ = array[x]; // Index out of bounds
+}
```

### test_programs/execution_failure/unused_array_set_known_index_out_of_bounds/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+[package]
+name = "unused_array_set_known_index_out_of_bounds"
+type = "bin"
+authors = [""]
+compiler_version = ">=0.31.0"
+
+[dependencies]
\ No newline at end of file
```

### test_programs/execution_failure/unused_array_set_known_index_out_of_bounds/src/main.nr
```diff
@@ -0,0 +1,4 @@
+fn main() {
+    let mut array = [1, 2, 3];
+    array[10] = 1; // Index out of bounds
+}
```

### test_programs/execution_failure/unused_array_set_unknown_index_out_of_bounds/Nargo.toml
```diff
@@ -0,0 +1,7 @@
+[package]
+name = "unused_array_set_unknown_index_out_of_bounds"
+type = "bin"
+authors = [""]
+compiler_version = ">=0.31.0"
+
+[dependencies]
\ No newline at end of file
```

### test_programs/execution_failure/unused_array_set_unknown_index_out_of_bounds/Prover.toml
```diff
@@ -0,0 +1 @@
+x = "10"
\ No newline at end of file
```
