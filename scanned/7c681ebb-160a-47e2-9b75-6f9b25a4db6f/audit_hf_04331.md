# [M] M-07 | Rebalance Threshold May Prevent Sliding Operation

## Summary
Severity: Medium
Contest weight: 0.1020
Dataset id: 21487
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The REBALANCE_THRESHOLD is a param set in the constructor of MarketMaking policy. This means that this param can be configured by the protocol. Although the current deployment script sets the initial value to 1, any value above this will cause unexpected behavior of the slide operation. This is due to the fact that if checkpoint and active ticks are less than 2 TS away from the floor tick, slide can't be triggered if the price trades into the FLOOR range (canSlide tick will be located below the floor tick). Therefore, the protocol won't be able to correctly rebalance the liquidity when there is heavy selling of bAssets.

## Recommendation
Remove the REBALANCE_THRESHOLD from the constructor params and set it as a constant inside the MarketMaking policy, with value 1.
