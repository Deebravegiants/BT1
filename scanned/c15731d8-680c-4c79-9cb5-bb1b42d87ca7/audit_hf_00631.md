# [M] M-24 | Profit Can Only Be Realized With The Pool’s Collateral Token

## Summary
Severity: Medium
Contest weight: 0.1969
Dataset id: 2132
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The CollateralPool contract calculates its overall assets under management by summing balances of its primary collateral token and any additional tokens that arrive via fees, trader losses or rebalance operations. Although traders can open positions based on this total multi-token value, the code that settles profit only checks the availability of the main collateral, see CollateralPool.realizeProfit function below. When traders attempt to realize profits, if there is insufficient balance of the primary collateral, even though other tokens in the pool collectively exceed the required amount, the function realizeProfit will revert, blocking some traders from closing and profiting from their positions due to the following require check: require(wad = _liquidityBalances[token], InsufficientLiquidity(wad, _liquidityBalances[token])); The expected approach would be for rebalancers to convert these other tokens into the main collateral token, but there is no guarantee that this can be done quickly as it requires that the pool1’s foreign token is held by any of the other pools. Therefore a significant time gap might occur before rebalancing is performed. Furthermore, even if the protocol attempts to swap these foreign tokens for the main collateral on, for example through Uniswap, the pool would have to pay a high fee of around 5%, causing the CollateralPool to lose a portion of its AUM with each of those swaps.

## Recommendation
Consider updating the realizeProfit function so trader’s PNL can be paid with multiple tokens. These tokens should be any supported collateral token by the protocol and held by the actual collateral pool.
