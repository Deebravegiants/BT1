# [M] `is_accepting_new_orders` can be bypassed in `MarginDex.open_trade`.

## Summary
Severity: Medium
Reporter: GimelSec
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L337
Type: audit-issue

## Details
# `is_accepting_new_orders` can be bypassed in `MarginDex.open_trade`.

## Summary

When `is_accepting_new_orders` is set to true, no new order should be accepted.  `MarginDex.add_tp_order` and `MarginDex.add_sl_order` are paused. But users can still call `MarginDex.open_trade` with `_tp_orders` and `_sl_orders`

## Vulnerability Detail

Both `MarginDex.add_tp_order` and `MarginDex.add_sl_order` are paused when  `is_accepting_new_orders` is set to true.
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L337
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L358
```vyper
def add_tp_order(_trade_uid: bytes32, _tp_order: TakeProfitOrder):
    …
    assert self.is_accepting_new_orders, "paused"
    …


@external
def add_sl_order(_trade_uid: bytes32, _sl_order: StopLossOrder):
    …
    assert self.is_accepting_new_orders, "paused"
    …
```

But there is no check in `MarginDex._open_trade`. The caller can add orders on their trades.
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L193-L199
```vyper
def _open_trade(
    _account: address,
    _position_token: address,
    _min_position_amount_out: uint256,
    _debt_token: address,
    _debt_amount: uint256,
    _margin_amount: uint256,
    _tp_orders: DynArray[TakeProfitOrder, 8],
    _sl_orders: DynArray[StopLossOrder, 8],
) -> Trade:
    …

    trade: Trade = Trade(
        {
            uid: position_uid,
            account: _account,
            vault_position_uid: position_uid,
            tp_orders: _tp_orders,
            sl_orders: _sl_orders,
        }
    )

    self.open_trades[position_uid] = trade
    self.trades_by_account[_account].append(position_uid)

    log TradeOpened(_account, position_uid, trade)
    return trade
```

## Impact

Setting `is_accepting_new_orders` to true can put protocol in defensive or winddown mode. `Open_trade` can still work. But no new order should be added.

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L832
> Allows admin to put protocol in defensive or winddown mode.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L193-L199
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L337
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L358


## Tool used

Manual Review

## Recommendation

Add a check in `MargixDex._open_trade`
```diff
def _open_trade(
    _account: address,
    _position_token: address,
    _min_position_amount_out: uint256,
    _debt_token: address,
    _debt_amount: uint256,
    _margin_amount: uint256,
    _tp_orders: DynArray[TakeProfitOrder, 8],
    _sl_orders: DynArray[StopLossOrder, 8],
) -> Trade:
    …
+   assert self.is_accepting_new_orders or (len(_tp_orders) == 0 and len(_sl_orders) == 0)
    trade: Trade = Trade(
        {
            uid: position_uid,
            account: _account,
            vault_position_uid: position_uid,
            tp_orders: _tp_orders,
            sl_orders: _sl_orders,
        }
    )

    self.open_trades[position_uid] = trade
    self.trades_by_account[_account].append(position_uid)

    log TradeOpened(_account, position_uid, trade)
    return trade
```
