# [?] jit audit fixes: Simulation Misses Reentrancy Guard Close

## Summary
Severity: Unknown
Chain: GMX
Component: gmx-io/gmx-synthetics
Published: 2025-09-04
Source: https://github.com/gmx-io/gmx-synthetics/commit/75b1494d026df4781c0630748e7e3690eb2687fb
Type: security-commit

## Details
jit audit fixes: Simulation Misses Reentrancy Guard Close

## Patch
### contracts/exchange/JitOrderHandler.sol
```diff
@@ -59,7 +59,7 @@ contract JitOrderHandler is IJitOrderHandler, BaseOrderHandler {
         GlvShiftUtils.CreateGlvShiftParams[] memory shiftParamsList,
         bytes32 orderKey,
         OracleUtils.SimulatePricesParams memory oracleParams
-    ) external override globalNonReentrant withSimulatedOraclePrices(oracleParams) {
+    ) external override withSimulatedOraclePrices(oracleParams) globalNonReentrant {
         _executeJitOrder(shiftParamsList, orderKey, true);
     }
 
```
