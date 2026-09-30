# [H] remainingbalanceowner_should_be_set_by_the_protocol_owner

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23456
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The remainingBalanceOwner parameter, passed during the invocation of the addNode function, is intended to represent the P-Chain owner address that will receive any leftover $AVAX from a validator's balance when the validator is removed from the validator set. Currently, this value is provided by the operator invoking addNode. However, from a protocol security and correctness perspective, the assignment of remainingBalanceOwner should not be left to the operator. Instead, this should be determined and configured by the protocol itself to prevent wrong party receiving leftover funds.

```solidity
function addNode(
    bytes32 nodeId,
    bytes calldata bllKey,
    uint64 registrationExpiry,
    PChainOwner calldata remainingBalanceOwner, // should be passed by the protocol
    PChainOwner calldata disableOwner,
    uint256 stakeAmount // optional
) external updateStakeCache(getCurrentEpoch(), PRIMARY_ASSET_CLASS)
updateGlobalNodeStakeOncePerEpoch {,!
```

Impact: Misrouting of leftover $AVAX funds upon validator removal, potentially enabling loss of funds for the stakers.

## Recommendation
Modify the protocol to internally assign the remainingBalanceOwner during the addNode operation, removing this parameter from operator input.

```solidity
function addNode(
    bytes32 nodeId,
    bytes calldata blsKey,
    uint64 registrationExpiry,
    // PChainOwner calldata remainingBalanceOwner,  // removed
    PChainOwner calldata disableOwner,
    uint256 stakeAmount // optional
) external updateStakeCache(getCurrentEpoch(), PRIMARY_ASSET_CLASS)
updateGlobalNodeStakeOncePerEpoch {,!
}
```
