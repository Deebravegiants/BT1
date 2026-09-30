# [?] use overflowing to prevent future issues

## Summary
Severity: Unknown
Chain: Hydration
Component: galacticcouncil/hydration-node
Published: 2024-12-18
Source: https://github.com/galacticcouncil/hydration-node/commit/83104b3eedc7fa396b97f882c88f20faca6a9a6b
Type: security-commit

## Details
use overflowing to prevent future issues

## Patch
### pallets/amm-support/src/lib.rs
```diff
@@ -147,7 +147,7 @@ impl<T: Config> Pallet<T> {
 		//TODO: double check what to do when these can fail, we dont really want failing due to this
 		let next_id = IncrementalId::<T>::try_mutate(|current_id| -> Result<IncrementalIdType, DispatchError> {
 			let inc_id = *current_id;
-			*current_id = current_id.checked_add(1).ok_or(ArithmeticError::Overflow)?;
+			*current_id = current_id.overflowing_add(1).0.into();
 			Ok(inc_id)
 		})?;
 
```
