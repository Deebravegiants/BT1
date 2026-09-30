# [H] MarketUtils.getPoolValueInfo() does not use

## Summary
Severity: High
Contest weight: 0.3794
Dataset id: 20025
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
!maximize when evaluating impactPoolUsd, leading to wrong logic of maximizing or minimizing the pool value.
MarketUtils.getPoolValueInfo() does not use !maximize when evaluating impactPoolUsd, leading to wrong logic of maximizing or minimizing the pool value.
This function is reachable by a withdrawal order to determine the amount of long/short tokens to withdraw, as a result, such amounts might be overestimated due to the wrong logic in MarketUtils.getPoolValueInfo(), leading to possible draining of the pool in the long run!
MarketUtils.getPoolValueInfo() is used to get the USD value of a pool. It is called in a withdrawal order execution to determine the amount of long/short tokens to withdraw via flow WithdrawalUtils.executeWithdrawal() -> _executeWithdrawal() -> WithdrawUtils.executeWithdrawal() -> _executeWithdrawal() -> _getOutputAmounts() -> MarketUtils.getPoolValueInfo(). Let's look at MarketUtils.getPoolValueInfo() assuming maximize = false. (which is the case in a withdrawl order). That is, we are trying to minimize the pool value. This is understandable since we need to minimize the output amounts of withdrawn tokens in favor of the system. The analysis for the case of maximize = true is similar.
cts/market/MarketUtils.sol#L289-L375
There are a few items we need to calculate:
1. longTokenUsd: we pick price longTokenPrice.pickPrice(maximize);
2. shortTokenUsd: we pick price shortTokenPrice.pickPrice(maximize)
3. totalBorrowingFee for the long side, no optimization option.
4. totalBorrowingFee for the short side, no optimization option.
5. impactPoolUsd, indexTokenPrice.pickPrice(maximize) is chosen, which is wrong, since this is to be subtracted from the total Usd value, we need to use indexTokenPrice.pickPrice(!maximize), just like the next item for calculating Pnl.
6. longPnl and shortPnl, both use the mode !maximize since both of them will be subtracted from the total value.
In summary, just like calculating Pnl, we need to use indexTokenPrice.pickPrice(!maximize) instead of indexTokenPrice.pickPrice(maximize) to calculate impactPoolUsd. Only in this way,

## Recommendation
In function MarketUtils.getPoolValueInfo() we need to use indexTokenPrice.pickPrice(!maximize) instead of indexTokenPrice.pickPrice(maximize) to calculate impactPoolUsd.
