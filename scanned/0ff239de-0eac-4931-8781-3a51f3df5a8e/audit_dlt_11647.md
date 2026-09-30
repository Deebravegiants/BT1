# [?] Merge rust-bitcoin/rust-bitcoin#6734: units: Prevent panic when parsing non-ASCII target and work hex

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2026-08-15
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/f4378f407feea82e27e41a6f900a4c8005e260a5
Type: security-commit

## Details
Merge rust-bitcoin/rust-bitcoin#6734: units: Prevent panic when parsing non-ASCII target and work hex

bd7d8653c2600bf4cff6361823d67c5c6cab994f units: Prevent panic when parsing non-ASCII target and work hex (questfever)

Pull request description:

  ## Summary
  
  Prevent `Target` and `Work` hex parsing from panicking on certain non-ASCII UTF-8 inputs.
  
  Add a regression test verifying that invalid non-ASCII hex input is returned as an error.
  
  ## Details
  
  The U256 hex parser uses `str::len()`, which returns the UTF-8 byte length, to calculate the boundary between its high and low halves:
  
  ```rust
  let high_len = s.len() - 32;
  let high_s = &s[..high_len];
  let low_s = &s[high_len..];
  ```
  
  
  For an input such as:
  
  `é0000000000000000000000000000000`
  
  
  the string contains 32 characters but 33 bytes. This makes `high_len == 1`, which falls inside the two-byte UTF-8 encoding of `é`.
  
  Slicing the string at that offset therefore panics.
  
  
  This path is reachable through the public `Target::{from_hex, from_unprefixed_hex}` and `Work::{from_hex, from_unprefixed_hex}` APIs. Invalid hexadecimal input should produce an error rather than panic.
  
  
  The parser now rejects non-ASCII input before splitting the string.
  
  
  ## Testing
  
  - Added a regression test for the non-ASCII input above.
  - Ran cargo test -p bitcoin-units --all-features.


ACKs for top commit:
  apoelstra:
    ACK bd7d8653c2600bf4cff6361823d67c5c6cab994f; successfully ran local tests


Tree-SHA512: 9e579ee9cafd889cd8b386e114636df08acfafef3eef74d7cd92d5dd165d653352f1eba5f5d1312fa253f036477da900bf26a3b951a795623ba7422f69445c7c

## Patch
### units/src/parse_int.rs
```diff
@@ -76,7 +76,7 @@ fn int<T: Integer, S: AsRef<str> + Into<InputString>>(s: S) -> Result<T, ParseIn
     s.as_ref().parse().map_err(|error| {
         ParseIntError {
             input: s.into(),
-            bits: u8::try_from(core::mem::size_of::<T>() * 8).expect("max is 128 bits for u128"),
+            bits: u16::try_from(core::mem::size_of::<T>() * 8).expect("max is 128 bits for u128"),
             // We detect if the type is signed by checking if -1 can be represented by it
             // this way we don't have to implement special traits and optimizer will get rid of the
             // computation.
@@ -365,6 +365,19 @@ pub(crate) fn hex_u256_unprefixed(s: &str) -> Result<crate::pow::U256, Unprefixe
 }
 
 pub(crate) fn hex_u256_unchecked(s: &str) -> Result<crate::pow::U256, ParseIntError> {
+    // We cannot use byte offsets into `s` if it is not ASCII.
+    if !s.is_ascii() {
+        // We want the `ParseIntError`; use u128 to get it since we know the string is not ASCII.
+        return u128::from_str_radix(s, 16)
+            .map_err(|error| ParseIntError {
+                input: s.into(),
+                bits: 256,
+                is_signed: false,
+                source: error,
+            })
+            .map(crate::pow::U256::from);
+    }
+
     let (high, low) = if s.len() <= 32 {
         let low = hex_u128_unchecked(s)?;
         (0, low)
@@ -418,7 +431,7 @@ pub mod error {
     pub struct ParseIntError {
         pub(crate) input: InputString,
         // for displaying - see Display impl with nice error message below
-        pub(crate) bits: u8,
+        pub(crate) bits: u16,
         // We could represent this as a single bit, but it wouldn't actually decrease the cost of moving
         // the struct because String contains pointers so there will be padding of bits at least
         // pointer_size - 1 bytes: min 1B in practice.
@@ -617,20 +630,21 @@ mod tests {
     fn parse_int_panic_when_populating_bits() {
         // Fields in the test type are never used
         #[allow(dead_code)]
-        struct TestTypeLargerThanU128(u128, u128);
-        impl_integer!(TestTypeLargerThanU128);
-        impl FromStr for TestTypeLargerThanU128 {
+        struct TestTypeWithMoreThanU16Bits([u8; 8192]);
+        impl_integer!(TestTypeWithMoreThanU16Bits);
+        impl FromStr for TestTypeWithMoreThanU16Bits {
             type Err = core::num::ParseIntError;
 
             fn from_str(_: &str) -> Result<Self, Self::Err> {
-                "Always invalid for testing".parse::<u32>().map(|_| Self(0, 0))
+                "Always invalid for testing".parse::<u32>().map(|_| Self([0; 8192]))
             }
         }
-        impl From<i8> for TestTypeLargerThanU128 {
-            fn from(_: i8) -> Self { Self(0, 0) }
+        impl From<i8> for TestTypeWithMoreThanU16Bits {
+            fn from(_: i8) -> Self { Self([0; 8192]) }
         }
 
-        let result = panic::catch_unwind(|| int_from_str::<TestTypeLargerThanU128>("not a number"));
+        let result =
+            panic::catch_unwind(|| int_from_str::<TestTypeWithMoreThanU16Bits>("not a number"));
         assert!(result.is_err());
     }
 
@@ -766,6 +780,12 @@ mod tests {
         assert!(hex_u128_unchecked("deadbeefabcdffffdeadbeefabcdffff1").is_err());
     }
 
+    #[test]
+    fn parse_u256_from_hex_non_ascii_reports_bit_length() {
+        let error = hex_u256_unchecked("é0000000000000000000000000000000").unwrap_err();
+        assert_eq!(error.bits, 256);
+    }
+
     #[test]
     #[cfg(feature = "alloc")]
     fn error_display_is_non_empty() {
```

### units/tests/parse.rs
```diff
@@ -6,7 +6,7 @@ use bitcoin_units::amount::{Amount, SignedAmount};
 use bitcoin_units::locktime::{absolute, relative};
 use bitcoin_units::{
     BlockHeight, BlockHeightInterval, BlockMtp, BlockMtpInterval, BlockTime, CompactTarget,
-    Sequence, Weight,
+    Sequence, Target, Weight, Work,
 };
 
 /// Tests `from_hex`/`from_unprefixed_hex` for an integer wrapper type.
@@ -112,6 +112,17 @@ test_hex_parse! {
     signed_amount, SignedAmount, "00000001", SignedAmount::from_sat(1).unwrap(), from_sat_hex, from_sat_unprefixed_hex;
 }
 
+#[test]
+fn target_and_work_hex_with_non_ascii_errors() {
+    const UNPREFIXED: &str = "é0000000000000000000000000000000";
+    const PREFIXED: &str = "0xé0000000000000000000000000000000";
+
+    assert!(Target::from_unprefixed_hex(UNPREFIXED).is_err());
+    assert!(Target::from_hex(PREFIXED).is_err());
+    assert!(Work::from_unprefixed_hex(UNPREFIXED).is_err());
+    assert!(Work::from_hex(PREFIXED).is_err());
+}
+
 /// Tests that hex parsing rejects out-of-range values for types with constrained ranges.
 mod hex_out_of_range {
     use super::*;
```
