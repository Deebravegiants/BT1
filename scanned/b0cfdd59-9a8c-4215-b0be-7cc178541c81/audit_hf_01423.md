# [M] M-5 Potential Deposit Blockage

## Summary
Severity: Medium
Contest weight: 0.0662
Dataset id: 7351
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The maxDeposit sUSX.sol#L229 will attempt to calculate the maximum amount that can be deposited based on the new mintCap, but it will revert due to underflow because mintCap - totalSupply is negative. This situation is not triggered by user actions but can occur if the admin changes the mintCap value. This issue is marked as medium because owner actions can lead to a temporary contract lock.

## Recommendation
We recommend avoiding reverting by returning 0 in maxDeposit.
