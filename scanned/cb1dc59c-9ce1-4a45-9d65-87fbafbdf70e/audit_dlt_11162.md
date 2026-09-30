# [?] fix(processor): return error on empty OverflowTable instead of panicking (#3370)

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2026-07-31
Source: https://github.com/0xMiden/miden-vm/commit/4261ef277bb4acd722f66e80dd0a72a0c4dac360
Type: security-commit

## Details
fix(processor): return error on empty OverflowTable instead of panicking (#3370)

Signed-off-by: Sertug17 <104278804+Sertug17@users.noreply.github.com>
Co-authored-by: François Garillot <4142+huitseeker@users.noreply.github.com>

## Patch
### CHANGELOG.md
```diff
@@ -4,6 +4,7 @@
 
 #### Changes
 - [BREAKING] Normalized each AIR's committed LogUp sum by its trace length and changed the running-sum constraint to close cyclically, removing the requirement that lookup activity be absent from the last row ([#3412](https://github.com/0xMiden/miden-vm/pull/3412)).
+- Replaced panics in `OverflowTable::restore_context()`, `get_current_overflow_stack()`, and `get_current_overflow_stack_mut()` with proper `OperationError` returns ([#3370](https://github.com/0xMiden/miden-vm/pull/3370)).
 - `FastProcessor` `restore_call_state()` and `restore_context()` now return `OperationError::Internal` instead of panicking on empty stacks ([#3371](https://github.com/0xMiden/miden-vm/pull/3371), fixes [#3296](https://github.com/0xMiden/miden-vm/issues/3296)).
 
 - Opened the `LargeSmtForest` backend API for external implementations: made `LineageMutation::new` and `AppliedLineageMutation::new` public and added `LineageId::as_bytes` and `MutationSet::from_parts`.
```

### processor/src/execution/mod.rs
```diff
@@ -704,7 +704,9 @@ where
     F: ExecutableMastForest + Clone,
 {
     // Signal the end of clock cycle to tracer (before incrementing processor clock).
-    tracer.finalize_clock_cycle(processor, op_helper_registers, current_forest);
+    if let Err(e) = tracer.finalize_clock_cycle(processor, op_helper_registers, current_forest) {
+        return ControlFlow::Break(BreakReason::Err(e));
+    }
 
     // Increment the processor clock.
     processor.system_mut().increment_clock();
```

### processor/src/fast/mod.rs
```diff
@@ -714,7 +714,8 @@ impl Tracer for NoopTracer {
         _processor: &FastProcessor,
         _op_helper_registers: OperationHelperRegisters,
         _current_forest: &Arc<MastForest>,
-    ) {
+    ) -> Result<(), ExecutionError> {
         // do nothing
+        Ok(())
     }
 }
```

### processor/src/trace/execution_tracer.rs
```diff
@@ -18,7 +18,8 @@ use super::{
     utils::split_u32_into_u16,
 };
 use crate::{
-    ContextId, EMPTY_WORD, FastProcessor, Felt, MIN_STACK_DEPTH, ONE, RowIndex, Word, ZERO,
+    ContextId, EMPTY_WORD, ExecutionError, FastProcessor, Felt, MIN_STACK_DEPTH, ONE, RowIndex,
+    Word, ZERO,
     continuation_stack::{Continuation, ContinuationStack},
     crypto::merkle::MerklePath,
     mast::{
@@ -934,14 +935,18 @@ impl Tracer for ExecutionTracer {
         processor: &FastProcessor,
         _op_helper_registers: OperationHelperRegisters,
         _current_forest: &Arc<MastForest>,
-    ) {
+    ) -> Result<(), ExecutionError> {
         // Restore the overflow table context for Call/Syscall/Dyncall END. This is deferred
         // from start_clock_cycle because finalize_clock_cycle is only called when the operation
         // succeeds (i.e., the stack depth check in processor.restore_context() passes).
         if self.pending_restore_context {
             // Restore context for call/syscall/dyncall: pop the current context's
             // (empty) overflow stack and restore the previous context's overflow state.
-            self.overflow_table.restore_context();
+            self.overflow_table.restore_context().map_err(|_| {
+                ExecutionError::Internal(
+                    "overflow table restore_context failed during trace finalization",
+                )
+            })?;
             self.overflow_replay.record_restore_context_overflow_addr(
                 MIN_STACK_DEPTH + self.overflow_table.num_elements_in_current_ctx(),
                 self.overflow_table.last_update_clk_in_current_ctx(),
@@ -982,6 +987,8 @@ impl Tracer for ExecutionTracer {
 
             self.is_eval_circuit_op = false;
         }
+
+        Ok(())
     }
 }
 
```

### processor/src/trace/parallel/tracer/mod.rs
```diff
@@ -435,9 +435,9 @@ impl Tracer for CoreTraceGenerationTracer<'_> {
         processor: &ReplayProcessor,
         op_helper_registers: OperationHelperRegisters,
         current_forest: &Arc<SparseMastForest>,
-    ) {
+    ) -> Result<(), ExecutionError> {
         if self.error_encountered.is_some() {
-            return;
+            return Ok(());
         }
 
         use Continuation::*;
@@ -623,6 +623,8 @@ impl Tracer for CoreTraceGenerationTracer<'_> {
         if let Err(e) = result {
             self.error_encountered = Some(e);
         }
+
+        Ok(())
     }
 }
 
```

### processor/src/trace/stack/overflow.rs
```diff
@@ -2,6 +2,7 @@ use miden_air::trace::RowIndex;
 use miden_utils_indexing::IndexVec;
 
 use super::{Felt, ZERO};
+use crate::operation::OperationError;
 
 // OVERFLOW TABLE
 // ================================================================================================
@@ -106,6 +107,7 @@ impl OverflowTable {
     /// returned.
     pub fn last_update_clk_in_current_ctx(&self) -> Felt {
         self.get_current_overflow_stack()
+            .expect("overflow table should always have at least one stack")
             .last()
             .map_or(ZERO, |entry| Felt::from(entry.clk))
     }
@@ -120,7 +122,9 @@ impl OverflowTable {
     /// Used by `ExecutionTracer` to compute `parent_next_overflow_addr` for `DYNCALL` before
     /// the actual pop has occurred (fixes #2813 / addresses huitseeker's review on PR #2904).
     pub fn clk_after_pop_in_current_ctx(&self) -> Felt {
-        let stack = self.get_current_overflow_stack();
+        let stack = self
+            .get_current_overflow_stack()
+            .expect("overflow table should always have at least one stack");
         let entries = stack.overflow.as_slice();
         if entries.len() < 2 {
             ZERO
@@ -131,21 +135,26 @@ impl OverflowTable {
 
     /// Returns the number of elements in the overflow stack for the current context.
     pub fn num_elements_in_current_ctx(&self) -> usize {
-        self.get_current_overflow_stack().num_elements()
+        self.get_current_overflow_stack()
+            .expect("overflow table should always have at least one stack")
+            .num_elements()
     }
 
     // PUBLIC MUTATORS
     // --------------------------------------------------------------------------------------------
 
     /// Pushes a value into the overflow table in the current context.
     pub fn push(&mut self, value: Felt, clk: RowIndex) {
-        self.get_current_overflow_stack_mut().push(OverflowStackEntry::new(value, clk));
+        self.get_current_overflow_stack_mut()
+            .expect("overflow table should always have at least one stack")
+            .push(OverflowStackEntry::new(value, clk));
     }
 
     /// Removes the last value from the overflow table in the current context, if any, and returns
     /// it.
     pub fn pop(&mut self) -> Option<Felt> {
         self.get_current_overflow_stack_mut()
+            .expect("overflow table should always have at least one stack")
             .pop()
             .as_ref()
             .map(OverflowStackEntry::value)
@@ -163,17 +172,27 @@ impl OverflowTable {
 
     /// Restores the specified context.
     ///
-    /// # Panics
-    /// - if there is no overflow stack for the current context.
-    /// - if the overflow stack for the current context is not empty.
-    ///   - i.e. this should be checked before calling this function.
-    pub fn restore_context(&mut self) {
-        // 1. pop the last overflow stack for the current context, and make sure it is empty.
-        let overflow_stack_for_ctx = self.overflow.swap_remove(self.overflow.len() - 1);
-        assert!(
-            overflow_stack_for_ctx.is_empty(),
-            "the overflow stack for the current context should be empty when restoring a context"
-        );
+    /// Returns an error if the overflow table has no stacks (i.e. there is no current context)
+    /// or if the overflow stack for the current context is not empty (i.e. the caller should
+    /// have drained it before calling this function).
+    pub fn restore_context(&mut self) -> Result<(), OperationError> {
+        let len = self.overflow.len();
+
+        if len <= 1 {
+            return Err(OperationError::Internal(
+                "cannot restore context: must have at least one child context above the root stack",
+            ));
+        }
+
+        let is_empty = self.overflow.as_slice().last().expect("len > 0").is_empty();
+        if !is_empty {
+            return Err(OperationError::Internal(
+                "cannot restore context: overflow stack for the current context is not empty",
+            ));
+        }
+
+        self.overflow.swap_remove(len - 1);
+        Ok(())
     }
 
     // HELPERS
@@ -184,17 +203,21 @@ impl OverflowTable {
     /// Specifically, this is a reference to the more recent overflow stack in the list of overflow
     /// stacks for the current context. Recall that for all contexts other than the root context,
     /// there is at most one overflow stack, but for the root context, there can be two.
-    fn get_current_overflow_stack(&self) -> &OverflowStack {
-        self.overflow
-            .as_slice()
-            .last()
-            .expect("The current context should always have an overflow stack initialized")
+    fn get_current_overflow_stack(&self) -> Result<&OverflowStack, OperationError> {
+        self.overflow.as_slice().last().ok_or(OperationError::Internal(
+            "the current context should always have an overflow stack initialized",
+        ))
     }
 
     /// Mutable version of `get_current_overflow_stack()`.
-    fn get_current_overflow_stack_mut(&mut self) -> &mut OverflowStack {
+    fn get_current_overflow_stack_mut(&mut self) -> Result<&mut OverflowStack, OperationError> {
         let len = self.overflow.len();
-        &mut self.overflow[RowIndex::from(len - 1)]
+        if len == 0 {
+            return Err(OperationError::Internal(
+                "the current context should always have an overflow stack initialized",
+            ));
+        }
+        Ok(&mut self.overflow[RowIndex::from(len - 1)])
     }
 }
 
@@ -203,3 +226,47 @@ impl Default for OverflowTable {
         Self::new()
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use miden_air::trace::RowIndex;
+
+    use super::*;
+
+    #[test]
+    fn restore_context_rejects_root_only_table() {
+        let mut table = OverflowTable::new();
+        // Table has only the root stack (len == 1), restore should fail.
+        let result = table.restore_context();
+        assert!(result.is_err(), "restore_context should reject root-only table");
+        // Table should be unchanged: still has 1 stack.
+        assert_eq!(table.num_elements_in_current_ctx(), 0);
+    }
+
+    #[test]
+    fn restore_context_rejects_non_empty_child_stack() {
+        let mut table = OverflowTable::new();
+        table.start_context();
+        table.push(Felt::new(42).unwrap(), RowIndex::from(1));
+        // Child stack is not empty, restore should fail.
+        let result = table.restore_context();
+        assert!(result.is_err(), "restore_context should reject non-empty child stack");
+        // Table should be unchanged: child stack still has 1 element.
+        assert_eq!(table.num_elements_in_current_ctx(), 1);
+    }
+
+    #[test]
+    fn restore_context_succeeds_with_empty_child_stack() {
+        let mut table = OverflowTable::new();
+        table.start_context();
+        // Child stack is empty, restore should succeed.
+        let result = table.restore_context();
+        assert!(result.is_ok(), "restore_context should succeed with empty child stack");
+        // Back to root stack.
+        assert_eq!(table.num_elements_in_current_ctx(), 0);
+
+        // Second call should fail — only root stack remains.
+        let result2 = table.restore_context();
+        assert!(result2.is_err(), "restore_context on root stack should fail");
+    }
+}
```

### processor/src/tracer.rs
```diff
@@ -7,7 +7,7 @@ use miden_core::{
 };
 
 use crate::{
-    ContextId,
+    ContextId, ExecutionError,
     continuation_stack::{Continuation, ContinuationStack},
     trace::{chiplets::CircuitEvaluation, utils::split_u32_into_u16},
 };
@@ -100,7 +100,7 @@ pub trait Tracer {
         processor: &Self::Processor,
         op_helper_registers: OperationHelperRegisters,
         current_forest: &Self::Forest,
-    );
+    ) -> Result<(), ExecutionError>;
 
     // MAST FOREST RESOLUTION
     // --------------------------------------------------------------------------------------------
```
