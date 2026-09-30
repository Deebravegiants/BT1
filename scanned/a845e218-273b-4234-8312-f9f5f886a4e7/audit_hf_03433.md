# [M] DPCU-4 | adjustedPriceImpactDiffAmount Minimized

## Summary
Severity: Medium
Contest weight: 0.0723
Dataset id: 18740
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
While converting the adjustedPriceImpactDiffUsd to a collateral token amount, the collateralTokenPrice.max is used. However the collateralTokenPrice.max will result in a smaller adjustedPriceImpactDiffAmount. In scenarios where the max price has a nontrivial difference with the min price, e.g. a depeg event, this can lead to users paying significantly less for this capped price impact amount than they ought to.

## Recommendation
Use the collateralTokenPrice.min when translating the adjustedPriceImpactDiffUsd to a adjustedPriceImpactDiffAmount.
