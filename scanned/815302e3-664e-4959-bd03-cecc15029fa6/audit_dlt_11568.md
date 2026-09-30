# [?] program: avoid overflow when calculating overflow (#322)

## Summary
Severity: Unknown
Chain: Solana
Component: velocity-exchange/protocol-v2
Published: 2023-01-11
Source: https://github.com/velocity-exchange/protocol-v2/commit/c3365da0339dfebae6892183fe0b03d4c5fd844a
Type: security-commit

## Details
program: avoid overflow when calculating overflow (#322)

* bigz/fix-for-large-inventory-scale

* incorp comment

* remove redudant abs

* CHANGELOG

Co-authored-by: Chris Heaney <chrisheaney30@gmail.com>

## Patch
### CHANGELOG.md
```diff
@@ -15,6 +15,7 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 
 ### Fixes
 
+- program: avoid overflow when calculating overflow ([#322](https://github.com/drift-labs/protocol-v2/pull/322))
 - ts-sdk: fix user.getUnrealizedPnl to account for lp position
 - program: cancel market order for not satisfying limit price only if there was some base asset amount filled
 
```

### programs/drift/src/math/amm_spread.rs
```diff
@@ -167,13 +167,12 @@ pub fn calculate_spread_inventory_scale(
 
     let min_side_liquidity = max_bids.min(max_asks.abs());
 
+    // cap so (6e9 * AMM_RESERVE_PRECISION)^2 < 2^127
+    let amm_inventory_size = base_asset_amount_with_amm.abs().min(6000000000000000000);
+
     // inventory scale
-    let inventory_scale = base_asset_amount_with_amm
-        .safe_mul(
-            base_asset_amount_with_amm
-                .abs()
-                .max(AMM_RESERVE_PRECISION_I128),
-        )?
+    let inventory_scale = amm_inventory_size
+        .safe_mul(amm_inventory_size.max(AMM_RESERVE_PRECISION_I128))?
         .safe_div(AMM_RESERVE_PRECISION_I128)?
         .safe_mul(DEFAULT_LARGE_BID_ASK_FACTOR.cast::<i128>()?)?
         .safe_div(min_side_liquidity.max(1))?
@@ -189,7 +188,9 @@ pub fn calculate_spread_inventory_scale(
 
     let inventory_scale_capped = min(
         inventory_scale_max,
-        BID_ASK_SPREAD_PRECISION.safe_add(inventory_scale.cast()?)?,
+        BID_ASK_SPREAD_PRECISION
+            .safe_add(inventory_scale.cast()?)
+            .unwrap_or(u64::MAX),
     );
 
     Ok(inventory_scale_capped)
```
