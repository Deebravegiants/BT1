# [?] Merge pull request #1178 from galacticcouncil/fix/price-provider-overflow

## Summary
Severity: Unknown
Chain: Hydration
Component: galacticcouncil/hydration-node
Published: 2025-08-26
Source: https://github.com/galacticcouncil/hydration-node/commit/47b74df022349b0bfefb9d575c19fec7f1e23ab3
Type: security-commit

## Details
Merge pull request #1178 from galacticcouncil/fix/price-provider-overflow

fix: possible overflow in price provider for given route

## Patch
### Cargo.lock
```diff
@@ -4618,7 +4618,7 @@ dependencies = [
 
 [[package]]
 name = "hydradx-adapters"
-version = "1.9.0"
+version = "1.9.1"
 dependencies = [
  "cumulus-pallet-parachain-system",
  "cumulus-primitives-core",
```

### runtime/adapters/Cargo.toml
```diff
@@ -1,6 +1,6 @@
 [package]
 name = "hydradx-adapters"
-version = "1.9.0"
+version = "1.9.1"
 description = "Structs and other generic types for building runtimes."
 authors = ["GalacticCouncil"]
 edition = "2021"
```

### runtime/adapters/src/lib.rs
```diff
@@ -630,17 +630,30 @@ where
 			return None;
 		}
 
-		let nominator = prices
-			.iter()
-			.try_fold(U512::from(1u128), |acc, price| acc.checked_mul(U512::from(price.n)))?;
-
-		let denominator = prices
-			.iter()
-			.try_fold(U512::from(1u128), |acc, price| acc.checked_mul(U512::from(price.d)))?;
+		// To avoid overflows - process in chunks of 4 prices
+		let calculate_price_product = {
+			fn inner(prices: &[EmaPrice]) -> Option<EmaPrice> {
+				if prices.len() <= 4 {
+					// Base case: process directly
+					let nom = prices
+						.iter()
+						.try_fold(U512::from(1u128), |acc, price| acc.checked_mul(U512::from(price.n)))?;
+					let den = prices
+						.iter()
+						.try_fold(U512::from(1u128), |acc, price| acc.checked_mul(U512::from(price.d)))?;
+					Some(round_u512_to_rational((nom, den), Rounding::Nearest).into())
+				} else {
+					// Recursive case: chunk and recurse
+					let chunk_results: Vec<EmaPrice> =
+						prices.chunks(4).map(|chunk| inner(chunk)).collect::<Option<Vec<_>>>()?;
 
-		let rat_as_u128 = round_u512_to_rational((nominator, denominator), Rounding::Nearest);
+					inner(&chunk_results)
+				}
+			}
+			inner
+		};
 
-		Some(EmaPrice::new(rat_as_u128.0, rat_as_u128.1))
+		calculate_price_product(&prices)
 	}
 }
 
```

### runtime/adapters/src/tests/mod.rs
```diff
@@ -1,3 +1,4 @@
 pub mod mock;
+mod prices;
 pub mod trader;
 pub mod xcm_exchange;
```

