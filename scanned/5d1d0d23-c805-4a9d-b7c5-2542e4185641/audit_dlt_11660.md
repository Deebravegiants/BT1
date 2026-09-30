# [?] Fix panic messages in from_sat_i32 and from_sat_u32 to include input value in satoshis

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2025-07-28
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/e064b14514209bdfe7ad02d84620bb86f7b56b61
Type: security-commit

## Details
Fix panic messages in from_sat_i32 and from_sat_u32 to include input value in satoshis

## Patch
### units/src/amount/signed.rs
```diff
@@ -116,7 +116,7 @@ impl SignedAmount {
         let sats = satoshi as i64; // cannot use i64::from in a constfn
         match Self::from_sat(sats) {
             Ok(amount) => amount,
-            Err(_) => panic!("unreachable - 32,767 BTC is within range"),
+            Err(_) => panic!("unreachable - i32 input [-2,147,483,648 to 2,147,483,647 satoshis] is within range"),
         }
     }
 
```

### units/src/amount/unsigned.rs
```diff
@@ -118,7 +118,8 @@ impl Amount {
         let sats = satoshi as u64; // cannot use i64::from in a constfn
         match Self::from_sat(sats) {
             Ok(amount) => amount,
-            Err(_) => panic!("unreachable - 65,536 BTC is within range"),
+            Err(_) =>
+                panic!("unreachable - u32 input [0 to 4,294,967,295 satoshis] is within range"),
         }
     }
 
```
