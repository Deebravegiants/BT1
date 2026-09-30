# [?] [proofs] fix integer overflow

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2020-10-08
Source: https://github.com/move-language/move/commit/160ff22aea0c4c41b45b8a60ebee7e5748990ec7
Type: security-commit

## Details
[proofs] fix integer overflow

Closes: #6472

## Patch
### types/src/proof/position/mod.rs
```diff
@@ -216,7 +216,7 @@ fn smear_ones_for_u64(v: u64) -> u64 {
 ///     00010010000 n=3
 /// ```
 fn turn_off_right_most_n_bits(v: u64, n: u32) -> u64 {
-    precondition!(n < 64);
+    debug_checked_precondition!(n < 64);
     (v >> n) << n
 }
 
@@ -233,7 +233,7 @@ fn turn_off_right_most_n_bits(v: u64, n: u32) -> u64 {
 /// ```
 /// http://www.catonmat.net/blog/low-level-bit-hacks-you-absolutely-must-know/
 fn isolate_rightmost_zero_bit(v: u64) -> u64 {
-    !v & (v + 1)
+    !v & v.overflowing_add(1).0
 }
 
 // The following part of the position implementation is logically separate and
```
