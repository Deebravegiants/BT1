# [?] Merge pull request #1990 from AleoHQ/fix/unecessary-overflow-checks

## Summary
Severity: Unknown
Chain: Aleo
Component: AleoNet/snarkVM-test
Published: 2023-10-07
Source: https://github.com/AleoNet/snarkVM-test/commit/735d69121780ec8ff9a01fe0c516a0efccff6148
Type: security-commit

## Details
Merge pull request #1990 from AleoHQ/fix/unecessary-overflow-checks

[TOB] Remove unnecessary overflow checks

## Patch
### synthesizer/program/src/logic/instruction/operation/mod.rs
```diff
@@ -158,11 +158,11 @@ crate::operation!(
         (I32, I32) => I32 ("ensure overflows halt", "ensure divide by zero halts"),
         (I64, I64) => I64 ("ensure overflows halt", "ensure divide by zero halts"),
         (I128, I128) => I128 ("ensure overflows halt", "ensure divide by zero halts"),
-        (U8, U8) => U8 ("ensure overflows halt", "ensure divide by zero halts"),
-        (U16, U16) => U16 ("ensure overflows halt", "ensure divide by zero halts"),
-        (U32, U32) => U32 ("ensure overflows halt", "ensure divide by zero halts"),
-        (U64, U64) => U64 ("ensure overflows halt", "ensure divide by zero halts"),
-        (U128, U128) => U128 ("ensure overflows halt", "ensure divide by zero halts"),
+        (U8, U8) => U8 ("ensure divide by zero halts"),
+        (U16, U16) => U16 ("ensure divide by zero halts"),
+        (U32, U32) => U32 ("ensure divide by zero halts"),
+        (U64, U64) => U64 ("ensure divide by zero halts"),
+        (U128, U128) => U128 ("ensure divide by zero halts"),
         // (Scalar, Scalar) => Scalar,
     }
 );
@@ -499,11 +499,11 @@ crate::operation!(
         (I32, I32) => I32 ("ensure overflows halt", "ensure divide by zero halts"),
         (I64, I64) => I64 ("ensure overflows halt", "ensure divide by zero halts"),
         (I128, I128) => I128 ("ensure overflows halt", "ensure divide by zero halts"),
-        (U8, U8) => U8 ("ensure overflows halt", "ensure divide by zero halts"),
-        (U16, U16) => U16 ("ensure overflows halt", "ensure divide by zero halts"),
-        (U32, U32) => U32 ("ensure overflows halt", "ensure divide by zero halts"),
-        (U64, U64) => U64 ("ensure overflows halt", "ensure divide by zero halts"),
-        (U128, U128) => U128 ("ensure overflows halt", "ensure divide by zero halts"),
+        (U8, U8) => U8 ("ensure divide by zero halts"),
+        (U16, U16) => U16 ("ensure divide by zero halts"),
+        (U32, U32) => U32 ("ensure divide by zero halts"),
+        (U64, U64) => U64 ("ensure divide by zero halts"),
+        (U128, U128) => U128 ("ensure divide by zero halts"),
     }
 );
 
```
