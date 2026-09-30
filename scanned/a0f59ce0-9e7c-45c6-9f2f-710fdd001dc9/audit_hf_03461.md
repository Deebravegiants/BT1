# [M] DPCU-4 | Non-zero Effect On Pool Value

## Summary
Severity: Medium
Contest weight: 0.1562
Dataset id: 18875
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the index token is the same as the PnL token, the positive price impact amount deducted from the position impact pool is maximized (round up division & divide by min price) meanwhile the deduction amount for the pool is minimized (round down division & divide by max price). Similarly, when the index token is the same as the collateral token, the negative price impact amount added to the position impact pool is minimized (multiplied by the min price and divided by the max price) while the pool amount delta is not. This creates a tendency for positive price impact to err on the side of increasing the pool value as stated in the comment on line 171. Because of the unequal effects on the impact pool amount and the pool amount there is an immediate non-zero impact on the pool value. This behavior opens up the possibility for market depositors to manipulate price impact and absorb the position impact pool value. Such a manipulation can be straightforward when the index token is the same as either the collateral token or PnL token.

## Recommendation
When the index token is the same as the collateral token or the PnL token consider using the same prices to convert usd values to token values during both positive and negative price impact accounting.
