# [C] insufficient_validation_in_avalanchel1middleware::removeoperator_can_create_permanent_validator_lockup

## Summary
Severity: Critical
Contest weight: 0.0000
Dataset id: 23553
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Removal of operators with active nodes, whether intentional or by accident, can permanently lock operator nodes and disrupt the protocol node rebalancing process.  
The AvalancheL1Middleware::disableOperator and AvalancheL1Middleware::removeOperator() lack validation to ensure operators have no active nodes before removal.

```solidity
// AvalancheL1Middleware.sol
function disableOperator(
    address operator
) external onlyOwner updateGlobalNodeStakeOncePerEpoch {
    operators.disable(operator); //@note disable an operator - this only works if operator exists
}
function removeOperator(
    address operator
) external onlyOwner updateGlobalNodeStakeOncePerEpoch {
    (, uint48 disabledTime) = operators.getTimes(operator);
    if (disabledTime == 0 || disabledTime + SLASHING_WINDOW > Time.timestamp()) {
        revert AvalancheL1Middleware__OperatorGracePeriodNotPassed(disabledTime, SLASHING_WINDOW);
    }
    operators.remove(operator); // @audit no check
}
```

Once an operator is removed, most node management functions become permanently inaccessible due to access control restrictions:

```solidity
modifier onlyRegisteredOperatorNode(address operator, bytes32 nodeId) {
    if (!operators.contains(operator)) {
        revert AvalancheL1Middleware__OperatorNotRegistered(operator); // @audit Always fails for removed operators,!
    }
    if (!operatorNodes[operator].contains(nodeId)) {
        revert AvalancheL1Middleware__NodeNotFound(nodeId);
    }
    _;
}

// Force updates also blocked
function forceUpdateNodes(address operator, uint256 limitStake) external {
    if (!operators.contains(operator)) {
        revert AvalancheL1Middleware__OperatorNotRegistered(operator); // @audit prevents any force updates,!
    }
    // ... rest of function never executes
}

// Individual node operations blocked
function removeNode(bytes32 nodeId) external
    onlyRegisteredOperatorNode(msg.sender, nodeId) // @audit modifier blocks removed operators
{
    _removeNode(msg.sender, nodeId);
}
```

**Impact:**  
1. permanent validator lockup where operators cannot exit the P-Chain  
2. disproportionate stake reduction for remaining operators during undelegations  
3. removed operators cannot be rebalanced

## Proof of Concept
```solidity
function test_POC_RemoveOperatorWithActiveNodes() public {
    uint48 epoch = _calcAndWarpOneEpoch();
    // Add nodes for alice
    (bytes32[] memory nodeIds, bytes32[] memory validationIDs,) = _createAndConfirmNodes(alice, 3, 0,
    true);,!
    // Move to next epoch to ensure nodes are active
    epoch = _calcAndWarpOneEpoch();
    // Verify alice has active nodes and stake
    uint256 nodeCount = middleware.getOperatorNodesLength(alice);
    uint256 aliceStake = middleware.getOperatorStake(alice, epoch, assetClassId);
    assertGt(nodeCount, 0, "Alice should have active nodes");
    assertGt(aliceStake, 0, "Alice should have stake");
    console2.log("Before removal:");
    console2.log(" Active nodes:", nodeCount);
    console2.log(" Operator stake:", aliceStake);
    // First disable the operator (required for removal)
    vm.prank(validatorManagerAddress);
    middleware.disableOperator(alice);
    // Warp past the slashing window to allow removal
    uint48 slashingWindow = middleware.SLASHING_WINDOW();
    vm.warp(block.timestamp + slashingWindow + 1);
    // @audit Admin can remove operator with active nodes (NO VALIDATION!)
    vm.prank(validatorManagerAddress);
    middleware.removeOperator(alice);
    // Verify alice is removed from operators mapping
    address[] memory currentOperators = middleware.getAllOperators();
    bool aliceFound = false;
    for (uint256 i = 0; i < currentOperators.length; i++) {
        if (currentOperators[i] == alice) {
            aliceFound = true;
            break;
        }
    }
    console2.log("Alice found:", aliceFound);
    assertFalse(aliceFound, "Alice should not be in current operators list");
    // Verify alice's nodes still exist in storage
    assertEq(middleware.getOperatorNodesLength(alice), nodeCount, "Alice's nodes should still exist in
    storage");,!
    // Verify alice's nodes still have stake cached
    for (uint256 i = 0; i < nodeIds.length; i++) {
        uint256 nodeStake = middleware.nodeStakeCache(epoch, validationIDs[i]);
        assertGt(nodeStake, 0, "Node should still have cached stake");
    }
    // Verify stake calculations still work
    uint256 stakeAfterRemoval = middleware.getOperatorStake(alice, epoch, assetClassId);
    assertEq(stakeAfterRemoval, aliceStake, "Stake calculation should still work");
}
```

## Recommendation
Consider allowing operator removal only if all active nodes of that operator are removed.
