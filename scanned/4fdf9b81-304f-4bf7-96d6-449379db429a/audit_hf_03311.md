# [C] DPCU-1 | Wrong Token Amount Applied

## Summary
Severity: Critical
Contest weight: 0.2236
Dataset id: 18157
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the case where the remainingCollateral for a position is negative during a liquidation, the getLiquidationValues function is called. The values.pnlTokenForPool is used in the returned values. However the values.pnlAmountForPool computed on line 347 is strictly a collateral token amount. A position may be in profit and still be liquidated due to the minCollateralUsdForLeverage combined with a depreciation in the user’s collateral token price. Therefore the pnlTokenForPool may be different from the collateral token, in which case a shortToken amount could be applied as a longToken amount or vice-versa. This will drastically perturb the poolAmount for the pnlTokenForPool in such a way that could leave the market insolvent or simply cause extreme loss for the market depositors.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/DPCU_1.ts

## Recommendation
Adjust the getLiquidationValues function so that it accounts for the cases where traders are being liquidated in profit.