### runtime/adapters/src/tests/prices.rs
```diff
@@ -0,0 +1,145 @@
+use crate::OraclePriceProvider;
+use frame_support::parameter_types;
+use hydra_dx_math::ema::EmaPrice;
+use hydradx_traits::router::{PoolType, Trade};
+use hydradx_traits::{AggregatedPriceOracle, OraclePeriod, PriceOracle, Source};
+use pallet_ema_oracle::OracleError;
+use primitives::constants::chain::Weight;
+
+type AssetId = u32;
+
+parameter_types! {
+	pub const LRNAAssetId: AssetId = 1;
+}
+
+struct MockOracle;
+
+impl AggregatedPriceOracle<AssetId, u32, EmaPrice> for MockOracle {
+	type Error = OracleError;
+	fn get_price(
+		_asset_a: AssetId,
+		_asset_b: AssetId,
+		_period: OraclePeriod,
+		_source: Source,
+	) -> Result<(EmaPrice, u32), Self::Error> {
+		Ok((EmaPrice::new(u128::MAX, u128::MAX), 0))
+	}
+	fn get_price_weight() -> Weight {
+		Weight::zero()
+	}
+}
+
+type PriceProviderForRoute = OraclePriceProvider<AssetId, MockOracle, LRNAAssetId>;
+
+#[test]
+fn price_provider_should_not_overflow_when_route_contains_more_than_4_trades() {
+	let generate_route = |c| -> Vec<Trade<AssetId>> {
+		let mut r = vec![];
+		for _ in 0..c {
+			r.push(Trade {
+				pool: PoolType::Omnipool,
+				asset_in: 1,
+				asset_out: 0,
+			})
+		}
+		r
+	};
+
+	let route = generate_route(2);
+	let price = PriceProviderForRoute::price(&route, OraclePeriod::LastBlock);
+	assert_eq!(
+		price,
+		Some(EmaPrice::new(
+			340282366920938463463374607431768211452,
+			340282366920938463463374607431768211452
+		))
+	);
+
+	let route = generate_route(3);
+	let price = PriceProviderForRoute::price(&route, OraclePeriod::LastBlock);
+	assert_eq!(
+		price,
+		Some(EmaPrice::new(
+			340282366920938463463374607431768211450,
+			340282366920938463463374607431768211450
+		))
+	);
+
+	let route = generate_route(4);
+	let price = PriceProviderForRoute::price(&route, OraclePeriod::LastBlock);
+	assert_eq!(
+		price,
+		Some(EmaPrice::new(
+			340282366920938463463374607431768211448,
+			340282366920938463463374607431768211448
+		))
+	);
+
+	let route = generate_route(5);
+	let price = PriceProviderForRoute::price(&route, OraclePeriod::LastBlock);
+	assert_eq!(
+		price,
+		Some(EmaPrice::new(
+			340282366920938463463374607431768211446,
+			340282366920938463463374607431768211446
+		))
+	);
+
+	let route = generate_route(6);
+	let price = PriceProviderForRoute::price(&route, OraclePeriod::LastBlock);
+	assert_eq!(
+		price,
+		Some(EmaPrice::new(
+			340282366920938463463374607431768211444,
+			340282366920938463463374607431768211444
+		))
+	);
+
+	let route = generate_route(7);
+	let price = PriceProviderForRoute::price(&route, OraclePeriod::LastBlock);
+	assert_eq!(
+		price,
+		Some(EmaPrice::new(
+			340282366920938463463374607431768211442,
+			340282366920938463463374607431768211442
+		))
+	);
+
+	let route = generate_route(8);
+	let price = PriceProviderForRoute::price(&route, OraclePeriod::LastBlock);
+	assert_eq!(
+		price,
+		Some(EmaPrice::new(
+			340282366920938463463374607431768211440,
+			340282366920938463463374607431768211440
+		))
+	);
+
+	let route = generate_route(9);
+	let price = PriceProviderForRoute::price(&route, OraclePeriod::LastBlock);
+	assert_eq!(
+		price,
+		Some(EmaPrice::new(
+			340282366920938463463374607431768211438,
+			340282366920938463463374607431768211438
+		))
+	);
+	let route = generate_route(16);
+	let price = PriceProviderForRoute::price(&route, OraclePeriod::LastBlock);
+	assert_eq!(
+		price,
+		Some(EmaPrice::new(
+			340282366920938463463374607431768211424,
+			340282366920938463463374607431768211424
+		))
+	);
+	let route = generate_route(17);
+	let price = PriceProviderForRoute::price(&route, OraclePeriod::LastBlock);
+	assert_eq!(
+		price,
+		Some(EmaPrice::new(
+			340282366920938463463374607431768211422,
+			340282366920938463463374607431768211422
+		))
+	);
+}
```
