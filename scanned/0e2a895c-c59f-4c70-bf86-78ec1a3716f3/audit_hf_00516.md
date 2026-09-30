# [M] M-07 | Fee Collector Can Hoard Fees

## Summary
Severity: Medium
Contest weight: 0.0661
Dataset id: 1974
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
M-01 of the previous audit was not addressed. Fee collectors can create under-collateralized positions and collateralize them using depositCollateral. Currently, there are no restrictions preventing a fee collector from creating an oversized liquidity position, which can monopolize all available liquidity and hoard fees, preventing other fee collectors from benefiting.

## Recommendation
Impose limits on the size of liquidity positions that fee collectors can create to ensure fair distribution of fees.
