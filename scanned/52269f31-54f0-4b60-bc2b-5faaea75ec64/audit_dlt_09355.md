# [?] fix out of bounds (#153)

## Summary
Severity: Unknown
Chain: Acala
Component: AcalaNetwork/Acala
Published: 2020-03-10
Source: https://github.com/AcalaNetwork/Acala/commit/7125a4683c75cc2ed869ffc9b4ae6df8e3bd73c7
Type: security-commit

## Details
fix out of bounds (#153)

## Patch
### modules/cdp_engine/src/lib.rs
```diff
@@ -302,16 +302,17 @@ impl<T: Trait> Module<T> {
 						runtime_io::offchain::timestamp().add(Duration::from_millis(LOCK_EXPIRE_DURATION));
 
 					Ok(OffchainWorkerLock {
-						previous_position: rng.pick_u32(collateral_currency_ids.len() as u32),
+						previous_position: rng.pick_u32(collateral_currency_ids.len().saturating_sub(1) as u32),
 						expire_timestamp: expire_timestamp,
 					})
 				}
 				Some(Some(lock)) if runtime_io::offchain::timestamp() >= lock.expire_timestamp => {
-					let execute_position = if lock.previous_position < collateral_currency_ids.len() as u32 - 1 {
-						lock.previous_position + 1
-					} else {
-						0
-					};
+					let execute_position =
+						if lock.previous_position < collateral_currency_ids.len().saturating_sub(1) as u32 {
+							lock.previous_position + 1
+						} else {
+							0
+						};
 					let expire_timestamp =
 						runtime_io::offchain::timestamp().add(Duration::from_millis(LOCK_EXPIRE_DURATION));
 
@@ -421,6 +422,11 @@ impl<T: Trait> Module<T> {
 	}
 
 	fn _offchain_worker(block_number: T::BlockNumber) -> Result<(), OffchainErr> {
+		let collateral_currency_ids = T::CollateralCurrencyIds::get();
+		if collateral_currency_ids.len().is_zero() {
+			return Ok(());
+		}
+
 		// check if we are a potential validator
 		if !runtime_io::offchain::is_validator() {
 			return Err(OffchainErr::NotValidator);
@@ -434,7 +440,6 @@ impl<T: Trait> Module<T> {
 		} = Self::acquire_offchain_worker_lock()?;
 
 		// start
-		let collateral_currency_ids = T::CollateralCurrencyIds::get();
 		let currency_id = collateral_currency_ids[(previous_position as usize)];
 
 		if !Self::is_shutdown() {
```
