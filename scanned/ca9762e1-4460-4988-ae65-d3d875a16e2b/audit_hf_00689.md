# [M] M-10 | Incorrect Calculation Of currentSize

## Summary
Severity: Medium
Contest weight: 0.0606
Dataset id: 2240
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In _validateMintAmount, we should avoid using currentSize = long_ + short_ because maxMarketValue returns the maximum allowable value for each side of the market. Let's say the maxMarketSize for each side of the market is 1000, meaning we can open 1000 in long and 1000 in short using the market, which is possible. However, if we do the same using LeveragedToken, it causes a DoS.

## Recommendation
currentSize = isLong * long_ : short_
