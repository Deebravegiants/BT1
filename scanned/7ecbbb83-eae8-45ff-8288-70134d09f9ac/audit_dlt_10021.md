# [?] fix: reentrancy check

## Summary
Severity: Unknown
Chain: Morpho
Component: morpho-org/morpho-blue
Published: 2023-08-20
Source: https://github.com/morpho-org/morpho-blue/commit/13321409c67ec1bc5e6c6de98615d0fec2f15b4f
Type: security-commit

## Details
fix: reentrancy check

## Patch
### certora/specs/DifficultMath.spec
```diff
@@ -33,6 +33,8 @@ rule supplyWithdraw() {
     env e2;
 
     require e1.block.timestamp == e2.block.timestamp;
+    require e1.block.timestamp < 2^128;
+    require e2.block.timestamp < 2^128;
 
     suppliedAssets, suppliedShares = supply(e1, marketParams, assets, shares, onbehalf, data);
 
@@ -62,6 +64,8 @@ rule withdrawSupply() {
     env e2;
 
     require e1.block.timestamp == e2.block.timestamp;
+    require e1.block.timestamp < 2^128;
+    require e2.block.timestamp < 2^128;
 
     withdrawnAssets, withdrawnShares = withdraw(e2, marketParams, assets, shares, onbehalf, receiver);
 
```

### certora/specs/Reentrancy.spec
```diff
@@ -1,5 +1,5 @@
 methods {
-    function _.borrowRate(MorphoHarness.Market market) external => summaryBorrowRate(market) expect uint256;
+    function _.borrowRate(MorphoHarness.MarketParams marketParams) external => summaryBorrowRate(marketParams) expect uint256;
 }
 
 ghost bool hasAccessedStorage;
@@ -9,7 +9,7 @@ ghost bool delegate_call;
 ghost bool static_call;
 ghost bool callIsBorrowRate;
 
-function summaryBorrowRate(MorphoHarness.Market market) returns uint256 {
+function summaryBorrowRate(MorphoHarness.MarketParams marketParams) returns uint256 {
     uint256 result;
     callIsBorrowRate = true;
     return result;
```
