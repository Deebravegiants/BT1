# [M] M-04 | Trades May Revert At Maximum Tick

## Summary
Severity: Medium
Contest weight: 0.0488
Dataset id: 22087
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The highestPrice for a swap is the exchange rate at the maximum tick. However, this exchange rate does not account for fees. Therefore, the highestPrice could prevent swaps which occur near the edge of the tick range, as the price after fees are included exceeds the highestPrice.

## Recommendation
Account for fees when calculating the highest price.
