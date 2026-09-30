# [H] POSU-1 | Profit Included In Remaining Collateral

## Summary
Severity: High
Contest weight: 0.2109
Dataset id: 18173
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The PnL of a position is added to the current collateral when calculating the remainingCollateralUsd. This is logically sound when a trader’s PnL is negative, as their losses will be subtracted from their collateral upon closing their position. However, when a position is in profit, there is no effect on the position’s collateral since the profits come from the pool. In the case where positions are in profit, adding the profit to the remainingCollateralUsd misrepresents how much collateral value actually remains. Furthermore, if a position is profitable, this profit can be used as collateral to continue to increase the position size. This allows trader’s to open positions with far greater leverage than the minCollateralFactor.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/POSU_1.ts

## Recommendation
Do not count profit as a part of the remaining collateral of a position.
