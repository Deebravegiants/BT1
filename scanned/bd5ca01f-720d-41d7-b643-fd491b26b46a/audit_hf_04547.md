# [M] M-07 | Liquidation Rewards Should Not Use Fill Price

## Summary
Severity: Medium
Contest weight: 0.1096
Dataset id: 22112
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
getRequiredMarginWithNewPosition calculates the required margin for a new position by adding
possible liquidation rewards to the required margin for the position.
The issue lies with how the liquidation rewards are calculated using fillPrice instead of an oracle
price:
runtime.accumulatedLiquidationRewards = marketConfig.calculateFlagReward(
MathUtil.abs(newPositionSize).mulDecimal(fillPrice));
1. This in contradiction with how isEligibleForLiquidation is calculated which uses an oracle price.
2. fillPrice includes a premium/discount according to how the trade affects the market skew. This
would unfairly make shorts require a higher margin when they balance the market and less when
they imbalance the market.

## Recommendation
Use oracle price to calculate the liquidation rewards.
