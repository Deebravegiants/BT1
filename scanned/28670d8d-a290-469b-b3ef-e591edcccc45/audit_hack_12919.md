# [H] Hardcoded slippage will make orders to be stuck in specific market conditions

## Summary
Severity: High
Reporter: stopthecap
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L426
Type: audit-issue

## Details
# Hardcoded slippage will make orders to be stuck in specific market conditions

## Summary
Hardcoded slippage will make orders to be stuck in specific market conditions

## Vulnerability Detail
Currently the calculation of the slippage for swapping, uses a constant named `liquidate_slippage` , which is a value choosen by the owner. This slippage will be used for the calculation in every swap that needs of unstoppables's calculation, in any market condition. Therefore, it is the same to say that the slippage is calculated using a hardcoded parameter.

https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L426

It does not just on limit orders, also in spot orders, where it is specified the variable `MAX_SLIPPAGE` has the value to calculate the `min_amount_out` for swapping when executing `dca` orders
## Impact

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L426
## Tool used

Manual Review

## Recommendation
Use the uniswap helper library to calculate slippage instead of hardcoding it
