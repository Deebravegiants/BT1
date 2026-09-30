# [?] fix(ssa): Do not panic in `remove_if_else_pre_check` if values other than array/vector are returned (#11272)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2026-01-20
Source: https://github.com/noir-lang/noir/commit/bea20efd2f2463e92f54d4da4f16be2ac53f1fd9
Type: security-commit

## Details
fix(ssa): Do not panic in `remove_if_else_pre_check` if values other than array/vector are returned (#11272)

## Patch
### compiler/noirc_evaluator/src/ssa/ir/dfg/simplify/value_merger.rs
```diff
@@ -1,5 +1,5 @@
 use acvm::acir::brillig::lengths::{ElementTypesLength, SemanticLength, SemiFlattenedLength};
-use noirc_errors::call_stack::CallStackId;
+use noirc_errors::{Location, call_stack::CallStackId};
 use rustc_hash::FxHashMap as HashMap;
 
 use crate::{
@@ -35,13 +35,23 @@ impl<'a> ValueMerger<'a> {
         ValueMerger { dfg, block, vector_sizes, call_stack }
     }
 
+    /// Choose a call stack to return with the [RuntimeError].
+    ///
+    /// If the call stack of the value is empty, it returns the call stack of the if-then-else itself.
+    fn get_call_stack(&self, value: ValueId) -> Vec<Location> {
+        // The value points at one of the problematic references, while the instruction would
+        // point at where we got the if-then-else; it's not clear which one is more useful.
+        let call_stack = self.dfg.get_value_call_stack(value);
+        if call_stack.is_empty() { self.dfg.get_call_stack(self.call_stack) } else { call_stack }
+    }
+
     /// Merge two values a and b to a single value.
     /// If these two values are numeric, the result will be
     /// `then_condition * (then_value - else_value) + else_value`.
     /// Otherwise, if the values being merged are arrays, a new array will be made
     /// recursively from combining each element of both input arrays.
     ///
-    /// It is currently an error to call this function on reference or function values
+    /// Returns an error if called with a function value or a reference or function values
     /// as it is less clear how to merge these.
     pub(crate) fn merge_values(
         &mut self,
@@ -74,13 +84,11 @@ impl<'a> ValueMerger<'a> {
                 else_value,
             ),
             Type::Reference(_) => {
-                // FIXME: none of then_value, else_value, then_condition, or else_condition have
-                // non-empty call stacks
-                let call_stack = self.dfg.get_value_call_stack(then_value);
+                let call_stack = self.get_call_stack(then_value);
                 Err(RuntimeError::ReturnedReferenceFromDynamicIf { call_stack })
             }
             Type::Function => {
-                let call_stack = self.dfg.get_value_call_stack(then_value);
+                let call_stack = self.get_call_stack(then_value);
                 Err(RuntimeError::ReturnedFunctionFromDynamicIf { call_stack })
             }
         }
```

### compiler/noirc_evaluator/src/ssa/opt/remove_if_else.rs
```diff
@@ -477,15 +477,12 @@ fn remove_if_else_pre_check(func: &Function) {
 
         for instruction_id in instruction_ids {
             if let Instruction::IfElse { then_value, .. } = &func.dfg[*instruction_id] {
-                assert!(
-                    func.dfg.instruction_results(*instruction_id).iter().all(|value| {
-                        matches!(
-                            func.dfg.type_of_value(*value),
-                            Type::Array(_, _) | Type::Vector(_)
-                        )
-                    }),
-                    "IfElse instruction returns unexpected type"
-                );
+                // We generally expect that all the results at this point will be either arrays or vectors,
+                // however the flattening makes no guarantee of this: if it needs to merge references or functions
+                // it will do so using IfElse. The ValueMerger already returns appropriate RuntimeErrors to point
+                // at the problem, so we don't assert this expectation.
+
+                // We do expect that numeric values are not used though.
                 let typ = func.dfg.type_of_value(*then_value);
                 assert!(
                     !matches!(typ, Type::Numeric(_)),
```

### test_programs/compile_failure/regression_11268/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "regression_11268"
+type = "bin"
+authors = [""]
+
+[dependencies]
\ No newline at end of file
```

### test_programs/compile_failure/regression_11268/src/main.nr
```diff
@@ -0,0 +1,7 @@
+fn main(c: bool) -> pub Field {
+    let f = || &mut 1;
+    let g = || &mut 2;
+    let h = if c { f } else { g };
+    let x = h();
+    *x
+}
```

### tooling/nargo_cli/tests/snapshots/compile_failure/regression_11268/execute__tests__stderr.snap
```diff
@@ -0,0 +1,15 @@
+---
+source: tooling/nargo_cli/tests/execute.rs
+expression: stderr
+---
+error: Cannot return references from an if or match expression, or assignment within these expressions
+  ┌─ src/main.nr:3:21
+  │
+3 │     let g = || &mut 2;
+  │                     -
+  │
+  = Call stack:
+    1. src/main.nr:5:13
+    2. src/main.nr:3:21
+
+Aborting due to 1 previous error
```
