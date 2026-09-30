# [?] Fix division overflow (#744)

## Summary
Severity: Unknown
Chain: ZK
Component: a16z/jolt
Published: 2025-07-02
Source: https://github.com/a16z/jolt/commit/2d0b5b2bd6f1b77112d87f2103f6ba5979fa7338
Type: security-commit

## Details
Fix division overflow (#744)

## Patch
### tracer/src/instruction/div.rs
```diff
@@ -52,7 +52,9 @@ impl RISCVTrace for DIV {
         let (quotient, remainder) = match cpu.xlen {
             Xlen::Bit32 => {
                 if y == 0 {
-                    (u32::MAX as u64, x as u64)
+                    (u32::MAX as u64, x as u32 as u64)
+                } else if x == cpu.most_negative() && y == -1 {
+                    (x as u32 as u64, 0)
                 } else {
                     let mut quotient = x as i32 / y as i32;
                     let mut remainder = x as i32 % y as i32;
@@ -66,6 +68,8 @@ impl RISCVTrace for DIV {
             Xlen::Bit64 => {
                 if y == 0 {
                     (u64::MAX, x as u64)
+                } else if x == cpu.most_negative() && y == -1 {
+                    (x as u64, 0)
                 } else {
                     let mut quotient = x / y;
                     let mut remainder = x % y;
```

### tracer/src/instruction/rem.rs
```diff
@@ -52,7 +52,9 @@ impl RISCVTrace for REM {
         let (quotient, remainder) = match cpu.xlen {
             Xlen::Bit32 => {
                 if y == 0 {
-                    (u32::MAX as u64, x as u64)
+                    (u32::MAX as u64, x as u32 as u64)
+                } else if x == cpu.most_negative() && y == -1 {
+                    (x as u32 as u64, 0)
                 } else {
                     let mut quotient = x as i32 / y as i32;
                     let mut remainder = x as i32 % y as i32;
@@ -66,6 +68,8 @@ impl RISCVTrace for REM {
             Xlen::Bit64 => {
                 if y == 0 {
                     (u64::MAX, x as u64)
+                } else if x == cpu.most_negative() && y == -1 {
+                    (x as u64, 0)
                 } else {
                     let mut quotient = x / y;
                     let mut remainder = x % y;
```
