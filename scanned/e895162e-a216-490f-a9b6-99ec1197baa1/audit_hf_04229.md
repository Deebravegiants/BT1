# [M] M-07 | Small Positions Accrue Bad Debt In The System

## Summary
Severity: Medium
Contest weight: 0.1408
Dataset id: 21125
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can set their own keeperFeeBufferUsd and limitPrice, potentially forcing bad debt into the system. This is because IM and MM have minimum values as follows: IM = 2% * position.size + fixed = 2% * p.size + 50 MM = 1% * position.size + fixed + liqFlagReward + keeper reward = 1% * p.size + 50 + liqFlagReward + keeper reward While the maximum value for keeperFeeBufferUsd is 100 USD. Currently, it's possible to place an order with keeperFeeBufferUsd > collateral > IM && MM, choosing the maximum keeperFeeBufferUsd and an unrealistic limitPrice, using it to cancel your order later and accrue bad debt of keeperFeeBufferUsd - collateral. Similarly users can submit orders that would decrease their position size by a trivial amount and avoid the liquidatable checks upon settlement, allowing the keeper fee to place their position in a liquidatable or even insolvent state.

## Recommendation
Consider raising the minMarginUsd such that it would not be possible for a keeper fee to exceed an account’s margin and cause bad debt to occur. Otherwise consider preventing orders from being created where the keeper fee would cause the account to ultimately become liquidatable.
