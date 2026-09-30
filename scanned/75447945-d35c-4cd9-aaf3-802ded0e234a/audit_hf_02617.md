# [H] H-1 checkpoint() resets totalEffectiveSupply

## Summary
Severity: High
Contest weight: 0.8581
Dataset id: 14129
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When ResolvStaking.checkpoint() is called with the zero address as the user, the variable totalEffectiveSupply is reset to zero because the function ResolvStakingCheckpoints.updateEffectiveBalance() returns zero for the zero address.
```solidity
• ResolvStakingCheckpoints.sol#L128
```
A hacker can pass the zero address to the checkpoint() function via ResolvStaking.updateCheckpoint(). Resetting totalEffectiveSupply to zero would prevent users from being able to withdraw funds from the contract due to an underflow at the following line:
```solidity
newTotalEffectiveSupply =
// (
_params.totalEffectiveSupply // =0
- oldEffectiveBalance // >0
// )
+ newEffectiveBalance;
```
ResolvStakingCheckpoints.sol#L163

## Recommendation
1. In ResolvStakingCheckpoints.updateEffectiveBalance(), return the current totalEffectiveSupply when the user address is zero.
2. Change the order of operations when calculating newTotalEffectiveSupply, adding first, subtracting last:
```solidity
newTotalEffectiveSupply =
(_params.totalEffectiveSupply +
newEffectiveBalance)
- oldEffectiveBalance;
```
Client's Commentary:
56f2fe95
2.3 Medium
Not Found
2.4 Low
