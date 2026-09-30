# [M] DPU-1 | Token Amount Added To USD Value

## Summary
Severity: Medium
Contest weight: 0.0770
Dataset id: 18501
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The estimatedRemainingCollateralUsd is incremented by a token amount rather than a token amount
multiplied by a price:
estimatedRemainingCollateralUsd += params.order.initialCollateralDeltaAmount().toInt256();
As a result, the main effect is estimatedRemainingCollateralUsd is much smaller than it should be
and the position is more likely to get closed out in its entirety unexpectedly due to the
MIN_COLLATERAL_USD check.

## Recommendation
Multiply the params.order.initialCollateralDeltaAmount() by the price of the collateral token to receive
a USD value before adding it with the estimatedRemainingCollateralUsd.
