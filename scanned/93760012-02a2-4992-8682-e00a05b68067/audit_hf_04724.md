# [H] BBLiquidation/SGLLiquidation::_updateBorrowAnd-

## Summary
Severity: High
Contest weight: 0.2306
Dataset id: 22535
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When handling liquidation in BigBang and Singularity market, the protocol ensures that the liquidatee has enough collateral to cover for the liquidation and reward. If that's not the case, then the reward for the liquidator is shrunk proportionally to the bad debt incurred by the protocol.
However the liquidator can simply choose to bypass this protection by setting a max repay amount small enough so it can be covered by the collateral of the liquidatee. This enables the liquidator to get full reward on a partial liquidation, and leaves the protocol with only bad debt collateralPartInAsset < borrowAmountWithBonus
However the liquidator can reduce the amount to repay arbitrarily by setting the maxBorrowPart parameter.
Thus the liquidator can always choose to execute the second branch, ensuring full reward.
The protocol incurs more bad debt than due because liquidator can bypass bad debt protection mechanism

## Recommendation
Ensure a minimal repay amount in order for the liquidation to always make the account solvent, this would make it impossible for the liquidator to reduce the repay amount arbitrarily
