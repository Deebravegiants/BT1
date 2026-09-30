# [?] use safe fixed operation to prevent panic

## Summary
Severity: Unknown
Chain: Hydration
Component: galacticcouncil/hydration-node
Published: 2024-04-15
Source: https://github.com/galacticcouncil/hydration-node/commit/356fd15d2a7fa7f2a1531edc14c8abeaa1890f1e
Type: security-commit

## Details
use safe fixed operation to prevent panic

## Patch
### pallets/route-executor/src/lib.rs
```diff
@@ -878,6 +878,6 @@ impl<T: Config> RouteSpotPriceProvider<T::AssetId> for Pallet<T> {
 
 		let rat_as_u128 = round_u512_to_rational((nominator, denominator), Rounding::Nearest);
 
-		Some(FixedU128::from_rational(rat_as_u128.0, rat_as_u128.1))
+		FixedU128::checked_from_rational(rat_as_u128.0, rat_as_u128.1)
 	}
 }
```
