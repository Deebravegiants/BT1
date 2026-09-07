# [M] Functions in the `BatchRequests` contract revert for removed contract addresses

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-06-yieldy
Published: 2022-06-26
Source: https://github.com/code-423n4/2022-06-yieldy-findings/issues/283
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-06-yieldy/blob/524f3b83522125fb7d4677fa7a7e5ba5a2c0fe67/src/contracts/BatchRequests.sol#L50-L59
https://github.com/code-423n4/2022-06-yieldy/blob/524f3b83522125fb7d4677fa7a7e5ba5a2c0fe67/src/contracts/BatchRequests.sol#L33-L44


# Vulnerability details

## Impact

Removing Yieldy contract addresses from the `contracts` array with `BatchRequests.removeAddress` replaces the contract address with a zero-address (due to how `delete` works).

Each function that loops over the `contracts` array or accesses an array item by index, should zero-address check the value before calling any external contract functions. If this zero-address check is missing, an external call to this zero-address will revert.

## Proof of Concept

[BatchRequests.canBatchContractByIndex](https://github.com/code-423n4/2022-06-yieldy/blob/524f3b83522125fb7d4677fa7a7e5ba5a2c0fe67/src/contracts/BatchRequests.sol#L50-L59)

```solidity
function canBatchContractByIndex(uint256 _index)
    external
    view
    returns (address, bool)
{
    return (
        contracts[_index],
        IStaking(contracts[_index]).canBatchTransactions() // @audit-info `contracts` with zero-address elements (due to deletion) will revert - add zero-address check and return false
    );
}
```

[BatchRequests.canBatchContracts](https://github.com/code-423n4/2022-06-yieldy/blob/524f3b83522125fb7d4677fa7a7e5ba5a2c0fe67/src/contracts/BatchRequests.sol#L33-L44)

```solidity
function canBatchContracts() external view returns (Batch[] memory) {
    uint256 contractsLength = contracts.length;
    Batch[] memory batch = new Batch[](contractsLength);
    for (uint256 i; i < contractsLength; ) {
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-06-yieldy-findings/issues/283_
