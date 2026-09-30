# [?] fix(Dashboard): fix underflow

## Summary
Severity: Unknown
Chain: Lido
Component: lidofinance/core
Published: 2025-04-17
Source: https://github.com/lidofinance/core/commit/58581b675a88b11a9aa4c3a5a9fd04bd6282c2ee
Type: security-commit

## Details
fix(Dashboard): fix underflow

## Patch
### contracts/0.8.25/vaults/dashboard/NodeOperatorFee.sol
```diff
@@ -147,7 +147,7 @@ contract NodeOperatorFee is Permissions {
         // cast down safely clamping to int128.max
         int128 adjustment = int128(int256(accruedRewardsAdjustment & ADJUSTMENT_CLAMP_MASK));
 
-        int128 rewardsAccrued = int128(latestReport.valuation - _lastClaimedReport.valuation) -
+        int128 rewardsAccrued = int128(latestReport.valuation) - int128(_lastClaimedReport.valuation) -
             (latestReport.inOutDelta - _lastClaimedReport.inOutDelta) -
             adjustment;
 
```
