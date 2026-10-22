# [M] Max allocations can be bypassed with multi-

## Summary
Severity: Medium
Contest weight: 0.6774
Dataset id: 22606
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
TokenSale._processPrivate() ensures that a user cannot deposit more than their allocation amount. However, each address can deposit up to at least maxAllocations. This can be leveraged by a malicious user by using different addresses to claim all tokens without even staking. The idea of the protocol is to give everyone the right to have at least maxAllocations allocations. By completing missions, users level up and unlock new tiers. This process will be increasing their allocations. The problem is that when a user has no allocations, they have still a granted amount of maxAllocations. TokenSale.calculateMaxAllocation returns max(maxTierAlloc(); maxAllocation) that this user have maxAllocation allocations (because maxAllocation > 0).
```solidity
if (userTier == 0 && giftedTierAllc == 0) {
    return 0;
}
```
Multiple Ethereum accounts can be used by the same party to take control over the IDO and all its allocations, on top of that without even staking. wants to still give some allocations to their users. Buying all allocations without staking. This also violates a key property that only ION holders can deposit.
```solidity
function calculateMaxAllocation(address _sender) public returns (uint256) {
    uint256 userMaxAllc = _maxTierAllc(_sender);
    if (userMaxAllc > maxAllocation) {
        return userMaxAllc;
    } else {
        return maxAllocation;
    }
}
```

## Recommendation
A possible solution may be to modify calculateMaxAllocation in the following way:
```solidity
function calculateMaxAllocation(address _sender) public returns (uint256) {
    uint256 userMaxAllc = _maxTierAllc(_sender);
    if (userMaxAllc == 0) return 0;
    if (userMaxAllc > maxAllocation) {
        return userMaxAllc;
    } else {
        return maxAllocation;
    }
}
```
