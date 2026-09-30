# [?] Merge rust-bitcoin/rust-bitcoin#4728: fix: panic messages in from_sat_i32 and from_sat_u32 to use satoshi limits

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2025-12-10
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/7c31c2548dc096018898759d1e5580112cd2cfa4
Type: security-commit

## Details
Merge rust-bitcoin/rust-bitcoin#4728: fix: panic messages in from_sat_i32 and from_sat_u32 to use satoshi limits

e064b14514209bdfe7ad02d84620bb86f7b56b61 Fix panic messages in from_sat_i32 and from_sat_u32 to include input value in satoshis (nahem)

Pull request description:

  **Fixes**: #4727 
  
  Updates panic messages in `from_sat_i32` and `from_sat_u32` to fix incorrect "32,767 BTC" reference..
  - `from_sat_i32`: "unreachable - i32 input [-2,147,483,648 to 2,147,483,647 satoshis] is within range"
  - `from_sat_u32`: "unreachable - u32 input [0 to 4,294,967,295 satoshis] is within range"
  
  Also updates docstrings to emphasize satoshi ranges, removing BTC approximations as it's not relevant for the conversion. 
  
  **Testing**:
  - Ran `cargo test` to confirm no regressions.


ACKs for top commit:
  apoelstra:
    ACK e064b14514209bdfe7ad02d84620bb86f7b56b61; successfully ran local tests
  jrakibi:
    ACK e064b14514209bdfe7ad02d84620bb86f7b56b61


Tree-SHA512: a59a89d75947ffb47bae25cd55d07559ac392cbffaa2bb90c482d62311ad2d50b6b1c60847d00283ff3585de878bbb9eb068ad6c98345f27d78d519db43a57b6

## Patch
### units/src/amount/signed.rs
```diff
@@ -118,7 +118,7 @@ impl SignedAmount {
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
@@ -123,7 +123,8 @@ impl Amount {
         let sats = const_casts::u32_to_u64(satoshi);
         match Self::from_sat(sats) {
             Ok(amount) => amount,
-            Err(_) => panic!("unreachable - 65,536 BTC is within range"),
+            Err(_) =>
+                panic!("unreachable - u32 input [0 to 4,294,967,295 satoshis] is within range"),
         }
     }
 
```
