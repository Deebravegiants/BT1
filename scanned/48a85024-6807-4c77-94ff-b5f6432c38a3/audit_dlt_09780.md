# [?] jit audit fixes: Lacking doExecuteGlvShift Reentrancy Guard

## Summary
Severity: Unknown
Chain: GMX
Component: gmx-io/gmx-synthetics
Published: 2025-09-02
Source: https://github.com/gmx-io/gmx-synthetics/commit/5a70dd0bcfdc067a8af78755476898b1fe0d2ae8
Type: security-commit

## Details
jit audit fixes: Lacking doExecuteGlvShift Reentrancy Guard

## Patch
### contracts/exchange/GlvShiftHandler.sol
```diff
@@ -67,7 +67,8 @@ contract GlvShiftHandler is BaseHandler, ReentrancyGuard {
         }
     }
 
-    function doExecuteGlvShift(bytes32 key, GlvShift.Props memory glvShift, address keeper, bool skipRemoval) external onlySelfOrController {
+    // @note the caller function should be protected by global reentrancy guard
+    function doExecuteGlvShift(bytes32 key, GlvShift.Props memory glvShift, address keeper, bool skipRemoval) external nonReentrant onlySelfOrController {
         FeatureUtils.validateFeature(dataStore, Keys.executeGlvShiftFeatureDisabledKey(address(this)));
 
         GlvShiftUtils.ExecuteGlvShiftParams memory params = GlvShiftUtils.ExecuteGlvShiftParams({
```
