# [?] fix: overflow bug for pendingDiff input (#1027)

## Summary
Severity: Unknown
Chain: EigenLayer
Component: Layr-Labs/eigenlayer-contracts
Published: 2025-01-30
Source: https://github.com/Layr-Labs/eigenlayer-contracts/commit/30be88df0eb75f2bb9cbded51ece81f7bd59db55
Type: security-commit

## Details
fix: overflow bug for pendingDiff input (#1027)

* fix: overflow bug for pendingDiff input

* test: add check to regression test

---------

Co-authored-by: wadealexc <pragma-services@proton.me>

## Patch
### src/contracts/core/AllocationManager.sol
```diff
@@ -21,6 +21,7 @@ contract AllocationManager is
 {
     using DoubleEndedQueue for DoubleEndedQueue.Bytes32Deque;
     using EnumerableSet for *;
+    using SafeCast for *;
 
     using Snapshots for Snapshots.DefaultWadHistory;
     using OperatorSetLib for OperatorSet;
@@ -588,8 +589,9 @@ contract AllocationManager is
         return int128(uint128(newMagnitude)) - int128(uint128(currentMagnitude));
     }
 
+    /// @dev Use safe casting when downcasting to uint64
     function _addInt128(uint64 a, int128 b) internal pure returns (uint64) {
-        return uint64(uint128(int128(uint128(a)) + b));
+        return uint256(int256(int128(uint128(a)) + b)).toUint64();
     }
 
     /**
```

### src/test/unit/AllocationManagerUnit.t.sol
```diff
@@ -1995,6 +1995,58 @@ contract AllocationManagerUnitTests_ModifyAllocations is AllocationManagerUnitTe
         allocationManager.modifyAllocations(defaultOperator, allocateParams);
     }
 
+    function test_revert_safeCastOverflow() public {
+        // setup additional operatorSets for tests
+        OperatorSet memory opSet1 = OperatorSet(defaultAVS, 1);
+        _createOperatorSet(opSet1, defaultStrategies);
+        _registerOperator(defaultOperator);
+        _setAllocationDelay(defaultOperator, DEFAULT_OPERATOR_ALLOCATION_DELAY);
+        _registerForOperatorSet(defaultOperator, opSet1);
+
+        OperatorSet memory opSet2 = OperatorSet(defaultAVS, 2);
+        _createOperatorSet(opSet2, defaultStrategies);
+        _registerOperator(defaultOperator);
+        _setAllocationDelay(defaultOperator, DEFAULT_OPERATOR_ALLOCATION_DELAY);
+        _registerForOperatorSet(defaultOperator, opSet2);
+
+        // 1. Allocate all available magnitude for the strategy (WAD)
+        AllocateParams[] memory allocateParams = _randAllocateParams_DefaultOpSet();
+        allocateParams[0].newMagnitudes[0] = WAD;
+        cheats.prank(defaultOperator);
+        allocationManager.modifyAllocations(defaultOperator, allocateParams);
+        assertEq(
+            allocationManager.getAllocatableMagnitude(defaultOperator, strategyMock),
+            0,
+            "Allocatable magnitude should be 0"
+        );
+        assertEq(
+            allocationManager.getEncumberedMagnitude(defaultOperator, strategyMock),
+            WAD,
+            "Encumbered magnitude should be WAD"
+        );
+
+        // 2. allocate to another operatorSet for the same strategy to reset encumberedMagnitude back to 0
+        allocateParams[0].operatorSet = opSet1;
+        allocateParams[0].newMagnitudes[0] = type(uint64).max - WAD + 1;
+        cheats.prank(defaultOperator);
+        cheats.expectRevert("SafeCast: value doesn't fit in 64 bits");
+        allocationManager.modifyAllocations(defaultOperator, allocateParams);
+
+        // 3. after resetting encumberedMagnitude, attempt to allocate to opSet2 with WAD
+        allocateParams[0].operatorSet = opSet2;
+        allocateParams[0].newMagnitudes[0] = WAD;
+        cheats.prank(defaultOperator);
+        cheats.expectRevert(InsufficientMagnitude.selector);
+        allocationManager.modifyAllocations(defaultOperator, allocateParams);
+
+        // 4. after resetting encumberedMagnitude, attempt to allocate to opSet2 with 1
+        allocateParams[0].operatorSet = opSet2;
+        allocateParams[0].newMagnitudes[0] = 1;
+        cheats.prank(defaultOperator);
+        cheats.expectRevert(InsufficientMagnitude.selector);
+        allocationManager.modifyAllocations(defaultOperator, allocateParams);
+    }
+
     /**
      * @notice Tests edge cases around allocation delay:
      * 1. Set allocation delay to a value greater than ALLOCATION_CONFIGURATION_DELAY
```
