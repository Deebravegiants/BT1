# [?] Fix overflow bug in `Weight` constructors

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2025-08-16
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/aa086a0a01bcae252de39a461de9286b3b9adee8
Type: security-commit

## Details
Fix overflow bug in `Weight` constructors

This fixes an overflow bug which occured when these constructors were
used to construct a `Weight` of max value. Since `Weight` is a `u64`
under the hood, the constructors panicked during the attempt to add
to the max weight value

## Patch
### units/src/weight.rs
```diff
@@ -105,14 +105,14 @@ impl Weight {
     pub const fn to_kwu_floor(self) -> u64 { self.to_wu() / 1000 }
 
     /// Converts to kilo weight units rounding up.
-    pub const fn to_kwu_ceil(self) -> u64 { (self.to_wu() + 999) / 1000 }
+    pub const fn to_kwu_ceil(self) -> u64 { self.to_wu().saturating_add(999) / 1000 }
 
     /// Converts to vB rounding down.
     pub const fn to_vbytes_floor(self) -> u64 { self.to_wu() / Self::WITNESS_SCALE_FACTOR }
 
     /// Converts to vB rounding up.
     pub const fn to_vbytes_ceil(self) -> u64 {
-        (self.to_wu() + Self::WITNESS_SCALE_FACTOR - 1) / Self::WITNESS_SCALE_FACTOR
+        self.to_wu().saturating_add(Self::WITNESS_SCALE_FACTOR - 1) / Self::WITNESS_SCALE_FACTOR
     }
 
     /// Checked addition.
@@ -387,6 +387,7 @@ mod tests {
     fn to_kwu_ceil() {
         assert_eq!(Weight::from_wu(1_000).to_kwu_ceil(), 1);
         assert_eq!(Weight::from_wu(1_001).to_kwu_ceil(), 2);
+        assert_eq!(Weight::MAX.to_kwu_ceil(), u64::MAX / 1_000);
     }
 
     #[test]
@@ -399,6 +400,7 @@ mod tests {
     fn to_vb_ceil() {
         assert_eq!(Weight::from_wu(4).to_vbytes_ceil(), 1);
         assert_eq!(Weight::from_wu(5).to_vbytes_ceil(), 2);
+        assert_eq!(Weight::MAX.to_vbytes_ceil(), u64::MAX / Weight::WITNESS_SCALE_FACTOR);
     }
 
     #[test]
```
