# [?] Correctly check for overflow in add, mul and pow (#6452)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2024-09-09
Source: https://github.com/FuelLabs/sway/commit/4830d00ecaa2581e6054502c0c17929c251e6d9b
Type: security-commit

## Details
Correctly check for overflow in add, mul and pow (#6452)

## Description
Adds flag checks for overflow in core lib, properly cap values if
overflow is enabled

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

Co-authored-by: Cameron Carstens <bitzoic.eth@gmail.com>
Co-authored-by: Sophie Dankel <47993817+sdankel@users.noreply.github.com>
Co-authored-by: K1-R1 <77465250+K1-R1@users.noreply.github.com>

## Patch
### sway-lib-core/src/ops.sw
```diff
@@ -59,9 +59,15 @@ impl Add for u32 {
         // any non-64-bit value is compiled to a u64 value under-the-hood
         // constants (like Self::max() below) are also automatically promoted to u64
         let res = __add(self, other);
+        // integer overflow
         if __gt(res, Self::max()) {
-            // integer overflow
-            __revert(0)
+            if panic_on_overflow_is_enabled() {
+                __revert(0)
+            } else {
+                // overflow enabled
+                // res % (Self::max() + 1)
+                __mod(res, __add(Self::max(), 1))
+            }
         } else {
             // no overflow
             res
@@ -73,7 +79,13 @@ impl Add for u16 {
     fn add(self, other: Self) -> Self {
         let res = __add(self, other);
         if __gt(res, Self::max()) {
-            __revert(0)
+            if panic_on_overflow_is_enabled() {
+                __revert(0)
+            } else {
+                // overflow enabled
+                // res % (Self::max() + 1)
+                __mod(res, __add(Self::max(), 1))
+            }
         } else {
             res
         }
@@ -93,7 +105,16 @@ impl Add for u8 {
             input: u64
         };
         if __gt(res_u64, max_u8_u64) {
-            __revert(0)
+            if panic_on_overflow_is_enabled() {
+                __revert(0)
+            } else {
+                // overflow enabled
+                // res % (Self::max() + 1)
+                let res_u64 = __mod(res_u64, __add(max_u8_u64, 1));
+                asm(input: res_u64) {
+                    input: u8
+                }
+            }
         } else {
             asm(input: res_u64) {
                 input: u8
@@ -229,8 +250,14 @@ impl Multiply for u32 {
         // constants (like Self::max() below) are also automatically promoted to u64
         let res = __mul(self, other);
         if __gt(res, Self::max()) {
-            // integer overflow
-            __revert(0)
+            if panic_on_overflow_is_enabled() {
+                // integer overflow
+                __revert(0)
+            } else {
+                // overflow enabled
+                // res % (Self::max() + 1)
+                __mod(res, __add(Self::max(), 1))
+            }
         } else {
             // no overflow
             res
@@ -242,7 +269,11 @@ impl Multiply for u16 {
     fn multiply(self, other: Self) -> Self {
         let res = __mul(self, other);
         if __gt(res, Self::max()) {
-            __revert(0)
+            if panic_on_overflow_is_enabled() {
+                __revert(0)
+            } else {
+                __mod(res, __add(Self::max(), 1))
+            }
         } else {
             res
         }
@@ -262,7 +293,16 @@ impl Multiply for u8 {
             input: u64
         };
         if __gt(res_u64, max_u8_u64) {
-            __revert(0)
+            if panic_on_overflow_is_enabled() {
+                __revert(0)
+            } else {
+                // overflow enabled
+                // res % (Self::max() + 1)
+                let res_u64 = __mod(res_u64, __add(max_u8_u64, 1));
+                asm(input: res_u64) {
+                    input: u8
+                }
+            }
         } else {
             asm(input: res_u64) {
                 input: u8
@@ -1258,3 +1298,19 @@ pub fn ok_str_eq() {
     assert("" != "a");
     assert("a" != "b");
 }
+
+fn flags() -> u64 {
+    asm() {
+        flag
+    }
+}
+
+fn panic_on_overflow_is_enabled() -> bool {
+    __eq(
+        __and(
+            flags(),
+            0b00000000_00000000_00000000_00000000_00000000_00000000_00000000_00000010,
+        ),
+        0,
+    )
+}
```

### sway-lib-std/src/math.sw
```diff
@@ -2,6 +2,8 @@
 library;
 
 use ::assert::*;
+use ::revert::revert;
+use ::option::Option::{self, None, Some};
 use ::flags::{
     disable_panic_on_overflow,
     panic_on_overflow_enabled,
@@ -78,12 +80,38 @@ pub trait Power {
     fn pow(self, exponent: u32) -> Self;
 }
 
+fn u256_checked_mul(a: u256, b: u256) -> Option<u256> {
+    let res = u256::zero();
+
+    // The six-bit immediate value is used to select operating mode, as follows:
+
+    // Bits	Short name	Description
+    // ..XXXX	reserved	Reserved and must be zero
+    // .X....	indirect0	Is lhs operand ($rB) indirect or not
+    // X.....	indirect1	Is rhs operand ($rC) indirect or not
+    // As both operands are indirect, 110000 is used, which is 48 in decimal.
+    let of = asm(res: res, a: a, b: b) {
+        wqml res a b i48;
+        of: u64
+    };
+
+    if of != 0 {
+        return None;
+    }
+
+    Some(res)
+}
+
 impl Power for u256 {
     /// Raises self to the power of `exponent`, using exponentiation by squaring.
     ///
-    /// # Panics
+    /// # Additional Information
+    ///
+    /// * If panic on overflow is disabled, and the result overflows, the return value will be 0.
     ///
-    /// Panics if the result overflows the type.
+    /// # Reverts
+    ///
+    /// * Reverts if the result overflows the type, if panic on overflow is enabled.
     fn pow(self, exponent: u32) -> Self {
         let one = 0x0000000000000000000000000000000000000000000000000000000000000001u256;
 
@@ -97,13 +125,28 @@ impl Power for u256 {
 
         while exp > 1 {
             if (exp & 1) == 1 {
-                acc = acc * base;
+                // acc = acc * base;
+                let res = u256_checked_mul(acc, base);
+                acc = match res {
+                    Some(val) => val,
+                    None => return u256::zero(),
+                }
             }
             exp = exp >> 1;
-            base = base * base;
+            // base = base * base;
+            let res = u256_checked_mul(base, base);
+            base = match res {
+                Some(val) => val,
+                None => return u256::zero(),
+            }
         }
 
-        acc * base
+        // acc * base
+        let res = u256_checked_mul(acc, base);
+        match res {
+            Some(val) => val,
+            None => u256::zero(),
+        }
     }
 }
 
@@ -118,14 +161,21 @@ impl Power for u64 {
 
 impl Power for u32 {
     fn pow(self, exponent: u32) -> Self {
-        let res = asm(r1: self, r2: exponent, r3) {
+        let mut res = asm(r1: self, r2: exponent, r3) {
             exp r3 r1 r2;
             r3: u64
         };
-        // If panic on wrapping math is enabled, only then revert
-        if panic_on_overflow_enabled() {
-            assert(res <= Self::max().as_u64());
+
+        if res > Self::max().as_u64() {
+            // If panic on wrapping math is enabled, only then revert
+            if panic_on_overflow_enabled() {
+                revert(0);
+            } else {
+                // Follow spec of returning 0 for overflow
+                res = 0;
+            }
         }
+
         asm(r1: res) {
             r1: Self
         }
@@ -134,14 +184,21 @@ impl Power for u32 {
 
 impl Power for u16 {
     fn pow(self, exponent: u32) -> Self {
-        let res = asm(r1: self, r2: exponent, r3) {
+        let mut res = asm(r1: self, r2: exponent, r3) {
             exp r3 r1 r2;
             r3: u64
         };
-        // If panic on wrapping math is enabled, only then revert
-        if panic_on_overflow_enabled() {
-            assert(res <= Self::max().as_u64());
+
+        if res > Self::max().as_u64() {
+            // If panic on wrapping math is enabled, only then revert
+            if panic_on_overflow_enabled() {
+                revert(0);
+            } else {
+                // Follow spec of returning 0 for overflow
+                res = 0;
+            }
         }
+
         asm(r1: res) {
             r1: Self
         }
@@ -150,14 +207,21 @@ impl Power for u16 {
 
 impl Power for u8 {
     fn pow(self, exponent: u32) -> Self {
-        let res = asm(r1: self, r2: exponent, r3) {
+        let mut res = asm(r1: self, r2: exponent, r3) {
             exp r3 r1 r2;
             r3: u64
         };
-        // If panic on wrapping math is enabled, only then revert
-        if panic_on_overflow_enabled() {
-            assert(res <= Self::max().as_u64());
+
+        if res > Self::max().as_u64() {
+            // If panic on wrapping math is enabled, only then revert
+            if panic_on_overflow_enabled() {
+                revert(0);
+            } else {
+                // Follow spec of returning 0 for overflow
+                res = 0;
+            }
         }
+
         asm(r1: res) {
             r1: Self
         }
```

### test/src/in_language_tests/test_programs/math_inline_tests/src/main.sw
```diff
@@ -1,5 +1,7 @@
 library;
 
+use std::flags::disable_panic_on_overflow;
+
 #[test]
 fn math_root_u256() {
     let max_u256 = u256::max();
@@ -819,3 +821,283 @@ fn math_0th_root_fail() {
     };
     log(res);
 }
+
+#[test(should_revert)]
+fn math_u8_overflow_add_revert() {
+    let a = u8::max();
+    let b = a + 1;
+    log(b);
+}
+
+#[test(should_revert)]
+fn math_u16_overflow_add_revert() {
+    let a = u16::max();
+    let b = a + 1;
+    log(b);
+}
+
+#[test(should_revert)]
+fn math_u32_overflow_add_revert() {
+    let a = u32::max();
+    let b = a + 1;
+    log(b);
+}
+
+#[test(should_revert)]
+fn math_u64_overflow_add_revert() {
+    let a = u64::max();
+    let b = a + 1;
+    log(b);
+}
+
+#[test(should_revert)]
+fn math_u256_overflow_add_revert() {
+    let a = u256::max();
+    let b = a + 1;
+    log(b);
+}
+
+#[test(should_revert)]
+fn math_u8_overflow_mul_revert() {
+    let a = u8::max();
+    let b = a * 2;
+    log(b);
+}
+
+#[test(should_revert)]
+fn math_u16_overflow_mul_revert() {
+    let a = u16::max();
+    let b = a * 2;
+    log(b);
+}
+
+#[test(should_revert)]
+fn math_u32_overflow_mul_revert() {
+    let a = u32::max();
+    let b = a * 2;
+    log(b);
+}
+
+#[test(should_revert)]
+fn math_u64_overflow_mul_revert() {
+    let a = u64::max();
+    let b = a * 2;
+    log(b);
+}
+
+#[test(should_revert)]
+fn math_u256_overflow_mul_revert() {
+    let a = u256::max();
+    let b = a * 2;
+    log(b);
+}
+
+#[test]
+fn math_u8_overflow_add() {
+    let _ = disable_panic_on_overflow();
+
+    let a = u8::max();
+    let b = a + 1;
+
+    require(b == 0_u8, b);
+
+    let c = a + 2;
+
+    require(c == 1_u8, c);
+
+    let d = a + u8::max();
+
+    require(d == u8::max() - 1, d);
+
+    let e = a + (u8::max() - 1);
+
+    require(e == u8::max() - 2, e);
+}
+
+#[test]
+fn math_u16_overflow_add() {
+    let _ = disable_panic_on_overflow();
+
+    let a: u16 = u16::max();
+    let b: u16 = a + 1;
+
+    require(b == 0_u16, b);
+
+    let c = a + 2;
+
+    require(c == 1_u16, c);
+
+    let d = a + u16::max();
+
+    require(d == u16::max() - 1, d);
+
+    let e = a + (u16::max() - 1);
+
+    require(e == u16::max() - 2, e);
+}
+
+#[test]
+fn math_u32_overflow_add() {
+    let _ = disable_panic_on_overflow();
+
+    let a = u32::max();
+    let b = a + 1;
+
+    require(b == 0_u32, b);
+
+    let c = a + 2;
+
+    require(c == 1_u32, c);
+
+    let d = a + u32::max();
+
+    require(d == u32::max() - 1, d);
+
+    let e = a + (u32::max() - 1);
+
+    require(e == u32::max() - 2, e);
+}
+
+#[test]
+fn math_u64_overflow_add() {
+    let _ = disable_panic_on_overflow();
+
+    let a = u64::max();
+    let b = a + 1;
+
+    require(b == 0_u64, b);
+
+    let c = a + 2;
+
+    require(c == 1_u64, c);
+
+    let d = a + u64::max();
+
+    require(d == u64::max() - 1, d);
+
+    let e = a + (u64::max() - 1);
+
+    require(e == u64::max() - 2, e);
+}
+
+#[test]
+fn math_u256_overflow_add() {
+    let _ = disable_panic_on_overflow();
+
+    let a = u256::max();
+    let b = a + 1;
+
+    require(b == u256::zero(), b);
+
+    let c = a + 2;
+
+    require(c == 1, c);
+
+    let d = a + u256::max();
+
+    require(d == u256::max() - 1, d);
+
+    let e = a + (u256::max() - 1);
+
+    require(e == u256::max() - 2, e);
+}
+
+#[test]
+fn math_u8_overflow_mul() {
+    let _ = disable_panic_on_overflow();
+
+    let a = (u8::max() / 2) + 1;
+    let b = a * 2;
+
+    require(b == 0_u8, b)
+}
+
+#[test]
+fn math_u16_overflow_mul() {
+    let _ = disable_panic_on_overflow();
+
+    let a = (u16::max() / 2) + 1;
+    let b = a * 2;
+
+    require(b == 0_u16, b)
+}
+
+#[test]
+fn math_u32_overflow_mul() {
+    let _ = disable_panic_on_overflow();
+
+    let a = (u32::max() / 2) + 1;
+    let b = a * 2;
+
+    require(b == 0_u32, b)
+}
+
+#[test]
+fn math_u64_overflow_mul() {
+    let _ = disable_panic_on_overflow();
+
+    let a = (u64::max() / 2) + 1;
+    let b = a * 2;
+
+    require(b == 0_u64, b)
+}
+
+#[test]
+fn math_u256_overflow_mul() {
+    let _ = disable_panic_on_overflow();
+
+    let a = (u256::max() / 2) + 1;
+    let b = a * 2;
+
+    require(b == 0.as_u256(), b);
+}
+
+#[test]
+fn math_u8_overflow_pow() {
+    let _ = disable_panic_on_overflow();
+
+    let a = u8::max();
+    let b = a.pow(2);
+
+    require(b == 0_u8, b);
+}
+
+#[test]
+fn math_u16_overflow_pow() {
+    let _ = disable_panic_on_overflow();
+
+    let a = u16::max();
+    let b = a.pow(2);
+
+    require(b == 0_u16, b);
+}
+
+#[test]
+fn math_u32_overflow_pow() {
+    let _ = disable_panic_on_overflow();
+
+    let a = u32::max();
+    let b = a.pow(2);
+
+    require(b == 0_u32, b);
+}
+
+#[test]
+fn math_u64_overflow_pow() {
+    let _ = disable_panic_on_overflow();
+
+    let a = u64::max();
+    let b = a.pow(2);
+
+    require(b == 0_u64, b);
+}
+
+#[test]
+fn math_u256_overflow_pow() {
+    let _ = disable_panic_on_overflow();
+
+    let a = u256::max();
+    let b = a.pow(2);
+
+    require(b == 0.as_u256(), b);
+}
```
