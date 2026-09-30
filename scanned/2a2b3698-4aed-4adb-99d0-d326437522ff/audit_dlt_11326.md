# [?] fix: prevent panic within `remove_possibly_mutated_cached_make_arrays` (#7264)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2025-02-03
Source: https://github.com/noir-lang/noir/commit/130d99125a09110a3ee3e877d88d83b5aa37f369
Type: security-commit

## Details
fix: prevent panic within `remove_possibly_mutated_cached_make_arrays` (#7264)

## Patch
### compiler/noirc_evaluator/src/ssa/opt/constant_folding.rs
```diff
@@ -725,6 +725,11 @@ impl<'brillig> Context<'brillig> {
 
         // Should we consider calls to slice_push_back and similar to be mutating operations as well?
         if let Store { value: array, .. } | ArraySet { array, .. } = instruction {
+            if function.dfg.is_global(*array) {
+                // Early return as we expect globals to be immutable.
+                return;
+            };
+
             let instruction = match &function.dfg[*array] {
                 Value::Instruction { instruction, .. } => &function.dfg[*instruction],
                 _ => return,
```
