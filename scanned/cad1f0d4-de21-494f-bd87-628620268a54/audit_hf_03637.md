# [H] updateCollateral can be used to modify the to-

## Summary
Severity: High
Contest weight: 0.1648
Dataset id: 19706
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calling updateCollateral, a request is submitted to Gmx position router, and
some quote amount is transferred either in or out of the liquidity pool to the
GMXFuturesPoolHedger.
In LiquidityPool.sol: _getTotalPoolValueQuote uses the variable usedDeltaLiquidity
to track available quote amounts used on GMX as collateral.
The variable usedDeltaLiquidity will not be increased during the period in which
the request for increase is pending, but the quote will be sent to
GMXFuturesPoolHedger. A malicious user can call updateCollateral before
depositing into the LP, getting more shares.

## Recommendation
If quote amount has been transferred from liquidityPool, add pendingDelta into
totalPoolValue in function _getTotalPoolValueQuote
