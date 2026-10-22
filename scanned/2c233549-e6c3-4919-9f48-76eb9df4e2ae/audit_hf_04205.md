# [H] H-03 | sUSD Drained From Vault When Liquidating Margin Only

## Summary
Severity: High
Contest weight: 0.2390
Dataset id: 21098
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the isMarginLiquidatable function, accounts are determined to be liquidatable when they have a
discountedMarginUsd of 0. However this puts the protocol at risk of taking on bad debt as there is
no requirement that the margin is able to cover liquidator fees as well as potential instantaneous
collateral price decreases.
Furthermore, an issue arises with low price collateral assets. An attacker can deposit a very small
amount of collateral (1 wei), and the validation for isMarginLiquidatable will return true, as the
discountedCollateralUsd will be 0 when collateral price is below 1e18:
discountedCollateralUsd += available.mulDecimal(discountedCollateralPrice);
The attacker will then liquidate the account and earn keeper fees, withdrawing sUSD from the V3
pool.

## Recommendation
Change the definition of the isMarginLiquidatable function such that positions will be considered
liquidatable by margin only if their discountedMarginUsd cannot cover liquidation keeper rewards,
optionally as well as a safety bound for potential downward collateral price gaps.
Additionally, validate that positions hold enough collateral so that they are not liquidatable by margin
only upon any action that would modify their position’s collateral.
