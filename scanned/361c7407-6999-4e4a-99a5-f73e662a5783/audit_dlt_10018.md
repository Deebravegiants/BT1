# [?] test: add lltv shifting and authorization double spend tests

## Summary
Severity: Unknown
Chain: Morpho
Component: morpho-org/morpho-blue
Published: 2023-08-26
Source: https://github.com/morpho-org/morpho-blue/commit/3977f89935b168f5b6670364a1ab3b7d6f2c8173
Type: security-commit

## Details
test: add lltv shifting and authorization double spend tests

## Patch
### test/forge/BaseTest.sol
```diff
@@ -24,6 +24,8 @@ contract BaseTest is Test {
     uint256 internal constant MAX_TEST_AMOUNT = 1e28;
     uint256 internal constant MIN_TEST_SHARES = MIN_TEST_AMOUNT * SharesMathLib.VIRTUAL_SHARES;
     uint256 internal constant MAX_TEST_SHARES = MAX_TEST_AMOUNT * SharesMathLib.VIRTUAL_SHARES;
+    uint256 internal constant MIN_TEST_LLTV = 0.1 ether;
+    uint256 internal constant MAX_TEST_LLTV = 0.9 ether;
     uint256 internal constant MIN_COLLATERAL_PRICE = 1e10;
     uint256 internal constant MAX_COLLATERAL_PRICE = 1e40;
     uint256 internal constant MAX_COLLATERAL_ASSETS = type(uint128).max;
@@ -36,7 +38,7 @@ contract BaseTest is Test {
     address internal LIQUIDATOR = _addrFromHashedString("Morpho Liquidator");
     address internal OWNER = _addrFromHashedString("Morpho Owner");
 
-    uint256 internal constant LLTV = 0.8 ether;
+    uint256 internal LLTV = 0.8 ether;
 
     Morpho internal morpho;
     ERC20 internal borrowableToken;
@@ -112,6 +114,21 @@ contract BaseTest is Test {
         vm.warp(block.timestamp + 1 days);
     }
 
+    function _setLltv(uint256 lltv) internal {
+        LLTV = lltv;
+        marketParams =
+            MarketParams(address(borrowableToken), address(collateralToken), address(oracle), address(irm), lltv);
+        id = marketParams.id();
+
+        vm.startPrank(OWNER);
+        if (!morpho.isLltvEnabled(lltv)) morpho.enableLltv(lltv);
+        if (morpho.lastUpdate(marketParams.id()) == 0) morpho.createMarket(marketParams);
+        vm.stopPrank();
+
+        vm.roll(block.number + 1);
+        vm.warp(block.timestamp + 1 days);
+    }
+
     function _addrFromHashedString(string memory str) internal pure returns (address) {
         return address(uint160(uint256(keccak256(bytes(str)))));
     }
@@ -170,6 +187,10 @@ contract BaseTest is Test {
         return (amountCollateral, amountBorrowed, priceCollateral);
     }
 
+    function _boundTestLltv(uint256 lltv) internal view returns (uint256) {
+        return bound(lltv, MIN_TEST_LLTV, MAX_TEST_LLTV);
+    }
+
     function _boundValidLltv(uint256 lltv) internal view returns (uint256) {
         return bound(lltv, 0, WAD - 1);
     }
```

### test/forge/integration/AuthorizationIntegrationTest.sol
```diff
@@ -88,4 +88,22 @@ contract AuthorizationIntegrationTest is BaseTest {
         assertEq(morpho.isAuthorized(authorization.authorizer, authorization.authorized), authorization.isAuthorized);
         assertEq(morpho.nonce(authorization.authorizer), 1);
     }
+
+    function testAuthorizationFailsWithReusedSig(Authorization memory authorization, uint256 privateKey) public {
+        authorization.deadline = bound(authorization.deadline, block.timestamp + 1, type(uint256).max);
+
+        // Private key must be less than the secp256k1 curve order.
+        privateKey = bound(privateKey, 1, type(uint32).max);
+        authorization.nonce = 0;
+        authorization.authorizer = vm.addr(privateKey);
+
+        Signature memory sig;
+        bytes32 digest = SigUtils.getTypedDataHash(morpho.DOMAIN_SEPARATOR(), authorization);
+        (sig.v, sig.r, sig.s) = vm.sign(privateKey, digest);
+
+        morpho.setAuthorizationWithSig(authorization, sig);
+
+        vm.expectRevert(bytes(ErrorsLib.INVALID_NONCE));
+        morpho.setAuthorizationWithSig(authorization, sig);
+    }
 }
```

