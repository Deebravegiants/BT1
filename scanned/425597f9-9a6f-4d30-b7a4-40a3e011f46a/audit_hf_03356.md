# [M] DPCU-5 | Remaining Collateral Adjusted To Revert

## Summary
Severity: Medium
Contest weight: 0.1296
Dataset id: 18210
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When values.remainingCollateralAmount is less than or equal to collateralCache.adjustedPriceImpactDiffAmount, values.remainingCollateralAmount is set to 0 and the collateralCache.adjustedPriceImpactDiffAmount is placed in the holding area. The position is stamped with a collateral amount of 0 in DecreasePositionUtils.sol on line 195. Once validatePosition is entered, validateNonEmptyPosition will be called which will revert due to the 0 collateral amount with the EmptyPosition error. Overall, the position’s remainingCollateral is updated only to subsequently revert when validatePosition is called. Furthermore, this may open the market to scenarios where a user can inﬂuence when their order is executed and create a risk-free trade as the order stays in the store with the same updatedAtBlock.

## Recommendation
Do not set the remainingCollateralAmount to 0 only to have the order revert later on with an EmptyPosition error. Instead consider leaving some remainingCollateral or reverting with a separate error so that the order is cancelled or frozen.
