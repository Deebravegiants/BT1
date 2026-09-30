# [?] [fuzzing] fix crash in fuzz_targets/move_vm.rs

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2021-12-02
Source: https://github.com/move-language/move/commit/ec71633908e541e1e861ac84e0756fd5bf5f44de
Type: security-commit

## Details
[fuzzing] fix crash in fuzz_targets/move_vm.rs

Closes: #9932

## Patch
### testsuite/diem-fuzzer/src/fuzz_targets/move_vm.rs
```diff
@@ -5,7 +5,7 @@ use crate::FuzzTargetImpl;
 use anyhow::{bail, Result};
 use byteorder::{BigEndian, ReadBytesExt, WriteBytesExt};
 use diem_proptest_helpers::ValueGenerator;
-use move_core_types::value::MoveTypeLayout;
+use move_core_types::value::{MoveStructLayout, MoveTypeLayout};
 use move_vm_types::values::{prop::layout_and_value_strategy, Value};
 use std::io::Cursor;
 
@@ -48,7 +48,9 @@ fn is_valid_layout(layout: &MoveTypeLayout) -> bool {
         L::Vector(layout) => is_valid_layout(layout),
 
         L::Struct(struct_layout) => {
-            if struct_layout.fields().is_empty() {
+            if !matches!(struct_layout, MoveStructLayout::Runtime(_))
+                || struct_layout.fields().is_empty()
+            {
                 return false;
             }
             struct_layout.fields().iter().all(is_valid_layout)
```
