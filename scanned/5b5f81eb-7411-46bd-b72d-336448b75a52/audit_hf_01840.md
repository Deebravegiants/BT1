# [M] Pool Delegates can accidentally lock out of their funds LPs in the middle of redeeming.

## Summary
Severity: Medium
Contest weight: 0.0866
Dataset id: 10243
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Pool delegates are allowed to change the withdrawal manager address at any time using the setWithdrawalManager() function. Changing this address, even with good intentions in mind, poses the problem of locking out of their shares the LPs in the process of redeeming. This happens since the storage mappings: exitCycleId and lockedShares, as well as the ERC-20 tokens (shares) of the LPs waiting for their withdrawal window will not have migrated to the new address, and will now be locked in the previous withdrawalManager proxy contract.

## Recommendation
Remove the setWithdrawalManager() function or pause it by default.
