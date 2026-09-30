# [?] protocol: in open/close, avoid throwing underflow, limit collateral to 0

## Summary
Severity: Unknown
Chain: Solana
Component: velocity-exchange/protocol-v2
Published: 2021-10-25
Source: https://github.com/velocity-exchange/protocol-v2/commit/a15fa6cc645efdcf6c3e61e5a66b6261b5a4b21c
Type: security-commit

## Details
protocol: in open/close, avoid throwing underflow, limit collateral to 0

## Patch
### programs/clearing_house/src/lib.rs
```diff
@@ -637,7 +637,7 @@ pub mod clearing_house {
                 .ok_or_else(math_error!())?;
         }
 
-        user.collateral = user.collateral.checked_sub(fee).ok_or_else(math_error!())?;
+        user.collateral = user.collateral.checked_sub(fee).or(Some(0))?;
 
         user.total_fee_paid = user
             .total_fee_paid
@@ -848,7 +848,7 @@ pub mod clearing_house {
             .checked_add(fee)
             .ok_or_else(math_error!())?;
 
-        user.collateral = user.collateral.checked_sub(fee).ok_or_else(math_error!())?;
+        user.collateral = user.collateral.checked_sub(fee).or(Some(0))?;
 
         user.total_fee_paid = user
             .total_fee_paid
```
