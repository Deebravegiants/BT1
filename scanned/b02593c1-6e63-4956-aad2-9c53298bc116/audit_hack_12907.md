# [M] stop-loss orders doesn’t have any slippage protection

## Summary
Severity: Medium
Reporter: twicek
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L443-L447
Type: audit-issue

## Details
# stop-loss orders doesn’t have any slippage protection

## Summary
Due to the absence of slippage protection for stop loss orders, some users may find their positions being closed at a significantly lower price than the `trigger_price` they selected.

## Vulnerability Detail
Users cannot choose the minimum `amount_out_received` in `execute_sl_order` since `_min_amount_out` parameter of `_full_close` and `_partial_close` is hard-coded to `0`:

[MarginDex.vy#L443-L447](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L443-L447)
```solidity
amount_out_received: uint256 = 0
    if sl_order.reduce_by_amount >= position_amount:
        amount_out_received = self._full_close(trade, 0)
    else:
        amount_out_received = self._partial_close(trade, sl_order.reduce_by_amount, 0)
```

This will lead for some users to get their trade potentially closed very far from their `trigger_price`, especially if they are interacting with illiquid and high volatility pools.

## Impact
Missing slippage protection will lead users to potentially sell at the worst possible price.

## Code Snippet
[MarginDex.vy#L443-L447](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L443-L447)

## Tool used

Manual Review

## Recommendation
Allow users to specify the minimum `amount_out_received`. This will allow users to set an interval in which they are willing to sell, for instance a user may want to sell if the price reaches a given `trigger_price`, but only if `amount_out_received > min_amount_out`.
