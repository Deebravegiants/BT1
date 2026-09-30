# [?] Fix StableSurgeHook underflow when maxSurgeFeePercentage < staticSwapFeePercentage (#1271)

## Summary
Severity: Unknown
Chain: Balancer
Component: balancer/balancer-v3-monorepo
Published: 2025-02-06
Source: https://github.com/balancer/balancer-v3-monorepo/commit/767a6a137be78bf7b6bb67b8ff423f53ef60939c
Type: security-commit

## Details
Fix StableSurgeHook underflow when maxSurgeFeePercentage < staticSwapFeePercentage (#1271)

## Patch
### pkg/pool-hooks/contracts/StableSurgeHook.sol
```diff
@@ -328,6 +328,13 @@ contract StableSurgeHook is BaseHooks, VaultGuard, SingletonAuthentication {
         uint256[] memory newBalances
     ) internal view returns (uint256 surgeFeePercentage) {
         SurgeFeeData memory surgeFeeData = _surgeFeePoolData[pool];
+
+        // If the max surge fee percentage is less than the static fee percentage, return the static fee percentage.
+        // No matter where the imbalance is, the fee can never be smaller than the static fee.
+        if (surgeFeeData.maxSurgeFeePercentage < staticFeePercentage) {
+            return staticFeePercentage;
+        }
+
         uint256 newTotalImbalance = StableSurgeMedianMath.calculateImbalance(newBalances);
 
         bool isSurging = _isSurging(surgeFeeData, params.balancesScaled18, newTotalImbalance);
```

### pkg/pool-hooks/test/foundry/StableSurgeHookUnit.t.sol
```diff
@@ -45,6 +45,11 @@ contract StableSurgeHookUnitTest is BaseVaultTest {
             DEFAULT_MAX_SURGE_FEE_PERCENTAGE,
             DEFAULT_SURGE_THRESHOLD_PERCENTAGE
         );
+
+        authorizer.grantRole(
+            IAuthentication(address(stableSurgeHook)).getActionId(StableSurgeHook.setMaxSurgeFeePercentage.selector),
+            admin
+        );
     }
 
     function testOnRegister() public {
@@ -182,6 +187,40 @@ contract StableSurgeHookUnitTest is BaseVaultTest {
         stableSurgeHook.setSurgeThresholdPercentage(pool, 1e18);
     }
 
+    function testGetSurgeFeePercentage_MaxSurgeSmallerThanStatic() public {
+        // Set a small max surge fee percentage.
+        uint256 smallMaxSurgeFee = 1e16; // 1%
+        vm.prank(admin);
+        stableSurgeHook.setMaxSurgeFeePercentage(pool, smallMaxSurgeFee);
+
+        // Set a larger static fee percentage.
+        uint256 staticFeePercentage = 2e16; // 2%
+        vault.manuallySetSwapFee(pool, staticFeePercentage);
+
+        // Create an unbalanced state to mock an imbalance in the pool. This would normally trigger surge pricing and
+        // revert due to a math underflow, but the surge logic is currently blocked because maxSurgeFeePercentage <
+        // staticFeePercentage.
+        uint256[] memory balances = new uint256[](2);
+        balances[0] = poolInitAmount / 10;
+        balances[1] = poolInitAmount;
+
+        // Create swap params that would normally trigger surge pricing.
+        PoolSwapParams memory params = PoolSwapParams({
+            kind: SwapKind.EXACT_IN,
+            indexIn: 0,
+            indexOut: 1,
+            amountGivenScaled18: poolInitAmount / 2,
+            balancesScaled18: balances,
+            router: address(0),
+            userData: bytes("")
+        });
+
+        // Even though we're in a surging state, we should get back the static fee since it's larger than the max
+        // surge fee.
+        uint256 surgeFeePercentage = stableSurgeHook.getSurgeFeePercentage(params, pool, staticFeePercentage);
+        assertEq(surgeFeePercentage, staticFeePercentage, "Should return static fee percentage");
+    }
+
     function testGetSurgeFeePercentage__Fuzz(
         uint256 length,
         uint256 indexIn,
```
