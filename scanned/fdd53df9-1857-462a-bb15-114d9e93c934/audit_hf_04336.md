# [M] M-11 | Operations Using Outdated Circulating Supply

## Summary
Severity: Medium
Contest weight: 0.0719
Dataset id: 21492
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a credit is defaulted, its collateral is sent directly to the BPOOL contract through the _burnDefaultedCollateral function. This creates a temporary condition where the circulating supply is higher than expected, if the market making operations are executed before defaulting the expired loans. In the bump operation, an increased circulating supply will effectively mint more tokens than expected for the inflation basis.

## Recommendation
Ensure defaultOutstanding is executed at the start of market making operations.
