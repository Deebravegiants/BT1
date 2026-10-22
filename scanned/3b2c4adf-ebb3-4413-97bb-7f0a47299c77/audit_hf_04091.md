# [M] GMXO-1 | Withdrawal Not Necessarily 50-50

## Summary
Severity: Medium
Contest weight: 0.1165
Dataset id: 20546
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calculating the swap price impact, it is assumed that withdrawing GM tokens provides 50% in
the short token and the other 50% in long tokens. According to documentation, "Assume under the
worst case, we liquidate 10% of the supply cap (which would entail a swap for half of that, 5%, to
USDC (short token))."
However, that is not necessarily the case because long and short tokens are withdrawn with their
value relative to the total pool value e.g. if the total pool value is $100 and $80 is from the long token,
80% of the withdrawn value will be in long tokens.
This assumption leads to an inaccuracy in the resulting price impact calculation, affecting the
calculated price of the GM token in the _getGmTokenPriceAfterPriceImpact function.

## Recommendation
Consider using the reader to get the current token ratios in the market and adjust the wethAmountIn
accordingly.
