# [M] POSU-1 | Negative PnL Ignored In Sufficient Collateral Check

## Summary
Severity: Medium
Contest weight: 0.1135
Dataset id: 18507
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The PnL of the remaining position is no longer accounted for during the
willPositionCollateralBeSufficient check.
In the case where the remaining position PnL is positive, this avoids errantly counting profit towards
the remaining position’s collateral.
However, in the case where the remaining position PnL is negative, this check fails to consider that
the remaining PnL could make the actual value backing the position significantly smaller than the
minCollateralUsdForLeverage.
It may be prudent to consider the PnL of the remaining position, only when it is in a loss. This way
the negative PnL, which would be subtracted from the collateral in the position, is taken into account.

## Recommendation
Consider factoring the remaining position’s PnL into the willPositionCollateralBeSufficient check,
only when the remaining PnL is negative and would be subtracted from the collateral in any future
order.
