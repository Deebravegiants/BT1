# [H] Position owners can DoS the liquidation feature by adding margin

## Summary
Severity: High
Reporter: whiteh4t9527
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L372
Type: audit-issue

## Details
# Position owners can DoS the liquidation feature by adding margin

## Summary
`Vault.liquidate()` has a flawed penalty computation logic such that a the owner of a *liquidatable* position could prevent the position from being liquidated by making the penalty computation code being reverted.

## Vulnerability Detail
If the position owner intentionally makes `self.margin[position.account][position.debt_token]` less than `penalty`, [this line of code](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L372) in `Vault.liquidate()` would always revert. This could be done by `Vault.add_margin()` which moves fund from `self.margin[position.account][position.debt_token]` to a position margin.

## Impact
Liquidation won't happen

## Code Snippet
```vyper
def add_margin(_position_uid: bytes32, _amount: uint256):
    """
    @notice
        Allows to add additional margin to a Position and 
        reduce the leverage.
    """
    assert self.is_whitelisted_dex[msg.sender], "unauthorized"

    position: Position = self.positions[_position_uid]

    assert (self.margin[position.account][position.debt_token] >= _amount), "not enough margin"

    self.margin[position.account][position.debt_token] -= _amount
    position.margin_amount += _amount

    self.positions[_position_uid] = position
    log MarginAdded(_position_uid, _amount)
```

```vyper
def liquidate(_position_uid: bytes32):
    """
    @notice
        Liquidates a position that exceeds the maximum allowed
        leverage for that market.
        Charges the account a liquidation penalty.
    """
    assert self.is_whitelisted_dex[msg.sender], "unauthorized"
    assert self._is_liquidatable(_position_uid), "position not liquidateable"

    position: Position = self.positions[_position_uid]
    debt_amount: uint256 = self._debt(_position_uid)

    min_amount_out: uint256 = self._market_order_min_amount_out(
        position.position_token, position.debt_token, position.position_amount
    )

    amount_out_received: uint256 = self._close_position(_position_uid, min_amount_out)

    # penalize account
    penalty: uint256 = debt_amount * self.liquidation_penalty / PERCENTAGE_BASE

    if amount_out_received > debt_amount:
        # margin left
        remaining_margin: uint256 = amount_out_received - debt_amount
        penalty = min(penalty, remaining_margin)
        self.margin[position.account][position.debt_token] -= penalty //@audit always revert
        self._distribute_trading_fee(position.debt_token, penalty)

    log PositionLiquidated(position.account, _position_uid, position)
```

## Tool used

Manual Review

## Recommendation
Let the penalty be the smaller value of `penalty` and `self.margin[position.account][position.debt_token])`.
