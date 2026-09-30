# [M] GMOCL-3 | More Restrictive PnL Type Used

## Summary
Severity: Medium
Contest weight: 0.1481
Dataset id: 128
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the GmOracleWithAggregator contract the reported price uses the MAX_PNL_FACTOR_FOR_TRADERS PNL_TYPE to read the market token price from GMX. However this PnL type is less constrictive on the trader PnL than the MAX_PNL_FACTOR_FOR_DEPOSITS. Therefore when the market PnL is in between these two factors like so: MAX_PNL_FACTOR_FOR_TRADERS < PnL in market < MAX_PNL_FACTOR_FOR_DEPOSITS Then the resulting price of the market token will be higher when measured using the more constrictive PnL factor for traders. Therefore the user’s collateral will be valued higher using the PnL factor for traders than compared to the PnL factor for deposits. Out of an abundance of caution, it may be preferable to use the less constrictive max PnL for deposits, so that the collateral is not optimistically valued by capping the PnL to a lower amount. This is somewhat arbitrary as GM tokens cannot be redeemed as long as the pnl to pool ratio exceeds the MAX_PNL_FACTOR_FOR_WITHDRAWALS, which is the lowest of these PnL factors.

## Recommendation
Consider using the less constrictive MAX_PNL_FACTOR_FOR_DEPOSITS to read the price of the GM token.
