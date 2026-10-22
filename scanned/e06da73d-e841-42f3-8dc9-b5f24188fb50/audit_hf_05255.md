# [H] NodeId truncation can potentially cause validator registration denial of service

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23455
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: AvalancheL1Middleware::addNode function truncates 32-byte nodeId to 20-bytes when checking validator registration status. This truncation occurs when interacting with the BalancerValidatorManager.
// AvalancheL1Middleware.sol
bytes32 valId = balancerValidatorManager.registeredValidators(
abi.encodePacked(uint160(uint256(nodeId))) // Truncates 32 bytes to 20 bytes
);
uint160(uint256(nodeId)) discards the first 12 bytes of the nodeId before passing it to BalancerValidator-
Manager::registeredValidators(). However, the ValidatorManager.registeredValidators() function is de-
signed to work with full bytes nodeId without any truncation.
Impact: Operators cannot register validators if another validator with a colliding truncated nodeId already exists

## Proof of Concept
```solidity
function test_NodeIdCollisionVulnerability() public {
    uint48 epoch = _calcAndWarpOneEpoch();
    // Create two different nodeIds that have the same first 20 bytes
    bytes32 nodeId1 = 0x0000000000000000000000001234567890abcdef1234567890abcdef12345678;
    bytes32 nodeId2 = 0xFFFFFFFFFFFFFFFFFFFFFFFF1234567890abcdef1234567890abcdef12345678;
    // share same first 20 bytes when truncated
    bytes memory truncated1 = abi.encodePacked(uint160(uint256(nodeId1)));
    bytes memory truncated2 = abi.encodePacked(uint160(uint256(nodeId2)));
    assertEq(keccak256(truncated1), keccak256(truncated2), "Truncated nodeIds should be identical");
    // Alice adds the first node
    vm.prank(alice);
    middleware.addNode(
        nodeId1,
        hex"ABABABAB", // dummy BLS
        uint64(block.timestamp + 2 days),
        PChainOwner({threshold: 1, addresses: new address[](1)}),
        PChainOwner({threshold: 1, addresses: new address[](1)}),
        100_000_000_001_000
    );
    // Verify first node was registered
    bytes32 validationId1 = mockValidatorManager.registeredValidators(truncated1);
    assertNotEq(validationId1, bytes32(0), "First node should be registered");
    // Alice tries to add the second node with different nodeId but same truncated bytes
    // This should fail due to collision
    vm.prank(alice);
    vm.expectRevert();
    middleware.addNode(
        nodeId2,
        hex"ABABABAB", // dummy BLS
        uint64(block.timestamp + 2 days),
        PChainOwner({threshold: 1, addresses: new address[](1)}),
        PChainOwner({threshold: 1, addresses: new address[](1)}),
        100_000_000_001_000
    );
}
```

## Recommendation
Recommended Mitigation: Consider removing the forced truncation to 20 bytes
