# [M] M-13 | Collateral Of Epoch Ahead Can Be Stolen

## Summary
Severity: Medium
Contest weight: 0.0845
Dataset id: 1997
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When updating share price after an epoch, if no collateral was received, the share price is set to 1e18. This creates a significant issue as depositors can redeem their entire collateral even though no collateral was received after closing the liquidity position. Effectively, this allows depositors to withdraw funds that belong to the next epoch's depositors, who have already transferred their collateral into the contract.

## Recommendation
Initially, setting sharePrice to 0 instead of 1e18 was considered. However, this would affect the minting of new shares for the next epoch. As a solution, if no collateral is received, set the sharePrice for the current epoch to 0 while ensuring the sharePrice for the next epoch is reset to 1e18.
