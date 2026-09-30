# [?] fix(repay): underflow on repay max

## Summary
Severity: Unknown
Chain: Morpho
Component: morpho-org/morpho-blue
Published: 2023-08-24
Source: https://github.com/morpho-org/morpho-blue/commit/8754b777928d2ca6a97fe585f2379a735da2fbb0
Type: security-commit

## Details
fix(repay): underflow on repay max

## Patch
### src/Morpho.sol
```diff
@@ -267,8 +267,14 @@ contract Morpho is IMorpho {
 
         _accrueInterest(marketParams, id);
 
-        if (assets > 0) shares = assets.toSharesDown(market[id].totalBorrowAssets, market[id].totalBorrowShares);
-        else assets = shares.toAssetsUp(market[id].totalBorrowAssets, market[id].totalBorrowShares);
+        if (assets > 0) {
+            shares = assets.toSharesDown(market[id].totalBorrowAssets, market[id].totalBorrowShares);
+        } else {
+            assets = UtilsLib.min(
+                market[id].totalBorrowAssets,
+                shares.toAssetsUp(market[id].totalBorrowAssets, market[id].totalBorrowShares)
+            );
+        }
 
         user[id][onBehalf].borrowShares -= shares.toUint128();
         market[id].totalBorrowShares -= shares.toUint128();
```
