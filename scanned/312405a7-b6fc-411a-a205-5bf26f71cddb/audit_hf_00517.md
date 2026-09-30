# [M] M-08 | Decreasing LP May Require Collateral

## Summary
Severity: Medium
Contest weight: 0.0581
Dataset id: 1975
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The [M-05'](https://www.notion.so/M-05-1348bda5828c81c086e6d49037558a91?pvs=21)s recommendation to let the user specify an amount of collateral to be added when decreasing a liquidity position has not been implemented which leaves the problem unsolved.

## Recommendation
Allow the user to supply additional collateral when decreasing their position.
