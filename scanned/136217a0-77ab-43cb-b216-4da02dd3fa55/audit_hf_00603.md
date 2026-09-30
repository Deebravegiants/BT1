# [M] M-01 | Mismatching Baseline Values

## Summary
Severity: Medium
Contest weight: 0.0598
Dataset id: 2102
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
After the updates, the blv is calculated based on the upper ﬂoor tick in the MarketMaking,
CreditFacility, and LoopFacility contracts. However, in the BPOOL contract, it is still calculated using
the lower ﬂoor tick.
The BaselineInit.launch function uses the baseline value from the BPOOL contract when calculating
capacity, which creates a discrepancy.

## Recommendation
Update the getBaselineValue function in BPOOL contract.
