# [?] fix dex calculation overflow with big integer (#484)

## Summary
Severity: Unknown
Chain: Acala
Component: AcalaNetwork/Acala
Published: 2020-10-23
Source: https://github.com/AcalaNetwork/Acala/commit/e1b45d5acd3277fea7e7fea2699cd9a576b6cf05
Type: security-commit

## Details
fix dex calculation overflow with big integer (#484)

## Patch
### modules/dex/Cargo.toml
```diff
@@ -7,6 +7,7 @@ edition = "2018"
 [dependencies]
 serde = { version = "1.0.101", optional = true }
 codec = { package = "parity-scale-codec", version = "1.3.0", default-features = false }
+sp-core = { version = "2.0.0", default-features = false }
 sp-runtime = { version = "2.0.0", default-features = false }
 frame-benchmarking = { version = "2.0.0", default-features = false, optional = true }
 frame-support = { version = "2.0.0", default-features = false }
```

### modules/dex/src/lib.rs
```diff
@@ -16,11 +16,12 @@ use frame_system::{self as system, ensure_signed};
 use orml_traits::{MultiCurrency, MultiCurrencyExtended};
 use orml_utilities::with_transaction_result;
 use primitives::{Balance, CurrencyId, TradingPair};
+use sp_core::U256;
 use sp_runtime::{
-	traits::{AccountIdConversion, One, UniqueSaturatedInto, Zero},
+	traits::{AccountIdConversion, UniqueSaturatedInto, Zero},
 	DispatchError, DispatchResult, FixedPointNumber, ModuleId,
 };
-use sp_std::{prelude::*, vec};
+use sp_std::{convert::TryInto, prelude::*, vec};
 use support::{DEXManager, Price, Ratio};
 
 mod benchmarking;
@@ -314,12 +315,15 @@ impl<T: Trait> Module<T> {
 			let (fee_numerator, fee_denominator) = T::GetExchangeFee::get();
 			let supply_amount_with_fee =
 				supply_amount.saturating_mul(fee_denominator.saturating_sub(fee_numerator).unique_saturated_into());
-			let numerator = supply_amount_with_fee.saturating_mul(target_pool);
-			let denominator = supply_pool
-				.saturating_mul(fee_denominator.unique_saturated_into())
-				.saturating_add(supply_amount_with_fee);
+			let numerator: U256 = U256::from(supply_amount_with_fee).saturating_mul(U256::from(target_pool));
+			let denominator: U256 = U256::from(supply_pool)
+				.saturating_mul(U256::from(fee_denominator))
+				.saturating_add(U256::from(supply_amount_with_fee));
 
-			numerator.checked_div(denominator).unwrap_or_else(Zero::zero)
+			numerator
+				.checked_div(denominator)
+				.and_then(|n| TryInto::<Balance>::try_into(n).ok())
+				.unwrap_or_else(Zero::zero)
 		}
 	}
 
@@ -329,18 +333,18 @@ impl<T: Trait> Module<T> {
 			Zero::zero()
 		} else {
 			let (fee_numerator, fee_denominator) = T::GetExchangeFee::get();
-			let numerator = supply_pool
-				.saturating_mul(target_amount)
-				.saturating_mul(fee_denominator.unique_saturated_into());
-			let denominator = target_pool
-				.saturating_sub(target_amount)
-				.saturating_mul(fee_denominator.saturating_sub(fee_numerator).unique_saturated_into());
+			let numerator: U256 = U256::from(supply_pool)
+				.saturating_mul(U256::from(target_amount))
+				.saturating_mul(U256::from(fee_denominator));
+			let denominator: U256 = U256::from(target_pool)
+				.saturating_sub(U256::from(target_amount))
+				.saturating_mul(U256::from(fee_denominator.saturating_sub(fee_numerator)));
 
 			numerator
 				.checked_div(denominator)
-				.and_then(|r| r.checked_add(One::one()))
-				.unwrap_or_else(Zero::zero) // add 1 to result so that correct the possible
-			                // losses caused by remainder discarding in
+				.and_then(|r| r.checked_add(U256::one())) // add 1 to result so that correct the possible losses caused by remainder discarding in
+				.and_then(|n| TryInto::<Balance>::try_into(n).ok())
+				.unwrap_or_else(Zero::zero)
 		}
 	}
 
```

### modules/dex/src/tests.rs
```diff
@@ -89,6 +89,32 @@ fn get_target_amounts_work() {
 	});
 }
 
+#[test]
+fn calculate_amount_for_big_number_work() {
+	ExtBuilder::default().build().execute_with(|| {
+		LiquidityPool::insert(
+			AUSD_DOT_PAIR,
+			(171_000_000_000_000_000_000_000, 56_000_000_000_000_000_000_000),
+		);
+		assert_eq!(
+			DexModule::get_supply_amount(
+				171_000_000_000_000_000_000_000,
+				56_000_000_000_000_000_000_000,
+				1_000_000_000_000_000_000_000
+			),
+			3_140_495_867_768_595_041_323
+		);
+		assert_eq!(
+			DexModule::get_target_amount(
+				171_000_000_000_000_000_000_000,
+				56_000_000_000_000_000_000_000,
+				3_140_495_867_768_595_041_323
+			),
+			1_000_000_000_000_000_000_000
+		);
+	});
+}
+
 #[test]
 fn get_supply_amounts_work() {
 	ExtBuilder::default().build().execute_with(|| {
```
