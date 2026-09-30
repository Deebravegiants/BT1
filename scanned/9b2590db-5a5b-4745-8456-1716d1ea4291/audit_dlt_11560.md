# [?] program: fix max liquidation fee overflow (#1232)

## Summary
Severity: Unknown
Chain: Solana
Component: velocity-exchange/protocol-v2
Published: 2024-10-03
Source: https://github.com/velocity-exchange/protocol-v2/commit/08bc8e9ec0a6e386f0c27e1c8ecff24bfdca10ed
Type: security-commit

## Details
program: fix max liquidation fee overflow (#1232)

* program: fix max liquidation fee overflow

* CHANGELOG

## Patch
### CHANGELOG.md
```diff
@@ -16,6 +16,8 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 
 ### Fixes
 
+- program: fix max liquidation fee overflow ([#1232](https://github.com/drift-labs/protocol-v2/pull/1232))
+
 ### Breaking
 
 ## [2.95.0] - 2024-09-16
```

### programs/drift/src/state/perp_market.rs
```diff
@@ -422,8 +422,8 @@ impl PerpMarket {
     pub fn get_max_liquidation_fee(&self) -> DriftResult<u32> {
         let max_liquidation_fee = (self.liquidator_fee.safe_mul(MAX_LIQUIDATION_MULTIPLIER)?).min(
             self.margin_ratio_maintenance
-                .safe_mul(LIQUIDATION_FEE_PRECISION)?
-                .safe_div(MARGIN_PRECISION)?,
+                .safe_mul(LIQUIDATION_FEE_PRECISION / MARGIN_PRECISION)
+                .unwrap_or(u32::MAX),
         );
         Ok(max_liquidation_fee)
     }
```
