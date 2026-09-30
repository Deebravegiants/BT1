# [M] M-01 | Fee Collector Can Horde Fees

## Summary
Severity: Medium
Contest weight: 0.0595
Dataset id: 1983
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Fee collectors can create under-collateralized positions and collateralize them using depositCollateral. Currently, there are no restrictions preventing a fee collector from creating an oversized liquidity position, which can monopolize all available liquidity and hoard fees, preventing other fee collectors from benefiting.

## Recommendation
Impose limits on the size of liquidity positions that fee collectors can create to ensure fair distribution of fees.
