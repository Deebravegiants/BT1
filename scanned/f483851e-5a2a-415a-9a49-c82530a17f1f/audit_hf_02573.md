# [H] spotTimeWeightedPrice and withSwapping may conflict

## Summary
Severity: High
Contest weight: 0.2032
Dataset id: 13902
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The autoRebalance function has two input parameters.
useOracleForNewBounds : If false , use spotTimeWeightedPrice to
determine the new baseLower and baseUpper
withSwapping : If true , when the difference between spot and oracle prices
is too large, some tokens will be swapped to make the spot price closer to the
oracle price.
The following scenario occurs when useOracleForNewBounds is false and
withSwapping is true and the price difference between spot and oracle is too
large. There is a discrepancy between the spot price after the swap and the
spotTimeWeightedPrice obtained before the swap. The baseLower and
baseUppe are determined by the price before the swap. This will lead to an
In extreme cases, this may result in mint failure or uncompensated losses due
to the use of unreasonable liquidity ranges.

## Recommendation
Make sure the swap limit price is the same as priceRefForBounds.
