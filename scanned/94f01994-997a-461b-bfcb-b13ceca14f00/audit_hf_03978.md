# [M] Delisted collateral will be permanently trapped

## Summary
Severity: Medium
Contest weight: 0.0423
Dataset id: 20344
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
withdraw has the isWhitelistedCollateral modifier on it meaning that after a collateral has been delisted it cannot be withdrawn and will be permanently stuck in the contract.
See summary.
Delisted collateral will be permanently stuck in the exchange contract

## Recommendation
Remove the isWhitelistedCollateral from withdraw
