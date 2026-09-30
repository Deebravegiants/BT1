# [?] fix(crash): Fix Nu6.1 blocks crash (#9754)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2025-08-06
Source: https://github.com/ZcashFoundation/zebra/commit/3bac7fd6bbeb74df56d4aa2b14c9916c8de6d98e
Type: security-commit

## Details
fix(crash): Fix Nu6.1 blocks crash (#9754)

* add lockbox deferred amount to total input value in miner_fees_are_valid()

Co-authored-by: Arya <aryasolhi@gmail.com>

* fix hashset coinbase outputs issue

Co-authored-by: Arya <aryasolhi@gmail.com>

---------

Co-authored-by: Arya <aryasolhi@gmail.com>

## Patch
### zebra-consensus/src/block/check.rs
```diff
@@ -268,8 +268,10 @@ pub fn miner_fees_are_valid(
     expected_deferred_pool_balance_change: DeferredPoolBalanceChange,
     network: &Network,
 ) -> Result<(), BlockError> {
-    let transparent_value_balance = zebra_chain::parameters::subsidy::output_amounts(coinbase_tx)
+    let transparent_value_balance = coinbase_tx
+        .outputs()
         .iter()
+        .map(|output| output.value())
         .sum::<Result<Amount<NonNegative>, AmountError>>()
         .map_err(|_| SubsidyError::SumOverflow)?
         .constrain()
@@ -292,6 +294,7 @@ pub fn miner_fees_are_valid(
         (transparent_value_balance - sapling_value_balance - orchard_value_balance
             + expected_deferred_pool_balance_change.value())
         .map_err(|_| SubsidyError::SumOverflow)?;
+
     let total_input_value =
         (expected_block_subsidy + block_miner_fees).map_err(|_| SubsidyError::SumOverflow)?;
 
```
