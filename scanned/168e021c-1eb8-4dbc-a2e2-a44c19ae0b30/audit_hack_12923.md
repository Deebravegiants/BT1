# [M] TakeProfit orders fail if greater than the current position

## Summary
Severity: Medium
Reporter: 0x00ffDa
Source: https://github.com/Unstoppable-DeFi/unstoppable-dex-audit/blob/4153c3e67ccc080032ba0bbaffd9a0c56a573070/contracts/margin-dex/MarginDex.vy#L378
Type: audit-issue

## Details
# TakeProfit orders fail if greater than the current position

## Summary
If a Margin DEX `Trade` contains orders that have a total size (i.e. the sum of each one's `reduce_by_amount`) that is greater than the size of the original position, then TakeProfit orders can fail to exit the position as intended. 

## Vulnerability Detail
The Margin DEX `Trade` struct contains an array of TakeProfit (TP) orders, `tp_orders`, and an array of StopLoss (SL) orders, `sl_orders`. Orders may be placed when opening a `Trade` or later via the `add_tp_order()` and `add_sl_order()` functions. There is no validation of order size for initial orders nor those added to a `Trade` later. So, orders can be defined that in aggregate exceed the size of the position they are intended to close.

In [`execute_tp_order()`](https://github.com/Unstoppable-DeFi/unstoppable-dex-audit/blob/4153c3e67ccc080032ba0bbaffd9a0c56a573070/contracts/margin-dex/MarginDex.vy#L378), when a TP order being executed is larger than the `Trade`'s current position size, `tp_order.reduce_by_amount == position_amount` will be false and result in calling `self._partial_close().`
```javascript
   if tp_order.reduce_by_amount == position_amount:
        amount_out_received = self._full_close(trade, tp_order.min_amount_out)
    else:
        amount_out_received = self._partial_close(
            trade, tp_order.reduce_by_amount, tp_order.min_amount_out
        )
```
`_partial_close()` in turn calls the `Vault` [`reduce_position()`](https://github.com/Unstoppable-DeFi/unstoppable-dex-audit/blob/4153c3e67ccc080032ba0bbaffd9a0c56a573070/contracts/margin-dex/Vault.vy#L290) function which contains the following assert:
```javascript
    assert position.position_amount >= _reduce_by_amount, "_reduce_by_amount > position"
```
In the scenario described above, this assert will fail causing the order execution to revert. The TP order will remain stored in the `Trade` struct for future execution attempts which will fail in the same way.

This issue does not require an obvious user error in defining the orders. While making a math error, or accidentally creating redundant orders could expose this issue, it is also possible to create a reasonable set of orders that would also encounter the issue. For example, a trader creates a TP order for 100% of a position at an elevated price and also creates 2 SL orders at low prices, each for 50% of the same position. If the higher priced SL order executes reducing the position by 50% and then the TP order later becomes eligible for execution, the TP order execution will attempt to sell 100% of the original position when only 50% remains.

## Impact
This issue can prevent TakeProfit orders from executing as intended and cause traders to miss profit opportunities.

Keeper bots would waste gas repeatedly attempting such impossible TakeProfit orders and (depending how they select orders) could starve other orders that would succeed.

## Code Snippet

## Tool used

Manual Review

## Recommendation
Modify the `execute_tp_order()` function:  if `reduce_by_amount` is greater than `position_amount`, call `self.full_close()`. (Use ">=" instead of "==" like the logic in `execute_sl_order()`.)
