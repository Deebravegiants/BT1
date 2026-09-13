# [M] New trades are still accepted by `MarginDex` when `self.is_accepting_new_orders` is `False`

## Summary
Severity: Medium
Reporter: Dug
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L126-L202
Type: audit-issue

## Details
# New trades are still accepted by `MarginDex` when `self.is_accepting_new_orders` is `False`

## Summary

The `MarginDex` contract has a `self.is_accepting_new_orders` flag that is documented as follows.

> Allows admin to put protocol in defensive or winddown mode.
> Open trades can still be completed but no new trades are accepted.

However, the `MarginDex` contract does not check this flag when accepting new trades. This means that new trades can be accepted even when the flag is set to `False`.

## Vulnerability Detail

The `open_trade` function has no checks for the `self.is_accepting_new_orders` flag.

```vyper
@nonpayable
@external
def open_trade(
    _account: address,
    _position_token: address,
    _min_position_amount_out: uint256,
    _debt_token: address,
    _debt_amount: uint256,
    _margin_amount: uint256,
    _tp_orders: DynArray[TakeProfitOrder, 8],
    _sl_orders: DynArray[StopLossOrder, 8],
) -> Trade:
    assert (_account == msg.sender) or self.is_delegate[_account][msg.sender], "unauthorized"

    return self._open_trade(
        _account,
        _position_token,
        _min_position_amount_out,
        _debt_token,
        _debt_amount,
        _margin_amount,
        _tp_orders,
        _sl_orders,
    )
```

Nor, does the internal `_open_trade` function.

```vyper
@internal
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
    """
    @notice
        Creates a new Trade for user by opening a
        leveraged spot position in the Vault.

        Requires the user to have a positive margin
        balance in the Vault.
        Requires liquidity to be available in the Vault.

        All trades and their underlying positions are
        fully isolated.
    """
    buy_amount: uint256 = _debt_amount + _margin_amount

    position_uid: bytes32 = empty(bytes32)
    amount_bought: uint256 = 0
    (position_uid, amount_bought) = Vault(self.vault).open_position(
        _account,
        _position_token,
        _min_position_amount_out,
        _debt_token,
        _debt_amount,
        _margin_amount,
    )

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

This means that trades can still be initiated and orders created while the contract is in defensive or winddown mode. Therefore the defensive mode could be circumvented in the case that it was required as a result of a vulnerability in the contract. 

Additionally, a "winddown" could never successfully be completed as new trades could be created.

## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L126-L202

## Tool used

Manual Review

## Recommendation
Include the following check in the `open_trade` function.

```vyper
assert self.is_accepting_new_orders, "paused"
```
