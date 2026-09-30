# [?] fix padlength overflow error

## Summary
Severity: Unknown
Chain: ZK
Component: 0xPolygonZero/plonky2
Published: 2022-09-24
Source: https://github.com/0xPolygonZero/plonky2/commit/85b88a1cde027a834f299dda8a31fdb2582e7feb
Type: security-commit

## Details
fix padlength overflow error

## Patch
### evm/src/cpu/kernel/asm/ripemd/ripemd.asm
```diff
@@ -92,15 +92,14 @@ global process:
 %macro padlength
     // stack:          count
     %mod_const(64)
-    // stack:          count % 64
-    PUSH 56
-    SUB
-    // stack: x = 56 - count % 64
-    DUP1
-    %lt_const(9)
-    // stack:     x < 9  , x
+    // stack:      t = count % 64
+    PUSH 47
+    DUP2
+    // stack:          t , 47 , t
+    GT
+    // stack:          t > 47 , t
     %mul_const(64)
-    // stack: 64*(x < 9) , x
-    ADD
-    // stack: 64*(x < 9) + x
+    %add_const(56)
+    // stack: 56 + 64*(t > 47), t 
+    SUB
 %endmacro
```

### evm/src/cpu/kernel/tests/ripemd.rs
```diff
@@ -12,8 +12,8 @@ fn make_input(word: &str) -> Vec<u8> {
 
 #[test]
 fn test_ripemd() -> Result<()> {
-    let input: Vec<u8> = make_input("a");
-    let expected = U256::from("0x0bdc9d2d256b3ee9daae347be6f4dc835a467ffe");
+    let input: Vec<u8> = make_input("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789");
+    let expected = U256::from("0xb0e20b6e3116640286ed3a87a5713079b21f5189");
 
     let kernel = combined_kernel();
     let label = kernel.global_labels["ripemd_alt"];
```
