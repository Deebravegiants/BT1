# [H] Incorrect calculation of the slippage when reducing positions .

## Summary
Severity: High
Reporter: stopthecap
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L307-L311
Type: audit-issue

## Details
# Incorrect calculation of the slippage when reducing positions .

## Summary
Incorrect calculation of the slippage when reducing positions .


## Vulnerability Detail
When reducing a position. `Unstoppable`calculates the `slippage (min_amount_out)` for you if 0 was specified.
The calculation is wrong because when reducing position you are not swapping the whole position amount, that would be done in the `close_position` function. In the `reduce_position` function, you have to specify, as a trader, the amount that you want to reduce your position by `_reduce_by_amount`.

The error relies in the following lines:
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L307-L311

```solidity
    if min_amount_out == 0: 
        min_amount_out = self._market_order_min_amount_out(
            position.position_token, position.debt_token, position.position_amount
        )
```

The slippage is being calculated with the entire `position.position_amount` instead of the actual `_reduce_by_amount` amount. This will cause a wrong slippage to be calculated, getting either a wrong amount back from the swap, or swaps not being able to take place because the slippage amount was to high.

## Impact
A wrong slippage will cause users to get an incorrect amount funds back from the swap, or if it is too high, transactions will fail

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L307-L311

## Tool used

Manual Review

## Recommendation

Change the `position.position_amount` variable for `_reduce_by_amount` 
```solidity
    if min_amount_out == 0: 
        min_amount_out = self._market_order_min_amount_out(
            position.position_token, position.debt_token, _reduce_by_amount
        )
```
