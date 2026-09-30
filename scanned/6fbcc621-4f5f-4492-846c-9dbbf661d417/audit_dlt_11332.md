# [?] fix: prevent compiler panic when popping from empty slices (#6274)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-10-11
Source: https://github.com/noir-lang/noir/commit/87137d8d93622052dbe1c8a933d542a5c147c15c
Type: security-commit

## Details
fix: prevent compiler panic when popping from empty slices (#6274)

# Description

## Problem\*

Partial fix to https://github.com/noir-lang/noir/issues/5462

## Summary\*

This PR doesn't fully fix https://github.com/noir-lang/noir/issues/5462
but allows full compilation of a program without panicking. The test
program from #5462 now successfully compiles (due to us being able to
remove the inactive branch during inlining)


We still fail to properly handle branches which are conditional on
runtime values such as the below:
```
fn main(active: bool) {
    let empty_slice: [u8] = &[];

    if !active {
        let _ = empty_slice.pop_front();
    }
}
```

This compiles to the below program

```
Compiled ACIR for main (unoptimized):
func 0
current witness index : 2
private parameters indices : [0]
public parameters indices : []
return value indices : []
BLACKBOX::RANGE [(0)] [ ]
INIT (id: 0, len: 0) 
EXPR [ (-1, _1) 0 ]
MEM (id: 0, read at: x1, value: x2) 
```

This will then fail to execute with the below error:
```

error: Index out of bounds, array has size 0, but index was 0
   ┌─ /mnt/user-data/tom/noir/test_programs/execution_success/inactive_slice_popping/src/main.nr:11:17
   │
11 │         let _ = empty_slice.pop_front();
   │                 ---------------------
   │
   = Call stack:
     1. /mnt/user-data/tom/noir/test_programs/execution_success/inactive_slice_popping/src/main.nr:11:17

```

Note the memory block has been allocated with a length of 0 so even
applying a predicate to the array get will fail.

## Additional Context



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
### compiler/noirc_evaluator/src/ssa/ir/instruction.rs
```diff
@@ -118,15 +118,15 @@ impl Intrinsic {
             // These apply a constraint that the input must fit into a specified number of limbs.
             Intrinsic::ToBits(_) | Intrinsic::ToRadix(_) => true,
 
+            // These imply a check that the slice is non-empty and should fail otherwise.
+            Intrinsic::SlicePopBack | Intrinsic::SlicePopFront | Intrinsic::SliceRemove => true,
+
             Intrinsic::ArrayLen
             | Intrinsic::ArrayAsStrUnchecked
             | Intrinsic::AsSlice
             | Intrinsic::SlicePushBack
             | Intrinsic::SlicePushFront
-            | Intrinsic::SlicePopBack
-            | Intrinsic::SlicePopFront
             | Intrinsic::SliceInsert
-            | Intrinsic::SliceRemove
             | Intrinsic::StrAsBytes
             | Intrinsic::FromField
             | Intrinsic::AsField
```

### compiler/noirc_evaluator/src/ssa/ir/instruction/call.rs
```diff
@@ -166,6 +166,13 @@ pub(super) fn simplify_call(
             }
         }
         Intrinsic::SlicePopBack => {
+            let length = dfg.get_numeric_constant(arguments[0]);
+            if length.map_or(true, |length| length.is_zero()) {
+                // If the length is zero then we're trying to pop the last element from an empty slice.
+                // Defer the error to acir_gen.
+                return SimplifyResult::None;
+            }
+
             let slice = dfg.get_array_constant(arguments[1]);
             if let Some((_, typ)) = slice {
                 simplify_slice_pop_back(typ, arguments, dfg, block, call_stack.clone())
@@ -174,6 +181,13 @@ pub(super) fn simplify_call(
             }
         }
         Intrinsic::SlicePopFront => {
+            let length = dfg.get_numeric_constant(arguments[0]);
+            if length.map_or(true, |length| length.is_zero()) {
+                // If the length is zero then we're trying to pop the first element from an empty slice.
+                // Defer the error to acir_gen.
+                return SimplifyResult::None;
+            }
+
             let slice = dfg.get_array_constant(arguments[1]);
             if let Some((mut slice, typ)) = slice {
                 let element_count = typ.element_size();
@@ -225,6 +239,13 @@ pub(super) fn simplify_call(
             }
         }
         Intrinsic::SliceRemove => {
+            let length = dfg.get_numeric_constant(arguments[0]);
+            if length.map_or(true, |length| length.is_zero()) {
+                // If the length is zero then we're trying to remove an element from an empty slice.
+                // Defer the error to acir_gen.
+                return SimplifyResult::None;
+            }
+
             let slice = dfg.get_array_constant(arguments[1]);
             let index = dfg.get_numeric_constant(arguments[2]);
             if let (Some((mut slice, typ)), Some(index)) = (slice, index) {
```

### compiler/noirc_evaluator/src/ssa/opt/flatten_cfg/capacity_tracker.rs
```diff
@@ -99,7 +99,9 @@ impl<'a> SliceCapacityTracker<'a> {
                             let slice_contents = arguments[argument_index];
 
                             if let Some(contents_capacity) = slice_sizes.get(&slice_contents) {
-                                let new_capacity = *contents_capacity - 1;
+                                // We use a saturating sub here as calling `pop_front` or `pop_back`
+                                // on a zero-length slice would otherwise underflow.
+                                let new_capacity = contents_capacity.saturating_sub(1);
                                 slice_sizes.insert(result_slice, new_capacity);
                             }
                         }
```

### compiler/noirc_evaluator/src/ssa/opt/remove_if_else.rs
```diff
@@ -118,7 +118,9 @@ impl Context {
                             }
                             SizeChange::Dec { old, new } => {
                                 let old_capacity = self.get_or_find_capacity(&function.dfg, old);
-                                self.slice_sizes.insert(new, old_capacity - 1);
+                                // We use a saturating sub here as calling `pop_front` or `pop_back` on a zero-length slice
+                                // would otherwise underflow.
+                                self.slice_sizes.insert(new, old_capacity.saturating_sub(1));
                             }
                         }
                     }
```
