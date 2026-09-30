# [?] fix: bailsec - forceDeallocate() can underflow when LiquidityLaneAdapter realizes rewards

## Summary
Severity: Unknown
Chain: Symbiotic
Component: symbioticfi/core
Published: 2026-06-15
Source: https://github.com/symbioticfi/core/commit/fb186d03343d8335f3b491230bfec72c9124ccee
Type: security-commit

## Details
fix: bailsec - forceDeallocate() can underflow when LiquidityLaneAdapter realizes rewards

## Patch
### src/contracts/delegator/UniversalDelegator.sol
```diff
@@ -332,7 +332,7 @@ contract UniversalDelegator is
         // Update the adapter's absolute limit to avoid new allocations.
         _setLimits(
             adapter,
-            Math.min(absoluteLimitOf[adapter], adapterTotalAssets - deallocated - pending),
+            Math.min(absoluteLimitOf[adapter], adapterTotalAssets.saturatingSub(deallocated).saturatingSub(pending)),
             shareLimitOf[adapter]
         );
 
```

### test/delegator/UniversalDelegatorSweepPending.t.sol
```diff
@@ -11,6 +11,7 @@ import {
     MAX_SHARE,
     ADD_ADAPTER_ROLE,
     ALLOCATE_ROLE,
+    DEALLOCATE_ROLE,
     REMOVE_ADAPTER_ROLE,
     SET_ADAPTER_LIMITS_ROLE,
     SET_AUTO_ALLOCATE_ADAPTERS_ROLE,
@@ -190,6 +191,44 @@ contract UniversalDelegatorSweepAdapter {
     }
 }
 
+contract UniversalDelegatorSweepExcessDeallocateAdapter {
+    address public immutable FACTORY;
+    address public immutable vault;
+    uint256 public totalAssets;
+    uint256 public deallocateReturn;
+    uint256 public lastDeallocateAssets;
+
+    constructor(address factory, address vault_, uint256 totalAssets_, uint256 deallocateReturn_) {
+        FACTORY = factory;
+        vault = vault_;
+        totalAssets = totalAssets_;
+        deallocateReturn = deallocateReturn_;
+    }
+
+    function allocatable() external pure returns (uint256) {
+        return 0;
+    }
+
+    function freeAssets() external pure returns (uint256) {
+        return 0;
+    }
+
+    function allocate(uint256) external pure returns (uint256) {
+        return 0;
+    }
+
+    function deallocate(uint256 assets) external returns (uint256 deallocated) {
+        lastDeallocateAssets = assets;
+        if (assets == 0) {
+            return 0;
+        }
+        deallocated = deallocateReturn;
+        totalAssets = totalAssets > deallocated ? totalAssets - deallocated : 0;
+    }
+
+    function requestDeallocate(uint256) external {}
+}
+
 error UniversalDelegatorSweepAdapterBoom();
 
 contract UniversalDelegatorSweepRevertingAdapter {
@@ -616,6 +655,28 @@ contract UniversalDelegatorSweepPendingTest is Test {
         assertEq(vault.pushedAssets(), 0);
     }
 
+    function test_ForceDeallocateSaturatesLimitWhenAdapterReturnsMoreThanSnapshot() public {
+        UniversalDelegatorSweepQueue queue = new UniversalDelegatorSweepQueue(0);
+        UniversalDelegatorSweepVault vault = new UniversalDelegatorSweepVault(address(queue));
+        delegator.setVault(address(vault));
+
+        UniversalDelegatorSweepExcessDeallocateAdapter adapter =
+            new UniversalDelegatorSweepExcessDeallocateAdapter(address(adapterFactory), address(vault), 100, 120);
+        adapterRegistry.setWhitelisted(address(vault), address(adapter), true);
+
+        delegator.addAdapterForTest(address(adapter));
+        delegator.grantRoleForTest(DEALLOCATE_ROLE, address(this));
+        delegator.grantRoleForTest(SET_ADAPTER_LIMITS_ROLE, address(this));
+        delegator.setLimits(address(adapter), 80, MAX_SHARE);
+
+        (uint256 deallocated, uint256 pending) = delegator.forceDeallocate(address(adapter), 100);
+
+        assertEq(deallocated, 120);
+        assertEq(pending, 0);
+        assertEq(vault.pushedAssets(), 120);
+        assertEq(delegator.absoluteLimitOf(address(adapter)), 0);
+    }
+
     function test_SwapAdaptersSwapsAdaptersInRoute() public {
         UniversalDelegatorSweepAdapter adapter1 = _newAdapter(100, 0);
         UniversalDelegatorSweepAdapter adapter2 = _newAdapter(100, 0);
```