### test/forge/integration/LiquidateIntegrationTest.sol
```diff
@@ -8,14 +8,16 @@ contract LiquidateIntegrationTest is BaseTest {
     using MorphoLib for Morpho;
     using SharesMathLib for uint256;
 
-    function testLiquidateNotCreatedMarket(MarketParams memory marketParamsFuzz) public {
+    function testLiquidateNotCreatedMarket(MarketParams memory marketParamsFuzz, uint256 lltv) public {
+        _setLltv(_boundTestLltv(lltv));
         vm.assume(neq(marketParamsFuzz, marketParams));
 
         vm.expectRevert(bytes(ErrorsLib.MARKET_NOT_CREATED));
         morpho.liquidate(marketParamsFuzz, address(this), 1, 0, hex"");
     }
 
-    function testLiquidateZeroAmount() public {
+    function testLiquidateZeroAmount(uint256 lltv) public {
+        _setLltv(_boundTestLltv(lltv));
         vm.prank(BORROWER);
 
         vm.expectRevert(bytes(ErrorsLib.INCONSISTENT_INPUT));
@@ -37,12 +39,14 @@ contract LiquidateIntegrationTest is BaseTest {
         uint256 amountSupplied,
         uint256 amountBorrowed,
         uint256 amountSeized,
-        uint256 priceCollateral
+        uint256 priceCollateral,
+        uint256 lltv
     ) public {
+        _setLltv(_boundTestLltv(lltv));
         (amountCollateral, amountBorrowed, priceCollateral) =
             _boundHealthyPosition(amountCollateral, amountBorrowed, priceCollateral);
 
-        amountSupplied = bound(amountSupplied, amountBorrowed, MAX_TEST_AMOUNT);
+        amountSupplied = bound(amountSupplied, amountBorrowed, amountBorrowed + MAX_TEST_AMOUNT);
         _supply(amountSupplied);
 
         amountSeized = bound(amountSeized, 1, amountCollateral);
@@ -67,8 +71,10 @@ contract LiquidateIntegrationTest is BaseTest {
         uint256 amountSupplied,
         uint256 amountBorrowed,
         uint256 amountSeized,
-        uint256 priceCollateral
+        uint256 priceCollateral,
+        uint256 lltv
     ) public {
+        _setLltv(_boundTestLltv(lltv));
         (amountCollateral, amountBorrowed, priceCollateral) =
             _boundUnhealthyPosition(amountCollateral, amountBorrowed, priceCollateral);
 
@@ -129,8 +135,10 @@ contract LiquidateIntegrationTest is BaseTest {
         uint256 amountSupplied,
         uint256 amountBorrowed,
         uint256 sharesRepaid,
-        uint256 priceCollateral
+        uint256 priceCollateral,
+        uint256 lltv
     ) public {
+        _setLltv(_boundTestLltv(lltv));
         (amountCollateral, amountBorrowed, priceCollateral) =
             _boundUnhealthyPosition(amountCollateral, amountBorrowed, priceCollateral);
 
@@ -204,8 +212,10 @@ contract LiquidateIntegrationTest is BaseTest {
         uint256 amountCollateral,
         uint256 amountSupplied,
         uint256 amountBorrowed,
-        uint256 priceCollateral
+        uint256 priceCollateral,
+        uint256 lltv
     ) public {
+        _setLltv(_boundTestLltv(lltv));
         LiquidateBadDebtTestParams memory params;
 
         (amountCollateral, amountBorrowed, priceCollateral) =
```
