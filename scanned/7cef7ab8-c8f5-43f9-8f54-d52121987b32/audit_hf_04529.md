# [M] M-10 | payDebt Should Update The interestRate

## Summary
Severity: Medium
Contest weight: 0.0688
Dataset id: 22093
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
1. The interestRate is calculated based on the utilizationRate. This rate is calculated by comparing
the delegated funds from the LPs to the given market, with the open interest of the market.
2. The payDebt function pays the LPs funds back that are automatically counted as delegated to the
given market.
Therefore the interestRate after calling payDebt changes, but is not updated in the current
implementation.

## Recommendation
Update the interestRate at the end of the payDebt function.
