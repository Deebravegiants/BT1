# [H] Calls to liquidate don't write down totalBor-

## Summary
Severity: High
Contest weight: 0.5906
Dataset id: 20113
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a pool is liquidated, the totalBorrows storage slot for the token in question should be decremented by debtToCover in order to keep the exchange rate of the corresponding pToken correct. When users call liquidate to liquidate a pool, they specify the amount of debt they want to cover. In the end this is used to write down the borrow amount of the pool in question: record.amount = borrows - debtToCover; However, the totalBorrows of the token isn't written down as well (like it should be). The finishLiquidation method correctly writes down the totalBorrows state. When a user calls liquidate to liquidate a pool, the exchange rate of the token (from its pToken) remains high (because the totalBorrows for the token isn't decremented). The result is that users that have deposited this ERC20 token are receiving a higher rate of interest than they should. Because this interest is not being covered by anyone the end result is that the last withdrawer from the vault will not be able to redeem their pTokens because there isn't enough of the underlying ERC20 token available. The longer the period over which interest accrues, the greater the incentive for LPs to withdraw early.

## Recommendation
The liquidate method should include the following line to write down the total borrow amount of the debt token being liquidated:
```solidity
info.totalBorrows = info.totalBorrows - debtToCover;
```
