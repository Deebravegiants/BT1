# [?] fix: Thread errors through remove_if_else instead of panicing when the value merger finds reference values (#8783)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-06-06
Source: https://github.com/noir-lang/noir/commit/c4a8746921bc5fd6fef8e6bdce6563ae8817b8c4
Type: security-commit

## Details
fix: Thread errors through remove_if_else instead of panicing when the value merger finds reference values (#8783)

## Patch
### compiler/noirc_evaluator/src/errors.rs
```diff
@@ -16,6 +16,8 @@ use thiserror::Error;
 use crate::ssa::ir::types::NumericType;
 use serde::{Deserialize, Serialize};
 
+pub type RtResult<T> = Result<T, RuntimeError>;
+
 #[derive(Debug, PartialEq, Eq, Clone, Error)]
 pub enum RuntimeError {
     #[error(transparent)]
@@ -64,6 +66,14 @@ pub enum RuntimeError {
         "Could not resolve some references to the array. All references must be resolved at compile time"
     )]
     UnknownReference { call_stack: CallStack },
+    #[error(
+        "Cannot return references from an if or match expression, or assignment within these expressions"
+    )]
+    ReturnedReferenceFromDynamicIf { call_stack: CallStack },
+    #[error(
+        "Cannot return a function from an if or match expression, or assignment within these expressions"
+    )]
+    ReturnedFunctionFromDynamicIf { call_stack: CallStack },
 }
 
 #[derive(Debug, Clone, Serialize, Deserialize, Hash)]
@@ -174,6 +184,8 @@ impl RuntimeError {
             | RuntimeError::UnconstrainedSliceReturnToConstrained { call_stack }
             | RuntimeError::UnconstrainedOracleReturnToConstrained { call_stack }
             | RuntimeError::UnknownReference { call_stack } => call_stack,
+            RuntimeError::ReturnedReferenceFromDynamicIf { call_stack } => call_stack,
+            RuntimeError::ReturnedFunctionFromDynamicIf { call_stack } => call_stack,
         }
     }
 }
```

### compiler/noirc_evaluator/src/ssa.rs
```diff
@@ -178,7 +178,7 @@ pub fn primary_passes(options: &SsaEvaluatorOptions) -> Vec<SsaPass> {
             move |ssa| ssa.inline_functions_with_no_predicates(options.inliner_aggressiveness),
             "Inlining",
         ),
-        SsaPass::new(Ssa::remove_if_else, "Remove IfElse"),
+        SsaPass::new_try(Ssa::remove_if_else, "Remove IfElse"),
         SsaPass::new(Ssa::purity_analysis, "Purity Analysis"),
         SsaPass::new(Ssa::fold_constants, "Constant Folding"),
         SsaPass::new(Ssa::flatten_basic_conditionals, "Simplify conditionals for unconstrained"),
```

### compiler/noirc_evaluator/src/ssa/ir/dfg/simplify/call.rs
```diff
@@ -519,12 +519,17 @@ fn simplify_slice_push_back(
 
     let mut value_merger = ValueMerger::new(dfg, block, &mut slice_sizes, call_stack);
 
-    let new_slice = value_merger.merge_values(
+    let Ok(new_slice) = value_merger.merge_values(
         len_not_equals_capacity,
         len_equals_capacity,
         set_last_slice_value,
         new_slice,
-    );
+    ) else {
+        // If we were to percolate up the error here, it'd get to insert_instruction and eventually
+        // all of ssa. Instead we just choose not to simplify the slice call since this should
+        // be a rare case.
+        return SimplifyResult::None;
+    };
 
     SimplifyResult::SimplifiedToMultiple(vec![new_slice_length, new_slice])
 }
```

### compiler/noirc_evaluator/src/ssa/opt/flatten_cfg.rs
```diff
@@ -1697,6 +1697,7 @@ mod test {
             .flatten_cfg()
             .mem2reg()
             .remove_if_else()
+            .unwrap()
             .fold_constants()
             .dead_instruction_elimination();
 
```

### compiler/noirc_evaluator/src/ssa/opt/flatten_cfg/value_merger.rs
```diff
@@ -2,12 +2,15 @@ use acvm::{FieldElement, acir::AcirField};
 use fxhash::FxHashMap as HashMap;
 use noirc_errors::call_stack::CallStackId;
 
-use crate::ssa::ir::{
-    basic_block::BasicBlockId,
-    dfg::DataFlowGraph,
-    instruction::{ArrayOffset, BinaryOp, Instruction},
-    types::{NumericType, Type},
-    value::ValueId,
+use crate::{
+    errors::{RtResult, RuntimeError},
+    ssa::ir::{
+        basic_block::BasicBlockId,
+        dfg::DataFlowGraph,
+        instruction::{ArrayOffset, BinaryOp, Instruction},
+        types::{NumericType, Type},
+        value::ValueId,
+    },
 };
 
 pub(crate) struct ValueMerger<'a> {
@@ -45,28 +48,36 @@ impl<'a> ValueMerger<'a> {
         else_condition: ValueId,
         then_value: ValueId,
         else_value: ValueId,
-    ) -> ValueId {
+    ) -> RtResult<ValueId> {
         if then_value == else_value {
-            return then_value;
+            return Ok(then_value);
         }
 
         match self.dfg.type_of_value(then_value) {
-            Type::Numeric(_) => Self::merge_numeric_values(
+            Type::Numeric(_) => Ok(Self::merge_numeric_values(
                 self.dfg,
                 self.block,
                 then_condition,
                 else_condition,
                 then_value,
                 else_value,
-            ),
+            )),
             typ @ Type::Array(_, _) => {
                 self.merge_array_values(typ, then_condition, else_condition, then_value, else_value)
             }
             typ @ Type::Slice(_) => {
                 self.merge_slice_values(typ, then_condition, else_condition, then_value, else_value)
             }
-            Type::Reference(_) => panic!("Cannot return references from an if expression"),
-            Type::Function => panic!("Cannot return functions from an if expression"),
+            Type::Reference(_) => {
+                // FIXME: none of then_value, else_value, then_condition, or else_condition have
+                // non-empty call stacks
+                let call_stack = self.dfg.get_value_call_stack(then_value);
+                Err(RuntimeError::ReturnedReferenceFromDynamicIf { call_stack })
+            }
+            Type::Function => {
+                let call_stack = self.dfg.get_value_call_stack(then_value);
+                Err(RuntimeError::ReturnedFunctionFromDynamicIf { call_stack })
+            }
         }
     }
 
@@ -130,7 +141,7 @@ impl<'a> ValueMerger<'a> {
         else_condition: ValueId,
         then_value: ValueId,
         else_value: ValueId,
-    ) -> ValueId {
+    ) -> Result<ValueId, RuntimeError> {
         let mut merged = im::Vector::new();
 
         let (element_types, len) = match &typ {
@@ -162,14 +173,14 @@ impl<'a> ValueMerger<'a> {
                     else_condition,
                     then_element,
                     else_element,
-                ));
+                )?);
             }
         }
 
         let instruction = Instruction::MakeArray { elements: merged, typ };
-        self.dfg
-            .insert_instruction_and_results(instruction, self.block, None, self.call_stack)
-            .first()
+        let result =
+            self.dfg.insert_instruction_and_results(instruction, self.block, None, self.call_stack);
+        Ok(result.first())
     }
 
     fn merge_slice_values(
@@ -179,7 +190,7 @@ impl<'a> ValueMerger<'a> {
         else_condition: ValueId,
         then_value_id: ValueId,
         else_value_id: ValueId,
-    ) -> ValueId {
+    ) -> Result<ValueId, RuntimeError> {
         let mut merged = im::Vector::new();
 
         let element_types = match &typ {
@@ -219,37 +230,36 @@ impl<'a> ValueMerger<'a> {
                     } else {
                         let offset = ArrayOffset::None;
                         let get = Instruction::ArrayGet { array, index, offset };
-                        self.dfg
-                            .insert_instruction_and_results(
-                                get,
-                                self.block,
-                                typevars,
-                                self.call_stack,
-                            )
-                            .first()
+                        let results = self.dfg.insert_instruction_and_results(
+                            get,
+                            self.block,
+                            typevars,
+                            self.call_stack,
+                        );
+                        results.first()
                     }
                 };
 
-                let then_element = get_element(
-                    then_value_id,
-                    typevars.clone(),
-                    then_len * element_types.len() as u32,
-                );
-                let else_element =
-                    get_element(else_value_id, typevars, else_len * element_types.len() as u32);
+                let len = then_len * element_types.len() as u32;
+                let then_element = get_element(then_value_id, typevars.clone(), len);
+
+                let len = else_len * element_types.len() as u32;
+                let else_element = get_element(else_value_id, typevars, len);
 
                 merged.push_back(self.merge_values(
                     then_condition,
                     else_condition,
                     then_element,
                     else_element,
-                ));
+                )?);
             }
         }
 
         let instruction = Instruction::MakeArray { elements: merged, typ };
         let call_stack = self.call_stack;
-        self.dfg.insert_instruction_and_results(instruction, self.block, None, call_stack).first()
+        let result =
+            self.dfg.insert_instruction_and_results(instruction, self.block, None, call_stack);
+        Ok(result.first())
     }
 
     /// Construct a dummy value to be attached to the smaller of two slices being merged.
```

### compiler/noirc_evaluator/src/ssa/opt/remove_if_else.rs
```diff
@@ -2,6 +2,7 @@ use std::collections::hash_map::Entry;
 
 use fxhash::FxHashMap as HashMap;
 
+use crate::errors::RtResult;
 use crate::ssa::ir::function::RuntimeType;
 use crate::ssa::ir::instruction::Hint;
 use crate::ssa::ir::value::ValueId;
@@ -27,25 +28,26 @@ impl Ssa {
     /// the given array may alias another array (e.g. function parameters or
     /// a `load`ed array from a reference).
     #[tracing::instrument(level = "trace", skip(self))]
-    pub(crate) fn remove_if_else(mut self) -> Ssa {
+    pub(crate) fn remove_if_else(mut self) -> RtResult<Ssa> {
         for function in self.functions.values_mut() {
-            function.remove_if_else();
+            function.remove_if_else()?;
         }
-        self
+        Ok(self)
     }
 }
 
 impl Function {
-    pub(crate) fn remove_if_else(&mut self) {
+    pub(crate) fn remove_if_else(&mut self) -> RtResult<()> {
         // This should match the check in flatten_cfg
         if matches!(self.runtime(), RuntimeType::Brillig(_)) {
             // skip
         } else {
-            Context::default().remove_if_else(self);
+            Context::default().remove_if_else(self)?;
         }
 
         #[cfg(debug_assertions)]
         remove_if_else_post_check(self);
+        Ok(())
     }
 }
 
@@ -55,13 +57,13 @@ struct Context {
 }
 
 impl Context {
-    fn remove_if_else(&mut self, function: &mut Function) {
+    fn remove_if_else(&mut self, function: &mut Function) -> RtResult<()> {
         let block = function.entry_block();
 
         // Make sure this optimization runs when there's only one block
         assert_eq!(function.dfg[block].successors().count(), 0);
 
-        function.simple_reachable_blocks_optimization(|context| {
+        function.simple_reachable_blocks_optimization_result(|context| {
             let instruction_id = context.instruction_id;
             let instruction = context.instruction();
 
@@ -84,16 +86,11 @@ impl Context {
                         else_condition,
                         then_value,
                         else_value,
-                    );
+                    )?;
 
                     let _typ = context.dfg.type_of_value(value);
                     let results = context.dfg.instruction_results(instruction_id);
                     let result = results[0];
-                    // let result = match typ {
-                    //     Type::Array(..) => results[0],
-                    //     Type::Slice(..) => results[1],
-                    //     other => unreachable!("IfElse instructions should only have arrays or slices at this point. Found {other:?}"),
-                    // };
 
                     context.remove_current_instruction();
                     context.replace_value(result, value);
@@ -129,7 +126,8 @@ impl Context {
                 }
                 _ => (),
             }
-        });
+            Ok(())
+        })
     }
 
     fn get_or_find_capacity(&mut self, dfg: &DataFlowGraph, value: ValueId) -> u32 {
@@ -290,7 +288,7 @@ mod tests {
         ";
 
         let mut ssa = Ssa::from_str(src).unwrap();
-        ssa = ssa.remove_if_else();
+        ssa = ssa.remove_if_else().unwrap();
 
         // In case our if block is never activated, we need to fetch each value from the original array.
         // We then should create a new array where each value can be mapped to `(then_condition * then_value) + (!then_condition * else_value)`.
@@ -359,7 +357,7 @@ mod tests {
         ";
 
         let mut ssa = Ssa::from_str(src).unwrap();
-        ssa = ssa.remove_if_else();
+        ssa = ssa.remove_if_else().unwrap();
 
         // We attempt to optimize array mergers to only handle where an array was modified,
         // rather than merging the entire array. As we only modify the `y` array at a single index,
```

### compiler/noirc_evaluator/src/ssa/opt/simple_optimization.rs
```diff
@@ -1,9 +1,12 @@
-use crate::ssa::ir::{
-    basic_block::BasicBlockId,
-    dfg::DataFlowGraph,
-    function::Function,
-    instruction::{Instruction, InstructionId},
-    value::{ValueId, ValueMapping},
+use crate::{
+    errors::RtResult,
+    ssa::ir::{
+        basic_block::BasicBlockId,
+        dfg::DataFlowGraph,
+        function::Function,
+        instruction::{Instruction, InstructionId},
+        value::{ValueId, ValueMapping},
+    },
 };
 
 impl Function {
@@ -23,6 +26,34 @@ impl Function {
     pub(crate) fn simple_reachable_blocks_optimization<F>(&mut self, mut f: F)
     where
         F: FnMut(&mut SimpleOptimizationContext<'_, '_>),
+    {
+        self.simple_reachable_blocks_optimization_result(move |context| {
+            f(context);
+            Ok(())
+        })
+        .expect("`f` cannot error internally so this should be unreachable");
+    }
+
+    /// Performs a simple optimization according to the given callback, returning early if
+    /// an error occurred.
+    ///
+    /// The function's [`Function::reachable_blocks`] are traversed in turn, and instructions in those blocks
+    /// are then traversed in turn. For each one, `f` will be called with a context.
+    ///
+    /// The current instruction will be inserted at the end of the callback given to `mutate` unless
+    /// `remove_current_instruction` or `insert_current_instruction` are called.
+    ///
+    /// `insert_current_instruction` is useful if you need to insert new instructions after the current
+    /// one, so this can be done before the callback ends.
+    ///
+    /// `replace_value` can be used to replace a value with another one. This substitution will be
+    /// performed in all subsequent instructions.
+    pub(crate) fn simple_reachable_blocks_optimization_result<F>(
+        &mut self,
+        mut f: F,
+    ) -> RtResult<()>
+    where
+        F: FnMut(&mut SimpleOptimizationContext<'_, '_>) -> RtResult<()>,
     {
         let mut values_to_replace = ValueMapping::default();
 
@@ -44,7 +75,7 @@ impl Function {
                     values_to_replace: &mut values_to_replace,
                     insert_current_instruction_at_callback_end: true,
                 };
-                f(&mut context);
+                f(&mut context)?;
 
                 if context.insert_current_instruction_at_callback_end {
                     self.dfg[block_id].insert_instruction(instruction_id);
@@ -55,6 +86,7 @@ impl Function {
         }
 
         self.dfg.data_bus.replace_values(&values_to_replace);
+        Ok(())
     }
 }
 
```
