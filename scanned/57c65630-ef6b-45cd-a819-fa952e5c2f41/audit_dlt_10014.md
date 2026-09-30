# [?] fix: adapt borrow ratio spec to the underflow change

## Summary
Severity: Unknown
Chain: Morpho
Component: morpho-org/morpho-blue
Published: 2023-08-28
Source: https://github.com/morpho-org/morpho-blue/commit/4fe8cce9cd68748b21eb4ca4c857e2471a11094c
Type: security-commit

## Details
fix: adapt borrow ratio spec to the underflow change

## Patch
### certora/specs/BlueRatioMath.spec
```diff
@@ -13,8 +13,6 @@ methods {
 
     function _.borrowRate(MorphoHarness.MarketParams, MorphoHarness.Market) external => HAVOC_ECF;
 
-    function VIRTUAL_ASSETS() external returns uint256 envfree;
-    function VIRTUAL_SHARES() external returns uint256 envfree;
     function MAX_FEE() external returns uint256 envfree;
 }
 
@@ -101,7 +99,9 @@ filtered {
 }
 
 rule onlyAccrueInterestsCanIncreaseBorrowRatio(env e, method f, calldataarg args)
-filtered { f -> !f.isView }
+filtered {
+    f -> !f.isView && f.selector != sig:repay(MorphoHarness.MarketParams, uint256, uint256, address, bytes).selector
+}
 {
     MorphoHarness.Id id;
     requireInvariant feeInRange(id);
@@ -120,3 +120,25 @@ filtered { f -> !f.isView }
     // Check if ratio increases: assetsBefore/sharesBefore <= assetsAfter / sharesAfter
     assert assetsBefore * sharesAfter >= assetsAfter * sharesBefore;
 }
+
+rule repayIncreasesBorrowRatio(env e, MorphoHarness.MarketParams marketParams, uint256 assets, uint256 shares, address onbehalf, bytes data)
+{
+    MorphoHarness.Id id = getMarketId(marketParams);
+    requireInvariant feeInRange(id);
+
+    mathint assetsBefore = getVirtualTotalBorrowAssets(id);
+    mathint sharesBefore = getVirtualTotalBorrowShares(id);
+
+    require getLastUpdate(id) == e.block.timestamp;
+
+    mathint repaidAssets;
+    repaidAssets, _ = repay(e, marketParams, assets, shares, onbehalf, data);
+
+    require repaidAssets < assetsBefore;
+
+    mathint assetsAfter = getVirtualTotalBorrowAssets(id);
+    mathint sharesAfter = getVirtualTotalBorrowShares(id);
+
+    assert assetsAfter == assetsBefore - repaidAssets;
+    assert assetsBefore * sharesAfter >= assetsAfter * sharesBefore;
+}
```

### certora/specs/DifficultMath.spec
```diff
@@ -2,11 +2,18 @@ methods {
     function getMarketId(MorphoHarness.MarketParams) external returns MorphoHarness.Id envfree;
     function getVirtualTotalSupplyAssets(MorphoHarness.Id) external returns uint256 envfree;
     function getVirtualTotalSupplyShares(MorphoHarness.Id) external returns uint256 envfree;
+    function getVirtualTotalBorrowAssets(MorphoHarness.Id) external returns uint256 envfree;
+    function getVirtualTotalBorrowShares(MorphoHarness.Id) external returns uint256 envfree;
+    function getFee(MorphoHarness.Id) external returns uint256 envfree;
+    function getLastUpdate(MorphoHarness.Id) external returns uint256 envfree;
+
     function MathLib.mulDivDown(uint256 a, uint256 b, uint256 c) internal returns uint256 => summaryMulDivDown(a,b,c);
     function MathLib.mulDivUp(uint256 a, uint256 b, uint256 c) internal returns uint256 => summaryMulDivUp(a,b,c);
     function SafeTransferLib.safeTransfer(address token, address to, uint256 value) internal => NONDET;
     function SafeTransferLib.safeTransferFrom(address token, address from, address to, uint256 value) internal => NONDET;
     function _.onMorphoSupply(uint256 assets, bytes data) external => HAVOC_ECF;
+
+    function MAX_FEE() external returns uint256 envfree;
 }
 
 function summaryMulDivUp(uint256 x, uint256 y, uint256 d) returns uint256 {
@@ -17,6 +24,28 @@ function summaryMulDivDown(uint256 x, uint256 y, uint256 d) returns uint256 {
     return require_uint256((x * y) / d);
 }
 
+rule repayAllResetsBorrowRatio(env e, MorphoHarness.MarketParams marketParams, uint256 assets, uint256 shares, address onbehalf, bytes data)
+{
+    MorphoHarness.Id id = getMarketId(marketParams);
+    require getFee(id) <= MAX_FEE();
+
+    mathint assetsBefore = getVirtualTotalBorrowAssets(id);
+    mathint sharesBefore = getVirtualTotalBorrowShares(id);
+
+    require getLastUpdate(id) == e.block.timestamp;
+
+    mathint repaidAssets;
+    repaidAssets, _ = repay(e, marketParams, assets, shares, onbehalf, data);
+
+    require repaidAssets >= assetsBefore;
+
+    mathint assetsAfter = getVirtualTotalBorrowAssets(id);
+    mathint sharesAfter = getVirtualTotalBorrowShares(id);
+
+    assert assetsAfter == 1;
+}
+
+
 // There should be no profit from supply followed immediately by withdraw.
 rule supplyWithdraw() {
     MorphoHarness.MarketParams marketParams;
```
