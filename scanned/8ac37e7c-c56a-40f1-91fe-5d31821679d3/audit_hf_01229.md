# [M] ETH Dust in createAndInitializePool

## Summary
Severity: Medium
Contest weight: 0.3955
Dataset id: 5538
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The createAndInitializePool function is marked as payable, but it doesn't handle any potential dust ETH that might be sent along with the transaction. This could lead to ETH being trapped in the contract or potentially stolen by an attacker.
```solidity
function createAndInitializePool(
    CreateAndInitializeParams calldata params
)
external
payable
checkDeadline(params.deadline)
returns (
    address pool,
    address receiver,
    uint256 shares,
    uint256 amount0,
    uint256 amount1
)
{
    // ... function implementation ...
}
```
1. ETH sent to this function could become trapped in the contract.
2. An attacker could potentially extract any dust ETH left in the contract.
3. Users might lose small amounts of ETH unintentionally.

## Recommendation
Implement a mechanism to refund any unused ETH at the end of the function. This can be done by calling the refundETH() function that already exists in the PeripheryPayments contract.
