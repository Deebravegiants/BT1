# [M] SWPU-1 | Max Price Used For Swap Pricing

## Summary
Severity: Medium
Contest weight: 0.1039
Dataset id: 18496
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The getLatestPrice function is used to get prices for swaps, however, this will return the custom
price for the token if any is set. In the case of a MarketIncrease long order, the min and max price for
the customPrice are both the max of the primaryPrice. The inverse can be true using a
MarketDecrease short order.
This way users can get more favorable execution while swapping for the index token during a Market
order.
This invalidates the implemented protection where the inToken is supposedly valued at the minimum
price and the outToken is valued at the max price:
cache.amountOut = cache.amountIn * cache.tokenInPrice.min / cache.tokenOutPrice.max;

## Recommendation
Do not allow the max of the primaryPrice to be used as the price for the tokenIn during a swap.
