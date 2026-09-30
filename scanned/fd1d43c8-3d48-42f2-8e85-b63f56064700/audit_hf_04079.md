# [M] GMXO-2 | Potentially Misleading PnL Factor

## Summary
Severity: Medium
Contest weight: 0.1231
Dataset id: 20532
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the GmxV2MarketTokenPriceOracle contract the call to function getMarketTokenPrice uses the
MAX_PNL_FACTOR_FOR_WITHDRAWALS PnL type to read the market token price from GMX. This is
typically the most constrictive PnL Type, such that trader proﬁt is capped to the smallest amount
relative to the MAX_PNL_FACTOR_FOR_TRADERS and MAX_PNL_FACTOR_FOR_DEPOSITS.
Consequently, the resulting price of the market token will be higher when measured using the more
constrictive MAX_PNL_FACTOR_FOR_WITHDRAWALS. This will ultimately cause a user’s collateral to
have a greater value than if the another type was used.
Out of an abundance of caution, it may be preferable to use the less constrictive
MAX_PNL_FACTOR_FOR_DEPOSITS, so that the collateral is not optimistically valued by capping the
PnL to a lower amount.

## Recommendation
Consider using the less constrictive MAX_PNL_FACTOR_FOR_DEPOSITS to read the price of the GM
token.
