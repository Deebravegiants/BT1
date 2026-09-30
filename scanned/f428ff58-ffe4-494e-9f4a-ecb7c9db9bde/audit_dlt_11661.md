# [?] units: Fix panic message

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2025-03-19
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/6c614d9320e542e19196753bddc5b124e0274176
Type: security-commit

## Details
units: Fix panic message

Recently I wrote a panic message that included the maximum value of an
integer however I used the max of a 16 bit value for both signed and
unsigned - this is incorrect.

Use the correct values for `u16::MAX` and `i16::MAX`.

## Patch
### units/src/amount/signed.rs
```diff
@@ -152,7 +152,7 @@ impl SignedAmount {
 
         match Self::from_sat(sats) {
             Ok(amount) => amount,
-            Err(_) => panic!("unreachable - 65536 BTC is within range"),
+            Err(_) => panic!("unreachable - 32,767 BTC is within range"),
         }
     }
 
```

### units/src/amount/unsigned.rs
```diff
@@ -152,7 +152,7 @@ impl Amount {
 
         match Self::from_sat(sats) {
             Ok(amount) => amount,
-            Err(_) => panic!("unreachable - 65536 BTC is within range"),
+            Err(_) => panic!("unreachable - 65,535 BTC is within range"),
         }
     }
 
```
