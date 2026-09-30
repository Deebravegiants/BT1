# [?] Fix memory range-check clk underflow (#2976)

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2026-04-10
Source: https://github.com/0xMiden/miden-vm/commit/743bef60c36deb53e8c82620eacb0e50788429ad
Type: security-commit

## Details
Fix memory range-check clk underflow (#2976)

* Fix memory range-check clk underflow

* chore: Changelog

## Patch
### CHANGELOG.md
```diff
@@ -7,6 +7,7 @@
 - Reverted the `MainTrace` typed row storage change that caused a large `blake3_1to1` trace-building regression ([#2949](https://github.com/0xMiden/miden-vm/pull/2949)).
 #### Bug Fixes
 
+- Fixed debug-only underflow in memory range-check trace generation when the first memory access is at `clk = 0` ([#2976](https://github.com/0xMiden/miden-vm/pull/2976)).
 - Replaced unsound `ptr::read` with safe unbox in panic recovery, removing UB from potential double-drop ([#2934](https://github.com/0xMiden/miden-vm/pull/2934)).
 - Reverted `InvokeKind::ProcRef` back to `InvokeKind::Exec` in `visit_mut_procref` and added an explanatory comment (#2893).
 - Fixed the release dry-run publish cycle between `miden-air` and `miden-ace-codegen`, and preserved leaf-only DAG imports with explicit snapshots ([#2931](https://github.com/0xMiden/miden-vm/pull/2931)).
```

### processor/src/trace/chiplets/memory/mod.rs
```diff
@@ -255,7 +255,7 @@ impl Memory {
         // trace; we also adjust the clock cycle so that delta value for the first row would end
         // up being ZERO. if the trace is empty, return without any further processing.
         let (mut prev_ctx, mut prev_addr, mut prev_clk) = match self.get_first_row_info() {
-            Some((ctx, addr, clk)) => (ctx, addr, clk.as_canonical_u64() - 1),
+            Some((ctx, addr, clk)) => (ctx, addr, clk.as_canonical_u64().wrapping_sub(1)),
             None => return,
         };
 
@@ -275,7 +275,7 @@ impl Memory {
                     } else if prev_addr != addr {
                         u64::from(addr - prev_addr)
                     } else {
-                        clk - prev_clk
+                        clk.wrapping_sub(prev_clk)
                     };
 
                     let (delta_hi, delta_lo) = split_u32_into_u16(delta);
```

### processor/src/trace/chiplets/memory/tests.rs
```diff
@@ -15,7 +15,7 @@ use super::{
     TraceFragment, V_COL_RANGE, WORD_ADDR_HI_COL_IDX, WORD_ADDR_LO_COL_IDX, WORD_COL_IDX,
     segment::{MemoryAccessType, MemoryOperation},
 };
-use crate::{ContextId, MemoryAddress, MemoryError};
+use crate::{ContextId, MemoryAddress, MemoryError, trace::range::RangeChecker};
 
 #[test]
 fn mem_init() {
@@ -455,6 +455,17 @@ fn mem_get_state_at() {
     assert_eq!(mem.get_state_at(3.into(), clk), vec![]);
 }
 
+#[test]
+fn append_range_checks_does_not_panic_when_first_access_clk_is_zero() {
+    let mut mem = Memory::default();
+    mem.write(ContextId::root(), ZERO, 0.into(), ONE).unwrap();
+
+    let mut range_checker = RangeChecker::new();
+    mem.append_range_checks(0.into(), &mut range_checker);
+
+    assert!(range_checker.trace_len() > 0);
+}
+
 // HELPER STRUCT & FUNCTIONS
 // ================================================================================================
 
```

### processor/src/trace/chiplets/tests.rs
```diff
@@ -11,7 +11,7 @@ use miden_air::trace::{
 };
 use miden_core::{
     Felt, ONE, Word, ZERO,
-    mast::{BasicBlockNodeBuilder, MastForest, MastForestContributor},
+    mast::{BasicBlockNodeBuilder, CallNodeBuilder, MastForest, MastForestContributor},
     program::{Program, StackInputs},
 };
 
@@ -136,6 +136,32 @@ fn stacked_chiplet_trace() {
     validate_padding(&chiplets_trace, padding_start, trace_rows);
 }
 
+#[test]
+fn regression_trace_build_does_not_panic_when_first_memory_access_clk_is_zero() {
+    let processor = FastProcessor::new(StackInputs::default());
+    let mut host = DefaultHost::default();
+
+    // A CALL entrypoint records the callee frame pointer write before the processor clock is
+    // incremented, so the first memory access is captured at clk = 0.
+    let program = {
+        let mut forest = MastForest::new();
+
+        let callee = BasicBlockNodeBuilder::new(vec![Operation::Noop], Vec::new())
+            .add_to_forest(&mut forest)
+            .unwrap();
+        forest.make_root(callee);
+
+        let entry = CallNodeBuilder::new(callee).add_to_forest(&mut forest).unwrap();
+        forest.make_root(entry);
+
+        Program::with_kernel(forest.into(), entry, Kernel::default())
+    };
+
+    let trace_inputs = processor.execute_trace_inputs_sync(&program, &mut host).unwrap();
+
+    let _trace = crate::trace::build_trace(trace_inputs).unwrap();
+}
+
 // HELPER FUNCTIONS
 // ================================================================================================
 
```
