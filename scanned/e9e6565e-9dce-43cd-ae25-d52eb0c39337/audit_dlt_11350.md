# [?] fix: Fixed several vulnerabilities in U128, added some tests (#5024)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-05-14
Source: https://github.com/noir-lang/noir/commit/e5ab24d6a4154d11b3c8ae08f4431b7b93c76f23
Type: security-commit

## Details
fix: Fixed several vulnerabilities in U128, added some tests (#5024)

# Description

## Summary\*

I added the tests for construction and depedent functions, unconstrained
division and wrapping multiplication, fixing several bugs. I also added
a directory with the bugs so that it's easier to dive into what sort of
issues we come across in the future.

## Documentation\*

Check one:
- [ ] No documentation needed.
- [x] Documentation included in this PR.
- [ ] **[For Experimental Features]** Documentation to be submitted in a
separate PR.

# PR Checklist\*

- [x] I have tested the changes locally.
- [x] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

## Patch
### noir_stdlib/src/uint128.nr
```diff
@@ -1,8 +1,9 @@
 use crate::ops::{Add, Sub, Mul, Div, Rem, Not, BitOr, BitAnd, BitXor, Shl, Shr};
 use crate::cmp::{Eq, Ord, Ordering};
+use crate::println;
 
 global pow64 : Field = 18446744073709551616; //2^64;
-
+global pow63 : Field = 9223372036854775808; // 2^63;
 struct U128 {
     lo: Field,
     hi: Field,
@@ -20,6 +21,13 @@ impl U128 {
         U128::from_u64s_le(lo, hi)
     }
 
+    pub fn zero() -> U128 {
+        U128 { lo: 0, hi: 0 }
+    }
+
+    pub fn one() -> U128 {
+        U128 { lo: 1, hi: 0 }
+    }
     pub fn from_le_bytes(bytes: [u8; 16]) -> U128 {
         let mut lo = 0;
         let mut base = 1;
@@ -87,27 +95,44 @@ impl U128 {
         U128 { lo: lo as Field, hi: hi as Field }
     }
 
+    unconstrained fn uconstrained_check_is_upper_ascii(ascii: u8) -> bool {
+        ((ascii >= 65) & (ascii <= 90)) // Between 'A' and 'Z'
+    }
+
     fn decode_ascii(ascii: u8) -> Field {
         if ascii < 58 {
             ascii - 48
-        } else if ascii < 71 {
-            ascii - 55
         } else {
+            let ascii = ascii + 32 * (U128::uconstrained_check_is_upper_ascii(ascii) as u8);
+            assert(ascii >= 97); // enforce >= 'a'
+            assert(ascii <= 102); // enforce <= 'f'
             ascii - 87
         } as Field
     }
 
+    // TODO: Replace with a faster version. 
+    // A circuit that uses this function can be slow to compute
+    // (we're doing up to 127 calls to compute the quotient)
     unconstrained fn unconstrained_div(self: Self, b: U128) -> (U128, U128) {
-        if self < b {
-            (U128::from_u64s_le(0, 0), self)
+        if b == U128::zero() {
+            // Return 0,0 to avoid eternal loop
+            (U128::zero(), U128::zero())
+        } else if self < b {
+            (U128::zero(), self)
+        } else if self == b {
+            (U128::one(), U128::zero())
         } else {
-            //TODO check if this can overflow?
-            let (q,r) = self.unconstrained_div(b * U128::from_u64s_le(2, 0));
+            let (q,r) = if b.hi as u64 >= pow63 as u64 {
+                // The result of multiplication by 2 would overflow
+                (U128::zero(), self)
+            } else {
+                self.unconstrained_div(b * U128::from_u64s_le(2, 0))
+            };
             let q_mul_2 = q * U128::from_u64s_le(2, 0);
             if r < b {
                 (q_mul_2, r)
             } else {
-                (q_mul_2 + U128::from_u64s_le(1, 0), r - b)
+                (q_mul_2 + U128::one(), r - b)
             }
         }
     }
@@ -129,11 +154,7 @@ impl U128 {
         let low = self.lo * b.lo;
         let lo = low as u64 as Field;
         let carry = (low - lo) / pow64;
-        let high = if crate::field::modulus_num_bits() as u32 > 196 {
-            (self.lo + self.hi) * (b.lo + b.hi) - low + carry
-        } else {
-            self.lo * b.hi + self.hi * b.lo + carry
-        };
+        let high = self.lo * b.hi + self.hi * b.lo + carry;
         let hi = high as u64 as Field;
         U128 { lo, hi }
     }
@@ -294,8 +315,8 @@ impl Shr for U128 {
     } 
 }
 
-mod test {
-    use crate::uint128::{U128, pow64};
+mod tests {
+    use crate::uint128::{U128, pow64, pow63};
 
     #[test]
     fn test_not() {
@@ -309,4 +330,197 @@ mod test {
         let not_not_num = not_num.not();
         assert_eq(num, not_not_num);
     }
+    #[test]
+    fn test_construction() {
+        // Check little-endian u64 is inversed with big-endian u64 construction
+        let a = U128::from_u64s_le(2, 1);
+        let b = U128::from_u64s_be(1, 2);
+        assert_eq(a, b);
+        // Check byte construction is equivalent
+        let c = U128::from_le_bytes([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]);
+        let d = U128::from_u64s_le(0x0706050403020100, 0x0f0e0d0c0b0a0908);
+        assert_eq(c, d);
+    }
+    #[test]
+    fn test_byte_decomposition() {
+        let a = U128::from_u64s_le(0x0706050403020100, 0x0f0e0d0c0b0a0908);
+        // Get big-endian and little-endian byte decompostions
+        let le_bytes_a= a.to_le_bytes();
+        let be_bytes_a= a.to_be_bytes();
+
+        // Check equivalence
+        for i in 0..16 {
+            assert_eq(le_bytes_a[i], be_bytes_a[15 - i]);
+        }
+        // Reconstruct U128 from byte decomposition
+        let b= U128::from_le_bytes(le_bytes_a);
+        // Check that it's the same element
+        assert_eq(a, b);
+    }
+    #[test]
+    fn test_hex_constuction() {
+        let a = U128::from_u64s_le(0x1, 0x2);
+        let b = U128::from_hex("0x20000000000000001");
+        assert_eq(a, b);
+
+        let c= U128::from_hex("0xffffffffffffffffffffffffffffffff");
+        let d= U128::from_u64s_le(0xffffffffffffffff, 0xffffffffffffffff);
+        assert_eq(c, d);
+
+        let e= U128::from_hex("0x00000000000000000000000000000000");
+        let f= U128::from_u64s_le(0, 0);
+        assert_eq(e, f);
+    }
+
+    // Ascii decode tests
+
+    #[test]
+    fn test_ascii_decode_correct_range() {
+        // '0'..'9' range
+        for i in 0..10 {
+            let decoded= U128::decode_ascii(48 + i);
+            assert_eq(decoded, i as Field);
+        }
+        // 'A'..'F' range
+        for i in 0..6 {
+            let decoded = U128::decode_ascii(65 + i);
+            assert_eq(decoded, (i + 10) as Field);
+        }
+        // 'a'..'f' range
+        for i in 0..6 {
+            let decoded = U128::decode_ascii(97 + i);
+            assert_eq(decoded, (i + 10) as Field);
+        }
+    }
+
+    #[test(should_fail)]
+    fn test_ascii_decode_range_less_than_48_fails_0() {
+        crate::println(U128::decode_ascii(0));
+    }
+    #[test(should_fail)]
+    fn test_ascii_decode_range_less_than_48_fails_1() {
+        crate::println(U128::decode_ascii(47));
+    }
+
+    #[test(should_fail)]
+    fn test_ascii_decode_range_58_64_fails_0() {
+        let _ = U128::decode_ascii(58);
+    }
+    #[test(should_fail)]
+    fn test_ascii_decode_range_58_64_fails_1() {
+        let _ = U128::decode_ascii(64);
+    }
+    #[test(should_fail)]
+    fn test_ascii_decode_range_71_96_fails_0() {
+        let _ = U128::decode_ascii(71);
+    }
+    #[test(should_fail)]
+    fn test_ascii_decode_range_71_96_fails_1() {
+        let _ = U128::decode_ascii(96);
+    }
+    #[test(should_fail)]
+    fn test_ascii_decode_range_greater_than_102_fails() {
+        let _ = U128::decode_ascii(103);
+    }
+
+    #[test(should_fail)]
+    fn test_ascii_decode_regression() {
+        // This code will actually fail because of ascii_decode,
+        // but in the past it was possible to create a value > (1<<128)
+        let a = U128::from_hex("0x~fffffffffffffffffffffffffffffff");
+        let b:Field= a.to_integer();
+        let c= b.to_le_bytes(17);
+        assert(c[16] != 0);
+    }
+
+    #[test]
+    fn test_unconstrained_div() {
+        // Test the potential overflow case
+        let a= U128::from_u64s_le(0x0, 0xffffffffffffffff);
+        let b= U128::from_u64s_le(0x0, 0xfffffffffffffffe);
+        let c= U128::one();
+        let d= U128::from_u64s_le(0x0, 0x1);
+        let (q,r) = a.unconstrained_div(b);
+        assert_eq(q, c);
+        assert_eq(r, d);
+
+        let a = U128::from_u64s_le(2, 0);
+        let b = U128::one();
+        // Check the case where a is a multiple of b
+        let (c,d ) = a.unconstrained_div(b);
+        assert_eq((c, d), (a, U128::zero()));
+
+        // Check where b is a multiple of a
+        let (c,d) = b.unconstrained_div(a);
+        assert_eq((c, d), (U128::zero(), b));
+
+        // Dividing by zero returns 0,0
+        let a = U128::from_u64s_le(0x1, 0x0);
+        let b = U128::zero();
+        let (c,d)= a.unconstrained_div(b);
+        assert_eq((c, d), (U128::zero(), U128::zero()));
+
+        // Dividing 1<<127 by 1<<127 (special case)
+        let a = U128::from_u64s_le(0x0, pow63 as u64);
+        let b = U128::from_u64s_le(0x0, pow63 as u64);
+        let (c,d )= a.unconstrained_div(b);
+        assert_eq((c, d), (U128::one(), U128::zero()));
+    }
+
+    #[test]
+    fn integer_conversions() {
+        // Maximum
+        let start:Field = 0xffffffffffffffffffffffffffffffff;
+        let a = U128::from_integer(start);
+        let end = a.to_integer();
+        assert_eq(start, end);
+
+        // Minimum
+        let start:Field = 0x0;
+        let a = U128::from_integer(start);
+        let end = a.to_integer();
+        assert_eq(start, end);
+
+        // Low limb
+        let start:Field = 0xffffffffffffffff;
+        let a = U128::from_integer(start);
+        let end = a.to_integer();
+        assert_eq(start, end);
+
+        // High limb
+        let start:Field = 0xffffffffffffffff0000000000000000;
+        let a = U128::from_integer(start);
+        let end = a.to_integer();
+        assert_eq(start, end);
+    }
+    #[test]
+    fn test_wrapping_mul() {
+        // 1*0==0
+        assert_eq(U128::zero(), U128::zero().wrapping_mul(U128::one()));
+
+        // 0*1==0
+        assert_eq(U128::zero(), U128::one().wrapping_mul(U128::zero()));
+
+        // 1*1==1
+        assert_eq(U128::one(), U128::one().wrapping_mul(U128::one()));
+
+        // 0 * ( 1 << 64 ) ==  0
+        assert_eq(U128::zero(), U128::zero().wrapping_mul(U128::from_u64s_le(0, 1)));
+
+        // ( 1 << 64 ) * 0 == 0
+        assert_eq(U128::zero(), U128::from_u64s_le(0, 1).wrapping_mul(U128::zero()));
+
+        // 1 * ( 1 << 64 ) == 1 << 64
+        assert_eq(U128::from_u64s_le(0, 1), U128::from_u64s_le(0, 1).wrapping_mul(U128::one()));
+
+        // ( 1 << 64 ) * 1 == 1 << 64
+        assert_eq(U128::from_u64s_le(0, 1), U128::one().wrapping_mul(U128::from_u64s_le(0, 1)));
+
+        // ( 1 << 64 ) * ( 1 << 64 ) == 1 << 64
+        assert_eq(U128::zero(), U128::from_u64s_le(0, 1).wrapping_mul(U128::from_u64s_le(0, 1)));
+        // -1 * -1 == 1
+        assert_eq(
+            U128::one(), U128::from_u64s_le(0xffffffffffffffff, 0xffffffffffffffff).wrapping_mul(U128::from_u64s_le(0xffffffffffffffff, 0xffffffffffffffff))
+        );
+    }
 }
```

### security/insectarium/noir_stdlib.md
```diff
@@ -0,0 +1,61 @@
+# Bugs found in Noir stdlib
+
+## U128
+
+### decode_ascii
+Old **decode_ascii** function didn't check that the values of individual bytes in the string were just in the range of [0-9a-f-A-F].
+```rust
+fn decode_ascii(ascii: u8) -> Field {
+    if ascii < 58 {
+        ascii - 48
+    } else if ascii < 71 {
+        ascii - 55
+    } else {
+        ascii - 87
+    } as Field
+}
+```
+Since the function used the assumption that decode_ascii returns values in range [0,15] to construct **lo** and **hi** it was possible to overflow these 64-bit limbs.
+
+### unconstrained_div
+```rust
+ unconstrained fn unconstrained_div(self: Self, b: U128) -> (U128, U128) {
+        if self < b {
+            (U128::from_u64s_le(0, 0), self)
+        } else {
+            //TODO check if this can overflow?
+            let (q,r) = self.unconstrained_div(b * U128::from_u64s_le(2, 0));
+            let q_mul_2 = q * U128::from_u64s_le(2, 0);
+            if r < b {
+                (q_mul_2, r)
+            } else {
+                (q_mul_2 + U128::from_u64s_le(1, 0), r - b)
+            }
+        }
+    }
+```
+There were 2 issues in unconstrained_div:
+1) Attempting to divide by zero resulted in an infinite loop, because there was no check.
+2) $a >= 2^{127}$ cause the function to multiply b to such power of 2 that the result would be more than $2^{128}$ and lead to assertion failure even though it was a legitimate input
+
+N.B. initial fix by Rumata888 also had an edgecase missing for when a==b and b >= (1<<127).
+
+### wrapping_mul
+```rust
+fn wrapping_mul(self: Self, b: U128) -> U128 {
+        let low = self.lo * b.lo;
+        let lo = low as u64 as Field;
+        let carry = (low - lo) / pow64;
+        let high = if crate::field::modulus_num_bits() as u32 > 196 {
+            (self.lo + self.hi) * (b.lo + b.hi) - low + carry // Bug
+        } else {
+            self.lo * b.hi + self.hi * b.lo + carry
+        };
+        let hi = high as u64 as Field;
+        U128 { lo, hi }
+    }
+```
+Wrapping mul had the code copied from regular mul barring the assertion that the product of high limbs is zero. Because that check was removed, the optimized path for moduli > 196 bits was incorrect, since it included their product (as at least one of them was supposed to be zero originally, but not for wrapping multiplication)
+
+
+
```
