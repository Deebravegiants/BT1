# [?] Fix crash in `SerializedSignature` formatting

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2026-05-09
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/5b989e8aeea74e7058b2ddf6a9565ef7436b4b69
Type: security-commit

## Details
Fix crash in `SerializedSignature` formatting

The formatting function was calling `fmt_hex_exact!` macro which
requires exact buffer size rather than minimum buffer size causing it to
crash since the length of `SerializedSignature` is conditional.

This fixes it by simply conditionally calling the macro with appropriate
values.

## Patch
### crypto/src/taproot.rs
```diff
@@ -12,7 +12,6 @@ use core::str::FromStr;
 
 #[cfg(feature = "arbitrary")]
 use arbitrary::{Arbitrary, Unstructured};
-use hex_unstable::DisplayHex as _;
 use internals::array::ArrayExt;
 use internals::impl_to_hex_from_lower_hex;
 #[cfg(feature = "serde")]
@@ -157,6 +156,19 @@ impl SerializedSignature {
     #[inline]
     pub fn iter(&self) -> core::slice::Iter<'_, u8> { self.into_iter() }
 
+    fn is_default(&self) -> bool {
+        self.len() != MAX_LEN
+    }
+
+    #[inline]
+    fn fmt_internal(&self, f: &mut fmt::Formatter, case: hex_unstable::Case) -> fmt::Result {
+        if self.is_default() {
+            hex_unstable::fmt_hex_exact!(f, MAX_LEN - 1, self, case)
+        } else {
+            hex_unstable::fmt_hex_exact!(f, MAX_LEN, self, case)
+        }
+    }
+
     /// Constructs new `SerializedSignature` from data and length.
     ///
     /// # Panics
@@ -179,14 +191,14 @@ impl fmt::Debug for SerializedSignature {
 
 impl fmt::Display for SerializedSignature {
     fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
-        hex_unstable::fmt_hex_exact!(f, MAX_LEN, self, hex_unstable::Case::Lower)
+        fmt::LowerHex::fmt(self, f)
     }
 }
 
 impl fmt::LowerHex for SerializedSignature {
     #[inline]
     fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
-        fmt::LowerHex::fmt(&(**self).as_hex(), f)
+        self.fmt_internal(f, hex_unstable::Case::Lower)
     }
 }
 impl_to_hex_from_lower_hex!(SerializedSignature, |signature: &SerializedSignature| signature.len
@@ -195,7 +207,7 @@ impl_to_hex_from_lower_hex!(SerializedSignature, |signature: &SerializedSignatur
 impl fmt::UpperHex for SerializedSignature {
     #[inline]
     fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
-        fmt::UpperHex::fmt(&(**self).as_hex(), f)
+        self.fmt_internal(f, hex_unstable::Case::Upper)
     }
 }
 
```
