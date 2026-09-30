# [M] GMXC-7 | Share Amount As amountMarketToken

## Summary
Severity: Medium
Contest weight: 0.1000
Dataset id: 131
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the liquidate function, when additional value is necessary to cover the borrowed amount and the Order.sendValueInCollateral function is called, the provided amountMarketToken is computed from collateralShare - userCollateralShare[user]. However this is a share amount rather than an elastic market token amount. Currently there is no strategy for GM tokens in the DegenBox, however if there were to be a strategy that increased the elastic supply of GM tokens relative to the base shares, then the share value provided to the Order.sendValueInCollateral would be inaccurate.

## Recommendation
Consider converting the outstanding collateralShare amount to a market token amount with the DegenBox.toAmount function before providing this amount as the amountMarketToken for the sendValueInCollateral function.
