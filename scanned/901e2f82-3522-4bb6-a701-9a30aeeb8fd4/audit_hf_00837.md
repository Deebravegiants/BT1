# [M] M-08 | Some Liquidations Will Accrue Bad Debt

## Summary
Severity: Medium
Contest weight: 0.1038
Dataset id: 2573
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The liquidation ratio for SNX token is specified as 1.05e18 which means liquidations will only be possible if an account is holding less than 1.05X collateral against 1.00X debt. liquidationRewardD18 is specified as 50 SNX token. When liquidating, what will be distributed to other LP's is: collateralLiquidated - liquidationReward. If this amount ever becomes less than debtLiquidated, then it will accrue bad debt to other LP's. Considering the current configurations, this means any account liquidated that has less than 1050 SNX as collateral will cause other LP's to accrue bad debt.

## Recommendation
Either increase the liquidation ratio so that bad debt accruing will be less likely to achieved (doesn't solve the problem completely), or introduce a dynamic liquidation reward mechanism that will both incentivize the liquidator but don't create bad debt.
