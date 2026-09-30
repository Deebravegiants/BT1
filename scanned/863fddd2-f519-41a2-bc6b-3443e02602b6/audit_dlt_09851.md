# [?] do the calculation of route spot price in chunks to prevent overflow of u512

## Summary
Severity: Unknown
Chain: Hydration
Component: galacticcouncil/hydration-node
Published: 2024-05-08
Source: https://github.com/galacticcouncil/hydration-node/commit/0564b5affc1c99751519f8f112016ad9b16dc17b
Type: security-commit

## Details
do the calculation of route spot price in chunks to prevent overflow of u512

## Patch
### integration-tests/src/router.rs
```diff
@@ -4140,7 +4140,7 @@ mod route_spot_price {
 					expected_amount_out
 				);
 
-				let spot_price_of_hdx_per_dot = Router::spot_price_with_fee(&trades).unwrap();
+				let spot_price_of_hdx_per_dot = Router::spot_price(&trades).unwrap();
 				let calculated_amount_out = spot_price_of_hdx_per_dot
 					.reciprocal()
 					.unwrap()
@@ -4211,7 +4211,7 @@ mod route_spot_price {
 					expected_amount_out
 				);
 
-				let spot_price_of_hdx_per_dot = Router::spot_price_with_fee(&trades).unwrap();
+				let spot_price_of_hdx_per_dot = Router::spot_price(&trades).unwrap();
 				let calculated_amount_out = spot_price_of_hdx_per_dot
 					.reciprocal()
 					.unwrap()
```

### pallets/route-executor/src/lib.rs
```diff
@@ -855,26 +855,38 @@ impl<T: Config> RouteProvider<T::AssetId> for Pallet<T> {
 }
 impl<T: Config> RouteSpotPriceProvider<T::AssetId> for Pallet<T> {
 	fn spot_price_with_fee(route: &[Trade<T::AssetId>]) -> Option<FixedU128> {
-		let mut prices: Vec<FixedU128> = Vec::with_capacity(route.len());
-		for trade in route {
-			let spot_price_result = T::AMM::calculate_spot_price_with_fee(trade.pool, trade.asset_in, trade.asset_out);
-
-			match spot_price_result {
-				Ok(spot_price) => prices.push(spot_price),
-				Err(_) => return None,
-			}
-		}
-		if prices.is_empty() {
+		if route.is_empty() {
 			return None;
 		}
 
-		let nominator = prices.iter().try_fold(U512::from(1u128), |acc, price| {
-			acc.checked_mul(U512::from(price.into_inner()))
-		})?;
+		let mut nominator = U512::from(1u128);
+		let mut denominator = U512::from(1u128);
+
+		// We aggregate the prices after every 4 hops to prevent overflow of U512
+		for chunk_with_4_hops in route.chunks(4) {
+			let mut prices: Vec<FixedU128> = Vec::with_capacity(chunk_with_4_hops.len());
+			for trade in chunk_with_4_hops {
+				let spot_price_result =
+					T::AMM::calculate_spot_price_with_fee(trade.pool, trade.asset_in, trade.asset_out);
+				match spot_price_result {
+					Ok(spot_price) => prices.push(spot_price),
+					Err(_) => return None,
+				}
+			}
+
+			// Calculate the nominator and denominator for the current chunk
+			let chunk_nominator = prices.iter().try_fold(U512::from(1u128), |acc, price| {
+				acc.checked_mul(U512::from(price.into_inner()))
+			})?;
 
-		let denominator = prices.iter().try_fold(U512::from(1u128), |acc, _price| {
-			acc.checked_mul(U512::from(FixedU128::DIV))
-		})?;
+			let chunk_denominator = prices.iter().try_fold(U512::from(1u128), |acc, _price| {
+				acc.checked_mul(U512::from(FixedU128::DIV))
+			})?;
+
+			// Combine the chunk results with the final results
+			nominator = nominator.checked_mul(chunk_nominator)?;
+			denominator = denominator.checked_mul(chunk_denominator)?;
+		}
 
 		let rat_as_u128 = round_u512_to_rational((nominator, denominator), Rounding::Nearest);
 
```

### pallets/route-executor/src/tests/mod.rs
```diff
@@ -3,3 +3,4 @@ pub mod force_insert_route;
 pub mod mock;
 pub mod sell;
 pub mod set_route;
+pub mod spot_price;
```

### pallets/route-executor/src/tests/spot_price.rs
```diff
@@ -0,0 +1,17 @@
+use crate::tests::mock::*;
+use crate::{Error, Trade};
+use frame_support::pallet_prelude::*;
+use frame_support::{assert_noop, assert_ok};
+use hydradx_traits::router::RouteSpotPriceProvider;
+use hydradx_traits::router::{AssetPair, PoolType};
+use pretty_assertions::assert_eq;
+use sp_runtime::DispatchError::BadOrigin;
+
+#[test]
+fn price_should_be_none_for_empty_route() {
+	ExtBuilder::default().build().execute_with(|| {
+		let price = Router::spot_price_with_fee(&vec![]);
+
+		assert!(price.is_none());
+	});
+}
```
