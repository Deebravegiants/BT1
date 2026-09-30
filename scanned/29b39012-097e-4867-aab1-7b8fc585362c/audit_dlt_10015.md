# [?] Merge pull request #436 from morpho-labs/fix/underflow

## Summary
Severity: Unknown
Chain: Morpho
Component: morpho-org/morpho-blue
Published: 2023-08-28
Source: https://github.com/morpho-org/morpho-blue/commit/bdcf70a01e08c1d57daee9186fe2bf36349d375e
Type: security-commit

## Details
Merge pull request #436 from morpho-labs/fix/underflow

fix(repay): underflow on repay max

## Patch
### src/Morpho.sol
```diff
@@ -272,8 +272,9 @@ contract Morpho is IMorpho {
 
         position[id][onBehalf].borrowShares -= shares.toUint128();
         market[id].totalBorrowShares -= shares.toUint128();
-        market[id].totalBorrowAssets -= assets.toUint128();
+        market[id].totalBorrowAssets = UtilsLib.zeroFloorSub(market[id].totalBorrowAssets, assets).toUint128();
 
+        // `assets` may be greater than `totalBorrowAssets` by 1.
         emit EventsLib.Repay(id, msg.sender, onBehalf, assets, shares);
 
         if (data.length > 0) IMorphoRepayCallback(msg.sender).onMorphoRepay(assets, data);
@@ -366,7 +367,7 @@ contract Morpho is IMorpho {
 
         position[id][borrower].borrowShares -= repaidShares.toUint128();
         market[id].totalBorrowShares -= repaidShares.toUint128();
-        market[id].totalBorrowAssets -= repaidAssets.toUint128();
+        market[id].totalBorrowAssets = UtilsLib.zeroFloorSub(market[id].totalBorrowAssets, repaidAssets).toUint128();
 
         position[id][borrower].collateral -= seizedAssets.toUint128();
 
@@ -383,6 +384,7 @@ contract Morpho is IMorpho {
 
         IERC20(marketParams.collateralToken).safeTransfer(msg.sender, seizedAssets);
 
+        // `repaidAssets` may be greater than `totalBorrowAssets` by 1.
         emit EventsLib.Liquidate(id, msg.sender, borrower, repaidAssets, repaidShares, seizedAssets, badDebtShares);
 
         if (data.length > 0) IMorphoLiquidateCallback(msg.sender).onMorphoLiquidate(repaidAssets, data);
```

### src/libraries/EventsLib.sol
```diff
@@ -78,7 +78,7 @@ library EventsLib {
     /// @param id The market id.
     /// @param caller The caller.
     /// @param onBehalf The address for which the assets were repaid.
-    /// @param assets The amount of assets repaid.
+    /// @param assets The amount of assets repaid. May be 1 over the corresponding market's `totalBorrowAssets`.
     /// @param shares The amount of shares burned.
     event Repay(Id indexed id, address indexed caller, address indexed onBehalf, uint256 assets, uint256 shares);
 
@@ -103,7 +103,7 @@ library EventsLib {
     /// @param id The market id.
     /// @param caller The caller.
     /// @param borrower The borrower of the position.
-    /// @param repaidAssets The amount of assets repaid.
+    /// @param repaidAssets The amount of assets repaid. May be 1 over the corresponding market's `totalBorrowAssets`.
     /// @param repaidShares The amount of shares burned.
     /// @param seizedAssets The amount of collateral seized.
     /// @param badDebtShares The amount of shares minted as bad debt.
```

### src/libraries/UtilsLib.sol
```diff
@@ -28,4 +28,11 @@ library UtilsLib {
         require(x <= type(uint128).max, ErrorsLib.MAX_UINT128_EXCEEDED);
         return uint128(x);
     }
+
+    /// @dev Returns max(x - y, 0).
+    function zeroFloorSub(uint256 x, uint256 y) internal pure returns (uint256 z) {
+        assembly {
+            z := mul(gt(x, y), sub(x, y))
+        }
+    }
 }
```

