# [?] Resolve memory overflow when `b256::TryFrom<Bytes>` is not 32 bytes (#6136)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2024-06-19
Source: https://github.com/FuelLabs/sway/commit/2cd6a59dfbd58616bea014d7c7286aaab81f413d
Type: security-commit

## Details
Resolve memory overflow when `b256::TryFrom<Bytes>` is not 32 bytes (#6136)

## Description

Currently, when calling the `TryFrom` implementation for `b256` from
`Bytes`, if the `Bytes` has less than 32 bytes a memory overflow error
will occur. If there is less than 32 bytes, `None` is now returned.

Example:
```sway
    let mut bytes = Bytes::with_capacity(32);
    let mut i = 0;
    while i < 32 {
        // 0x33 is 51 in decimal
        bytes.push(51u8);
        i += 1;
    }
    let res = b256::try_from(bytes);
    assert(res.unrwap() == 0x3333333333333333333333333333333333333333333333333333333333333333);
```

Closes #6129 

## Checklist

- [x] I have linked to any relevant issues.
- [x] I have commented my code, particularly in hard-to-understand
areas.
- [x] I have updated the documentation where relevant (API docs, the
reference, and the Sway book).
- [ ] If my change requires substantial documentation changes, I have
[requested support from the DevRel
team](https://github.com/FuelLabs/devrel-requests/issues/new/choose)
- [x] I have added tests that prove my fix is effective or that my
feature works.
- [x] I have added (or requested a maintainer to add) the necessary
`Breaking*` or `New Feature` labels where relevant.
- [x] I have done my best to ensure that my PR adheres to [the Fuel Labs
Code Review
Standards](https://github.com/FuelLabs/rfcs/blob/master/text/code-standards/external-contributors.md).
- [x] I have requested a review from the relevant team or maintainers.

---------

Co-authored-by: SwayStar123 <46050679+SwayStar123@users.noreply.github.com>
Co-authored-by: K1-R1 <77465250+K1-R1@users.noreply.github.com>

## Patch
### sway-lib-std/src/primitive_conversions/b256.sw
```diff
@@ -8,7 +8,7 @@ use ::b512::B512;
 
 impl TryFrom<Bytes> for b256 {
     fn try_from(b: Bytes) -> Option<Self> {
-        if b.len() > 32 {
+        if b.len() != 32 {
             None
         } else {
             let mut val = 0x0000000000000000000000000000000000000000000000000000000000000000;
```

### test/src/in_language_tests/test_programs/primitive_conversions_b256_inline_tests/src/main.sw
```diff
@@ -11,10 +11,10 @@ fn b256_try_from_bytes() {
         initial_bytes.push(51u8);
         i += 1;
     }
-    let res = b256::try_from(initial_bytes);
-    let expected = 0x3333333333333333333333333333333333333333333333333333333333333333;
-
-    assert(res.unwrap() == expected);
+    let res1 = b256::try_from(initial_bytes);
+    let expected1 = 0x3333333333333333333333333333333333333333333333333333333333333333;
+    assert(res1.is_some());
+    assert(res1.unwrap() == expected1);
 
     let mut second_bytes = Bytes::with_capacity(33);
     i = 0;
@@ -23,12 +23,22 @@ fn b256_try_from_bytes() {
         second_bytes.push(51u8);
         i += 1;
     }
-    let res = b256::try_from(second_bytes);
-    assert(res.is_none());
+    let res2 = b256::try_from(second_bytes);
+    assert(res2.is_none());
 
     // bytes is still available to use:
     assert(second_bytes.len() == 33);
     assert(second_bytes.capacity() == 33);
+
+    let mut third_bytes = Bytes::with_capacity(31);
+    let mut i = 0;
+    while i < 31 {
+        // 0x33 is 51 in decimal
+        third_bytes.push(51u8);
+        i += 1;
+    }
+    let res3 = b256::try_from(third_bytes);
+    assert(res3.is_none());
 }
 
 #[test]
```
