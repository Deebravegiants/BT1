# [M] M-12 | Arbitrage Attack After Slide Operation

## Summary
Severity: Medium
Contest weight: 0.0714
Dataset id: 21493
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The market making slide operation rebalances the liquidity structure when active tick goes below a certain threshold. In case the heavy selling pushes the price to the FLOOR, the slide operation will be the only range with reserves. When liquidity is added to the FLOOR, bAssets will be minted in this range. This scenario allows arbitrager to buy tokens at discount, trigger sweep/bump operations, and profit from it.

## Recommendation
Verify the initial liquidity structure does not allow these arbitrage attacks to take place.
