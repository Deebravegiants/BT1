# [?] fix(aztec-nr): fix OOB index with nonzero offset (#21613)

## Summary
Severity: Unknown
Chain: Aztec
Component: AztecProtocol/aztec-packages
Published: 2026-03-17
Source: https://github.com/AztecProtocol/aztec-packages/commit/37149381b6dec554e8387fc5eeeaa3d5fe1eb117
Type: security-commit

## Details
fix(aztec-nr): fix OOB index with nonzero offset (#21613)

I simply asked Claude to go through our code and find bugs, and it found
this

## Summary
- Fixes an out-of-bounds array access in
`extract_property_value_from_selector` when `PropertySelector.offset >
0`. The formula `31 + offset - i` produces index >= 32 at `i = 0`;
corrected to `31 - offset - i`.
- Adds a regression test exercising a nonzero offset.

## Note
The bug was dormant -- every `PropertySelector` in the codebase uses
`offset: 0` (the macro hardcodes it). But anyone trying to use sub-field
byte selection would hit a runtime panic.

## Patch
### noir-projects/aztec-nr/aztec/src/note/note_getter.nr
```diff
@@ -29,11 +29,15 @@ fn extract_property_value_from_selector<let N: u32>(packed_note: [Field; N], sel
     let value: [u8; 32] = packed_note[selector.index as u32].to_be_bytes();
     let offset = selector.offset;
     let length = selector.length;
+    assert(offset as u32 + length as u32 <= 32, "PropertySelector offset + length exceeds field byte width");
     let mut value_field = 0 as Field;
     let mut acc: Field = 1;
     for i in 0..32 {
         if i < length {
-            value_field += value[(31 + offset - i) as u32] as Field * acc;
+            // `value` is big-endian, so the last byte (index 31) holds the lowest value.
+            // offset shifts the starting point away from that last byte, and i walks
+            // through consecutive bytes.
+            value_field += value[(31 - offset - i) as u32] as Field * acc;
             acc = acc * 256;
         }
     }
```

### noir-projects/aztec-nr/aztec/src/note/note_getter/test.nr
```diff
@@ -2,7 +2,7 @@ use crate::{
     note::{
         ConfirmedNote,
         HintedNote,
-        note_getter::{confirm_hinted_note, confirm_hinted_notes},
+        note_getter::{confirm_hinted_note, confirm_hinted_notes, extract_property_value_from_selector},
         note_getter_options::{NoteGetterOptions, PropertySelector, SortOrder},
     },
     oracle::random::random,
@@ -323,3 +323,68 @@ unconstrained fn constrain_view_note_rejects_mismatched_owner() {
         let _ = confirm_hinted_note(context, note, Option::some(owner), storage_slot);
     });
 }
+#[test]
+unconstrained fn extract_property_value_full_field_is_identity() {
+    let packed = [12345 as Field];
+    let selector = PropertySelector { index: 0, offset: 0, length: 32 };
+    let result = extract_property_value_from_selector(packed, selector);
+    assert_eq(result, 12345);
+}
+
+#[test]
+unconstrained fn extract_property_value_zero_length_returns_zero() {
+    let packed = [12345 as Field];
+    let selector = PropertySelector { index: 0, offset: 0, length: 0 };
+    let result = extract_property_value_from_selector(packed, selector);
+    assert_eq(result, 0);
+}
+
+#[test]
+unconstrained fn extract_property_value_with_zero_offset() {
+    // 0x030201 = [..., 0x03, 0x02, 0x01]. offset=0, length=2 reads [0x01, 0x02] -> 0x0201.
+    let packed = [0x030201 as Field];
+    let selector = PropertySelector { index: 0, offset: 0, length: 2 };
+    let result = extract_property_value_from_selector(packed, selector);
+    assert_eq(result, 0x0201);
+}
+
+#[test]
+unconstrained fn extract_property_value_with_nonzero_offset() {
+    // 0x0100 = [..., 0x01, 0x00]. offset=1 skips 0x00, length=1 reads 0x01.
+    let packed = [0x0100 as Field];
+    let selector = PropertySelector { index: 0, offset: 1, length: 1 };
+    let result = extract_property_value_from_selector(packed, selector);
+    assert_eq(result, 1);
+}
+
+#[test]
+unconstrained fn extract_property_value_nonzero_index() {
+    // index=1 skips the first Field (999) and reads from the second one (0x030201).
+    let packed = [999 as Field, 0x030201 as Field];
+    let selector = PropertySelector { index: 1, offset: 1, length: 2 };
+    let result = extract_property_value_from_selector(packed, selector);
+    assert_eq(result, 0x0302);
+}
+
+#[test]
+unconstrained fn extract_property_value_max_offset_reads_first_byte() {
+    // 256^31 = byte[0]=1, rest=0. offset=31, length=1 reads byte[0].
+    let packed = [Field::pow_32(256, 31)];
+    let selector = PropertySelector { index: 0, offset: 31, length: 1 };
+    let result = extract_property_value_from_selector(packed, selector);
+    assert_eq(result, 1);
+}
+
+#[test(should_fail_with = "PropertySelector offset + length exceeds field byte width")]
+unconstrained fn extract_property_value_rejects_offset_plus_length_exceeding_32() {
+    let packed = [1 as Field];
+    let selector = PropertySelector { index: 0, offset: 31, length: 2 };
+    let _ = extract_property_value_from_selector(packed, selector);
+}
+
+#[test(should_fail_with = "Index out of bounds")]
+unconstrained fn extract_property_value_fails_on_oob_index() {
+    let packed = [1 as Field];
+    let selector = PropertySelector { index: 1, offset: 0, length: 1 };
+    let _ = extract_property_value_from_selector(packed, selector);
+}
```
