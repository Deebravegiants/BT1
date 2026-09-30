# [?] process slashings: fix subtraction overflow

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2019-06-17
Source: https://github.com/sigp/lighthouse/commit/9cec5dc073ae4fa4608b787c1b624589add92fd0
Type: security-commit

## Details
process slashings: fix subtraction overflow

## Patch
### eth2/state_processing/src/per_epoch_processing/process_slashings.rs
```diff
@@ -15,8 +15,8 @@ pub fn process_slashings<T: EthSpec>(
     let total_penalities = total_at_end - total_at_start;
 
     for (index, validator) in state.validator_registry.iter().enumerate() {
-        let should_penalize = current_epoch.as_usize()
-            == validator.withdrawable_epoch.as_usize() - T::LatestSlashedExitLength::to_usize() / 2;
+        let should_penalize = current_epoch.as_usize() + T::LatestSlashedExitLength::to_usize() / 2
+            == validator.withdrawable_epoch.as_usize();
 
         if validator.slashed && should_penalize {
             let effective_balance = state.get_effective_balance(index, spec)?;
```
