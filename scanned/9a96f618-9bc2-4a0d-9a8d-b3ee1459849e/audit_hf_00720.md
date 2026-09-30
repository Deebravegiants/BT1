# [M] M-13 | payDebt Affects Utilization Without Update

## Summary
Severity: Medium
Contest weight: 0.1030
Dataset id: 2271
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the payDebt function when the caller provides sUSD to repay an account’s debt the creditCapacity of the market will be immediately incremented by the amountToBurn. As a result the utilization of the market will decrease, as the delegatedCollateralValueUsd which relies on the creditCapacity will increase. The utilization of the market will also be affected by the updateDebtAndCollateral function call for sUSD collateral repayments from the account. However the utilization rate is not recomputed in the payDebt function so this utilization change is not reﬂected in the resulting utilization charged over any period where payDebt occurs.

## Recommendation
Always recompute the utilization of the market after calling depositMarketUsd at the end of payDebt function.
