# [M] IPU-1 | Incongruent Price Impact

## Summary
Severity: Medium
Contest weight: 0.1325
Dataset id: 18857
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The price impact amount represented by the executionPrice may not match the price impact amount calculated. This is because the index price used to calculate the price impact amount may differ from the index price used in getExecutionPriceForIncrease. Consider the following scenario where a trader increases a long position: Price Impact USD = -$100; Index Price = ($50, $100). In IncreasePosition: index price = indexTokenPrice.min = $50. price impact amount = -$100 / $50 = -2 tokens. In BaseOrderUtils: index price = indexTokenPrice.pickPriceForPnl(isLong, true) = $100. price impact amount = -$100 / $100 = -1 tokens. The discrepancy is because $100 is used for the index price in getExecutionPriceForIncrease rather than $50. As a result, the executionPrice doesn’t reflect the price impact amount which is added to the baseSizeDeltaInTokens.

## Recommendation
executionPrice can simply be calculated as: executionPrice = params.order.sizeDeltaUsd() / cache.sizeDeltaInTokens to reflect the price impact amount used and then emitted in the event.
