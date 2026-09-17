# [M] StopLoss order needs a lower bound of price to prevent unnecessary loss of funds for the trader

## Summary
Severity: Medium
Reporter: GimelSec
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L432
Type: audit-issue

## Details
# StopLoss order needs a lower bound of price to prevent unnecessary loss of funds for the trader

## Summary

StopLoss order can help stop the loss when the current exchange rate is less than the trigger price that was set by the position owner. However, it could also cause unnecessary loss of funds if there isn’t a lower bound for the current price. 

## Vulnerability Detail


In `MarginDex.execute_sl_order`, it calls self._full_close or  self._partial_close when `sl_order.trigger_price >= current_exchange_rate`.
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L432
```vyper
def execute_sl_order(_trade_uid: bytes32, _sl_order_index: uint8):
    …

    current_exchange_rate: uint256 = Vault(self.vault).current_exchange_rate(
        trade.vault_position_uid
    )
    assert sl_order.trigger_price >= current_exchange_rate, "trigger price not reached"
    assert sl_order.executed == False, "order already executed"

    …
    if sl_order.reduce_by_amount >= position_amount:
        amount_out_received = self._full_close(trade, 0)
    else:
        amount_out_received = self._partial_close(trade, sl_order.reduce_by_amount, 0)

    log SlExecuted(_trade_uid, sl_order.reduce_by_amount, amount_out_received)
```

Normally, a user can set a StopLoss order to prevent loss of funds. Suppose that Alice set a StopLoss order with a trigger price 100. If the current exchange rate is 90, anyone can call `execute_sl_order` to help stop the loss. But if the current exchange rate is 50, Alice may not want to close the position at this price since the loss is already too much. 

## Impact

StopLoss order could make the owner lose more than desired.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L432


## Tool used

Manual Review

## Recommendation

Implement a lower bound for `current_exchange_rate` in StopLoss order.
