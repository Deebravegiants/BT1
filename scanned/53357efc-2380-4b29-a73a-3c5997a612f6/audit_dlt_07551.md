# [?] fixpoint: correct silent overflow bug

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2023-05-13
Source: https://github.com/penumbra-zone/penumbra/commit/5b6db6568b542ef12ce5a7515045d5d7762b7549
Type: security-commit

## Details
fixpoint: correct silent overflow bug

The bug was in this code:
```
        x1y1.checked_shl(128)
            .and_then(|acc| acc.checked_add(x0y1))
            .and_then(|acc| acc.checked_add(x1y0))
            .and_then(|acc| acc.checked_add(x0y0 >> 128))
            .map(U128x128)
```
The first call was intended to return None when there are nonzero bits in the
high part of the product. But that's not what checked_shl does: the check is on
the shift amount, not the shifted bits. Oops.

Longer-term, we should expand the `Error` type to have numeric errors, and
change the arithmetic operations to return `Result`s. For now, we can correct
this bug and see what other errors in our stack it was hiding.

## Patch
### crypto/src/fixpoint.rs
```diff
@@ -94,8 +94,11 @@ impl U128x128 {
 
     /// Performs checked multiplication, returning `Some` if no overflow occurred.
     pub fn checked_mul(self, rhs: &Self) -> Option<Self> {
-        let [x0, x1] = self.0 .0;
-        let [y0, y1] = rhs.0 .0;
+        // It's important to use `into_words` because the `U256` type has an
+        // unsafe API that makes the limb ordering dependent on the host
+        // endianness.
+        let (x1, x0) = self.0.into_words();
+        let (y1, y0) = rhs.0.into_words();
         let x0 = U256::from(x0);
         let x1 = U256::from(x1);
         let y0 = U256::from(y0);
@@ -113,6 +116,11 @@ impl U128x128 {
         let x1y0 = x1 * y0; // cannot overflow, widening mul
         let x1y1 = x1 * y1; // cannot overflow, widening mul
 
+        let (x1y1_hi, _x1y1_lo) = x1y1.into_words();
+        if x1y1_hi != 0 {
+            return None;
+        }
+
         x1y1.checked_shl(128)
             .and_then(|acc| acc.checked_add(x0y1))
             .and_then(|acc| acc.checked_add(x1y0))
```