### test/forge/integration/RepayIntegrationTest.sol
```diff
@@ -127,4 +127,25 @@ contract RepayIntegrationTest is BaseTest {
             "morpho balance"
         );
     }
+
+    function testRepayMax(uint256 shares) public {
+        shares = bound(shares, MIN_TEST_SHARES, MAX_TEST_SHARES);
+
+        uint256 assets = shares.toAssetsUp(0, 0);
+
+        borrowableToken.setBalance(address(this), assets);
+
+        morpho.supply(marketParams, 0, shares, SUPPLIER, hex"");
+
+        collateralToken.setBalance(address(this), HIGH_COLLATERAL_AMOUNT);
+
+        morpho.supplyCollateral(marketParams, HIGH_COLLATERAL_AMOUNT, BORROWER, hex"");
+
+        vm.prank(BORROWER);
+        morpho.borrow(marketParams, 0, shares, BORROWER, RECEIVER);
+
+        borrowableToken.setBalance(address(this), assets);
+
+        morpho.repay(marketParams, 0, shares, BORROWER, hex"");
+    }
 }
```

### test/forge/invariant/SingleMarketChangingPriceInvariantTest.sol
```diff
@@ -272,8 +272,8 @@ contract SingleMarketChangingPriceInvariantTest is InvariantTest {
     }
 
     function invariantMorphoBalance() public {
-        assertEq(
-            morpho.totalSupplyAssets(id) - morpho.totalBorrowAssets(id), borrowableToken.balanceOf(address(morpho))
+        assertGe(
+            borrowableToken.balanceOf(address(morpho)), morpho.totalSupplyAssets(id) - morpho.totalBorrowAssets(id)
         );
     }
 }
```

### test/forge/invariant/SingleMarketInvariantTest.sol
```diff
@@ -131,8 +131,8 @@ contract SingleMarketInvariantTest is InvariantTest {
     }
 
     function invariantMorphoBalance() public {
-        assertEq(
-            morpho.totalSupplyAssets(id) - morpho.totalBorrowAssets(id), borrowableToken.balanceOf(address(morpho))
+        assertGe(
+            borrowableToken.balanceOf(address(morpho)), morpho.totalSupplyAssets(id) - morpho.totalBorrowAssets(id)
         );
     }
 }
```

### test/forge/invariant/SinglePositionInvariantTest.sol
```diff
@@ -123,8 +123,8 @@ contract SinglePositionInvariantTest is InvariantTest {
     }
 
     function invariantMorphoBalance() public {
-        assertEq(
-            morpho.totalSupplyAssets(id) - morpho.totalBorrowAssets(id), borrowableToken.balanceOf(address(morpho))
+        assertGe(
+            borrowableToken.balanceOf(address(morpho)), morpho.totalSupplyAssets(id) - morpho.totalBorrowAssets(id)
         );
     }
 
```

### test/forge/invariant/TwoMarketsInvariantTest.sol
```diff
@@ -158,6 +158,7 @@ contract TwoMarketsInvariantTest is InvariantTest {
     function invariantMorphoBalance() public {
         uint256 marketAvailableAmount = morpho.totalSupplyAssets(id) - morpho.totalBorrowAssets(id);
         uint256 market2AvailableAmount = morpho.totalSupplyAssets(id2) - morpho.totalBorrowAssets(id2);
-        assertEq(marketAvailableAmount + market2AvailableAmount, borrowableToken.balanceOf(address(morpho)));
+
+        assertGe(borrowableToken.balanceOf(address(morpho)), marketAvailableAmount + market2AvailableAmount);
     }
 }
```

### test/forge/libraries/UtilsLibTest.sol
```diff
@@ -27,4 +27,8 @@ contract UtilsLibTest is Test {
         vm.expectRevert(bytes(ErrorsLib.MAX_UINT128_EXCEEDED));
         x.toUint128();
     }
+
+    function testZeroFloorSub(uint256 x, uint256 y) public {
+        assertEq(UtilsLib.zeroFloorSub(x, y), x < y ? 0 : x - y);
+    }
 }
```
