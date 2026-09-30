# [M] M-04 | flagReward Incorrectly Based On marginUsd

## Summary
Severity: Medium
Contest weight: 0.0835
Dataset id: 21105
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the validateNextPositionEnoughMargin function the Maintenance Margin is calculated through the
getLiquidationMarginUsd function. However the invocation wrongly passes in the nextMarginUsd to
compute the flagReward when it should be passing in collateralUsd.
The flagPosition function computes the flagReward based upon the collateralUsd of the position,
therefore using nextMarginUsd to compute the flagReward inaccurately accounts for the amount in
the liquidation check.

## Recommendation
Provide the collateralUsd as the second to last parameter when invoking the
getLiquidationMarginUsd function within the validateNextPositionEnoughMargin function.
