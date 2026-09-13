# [M] A position exceeding the max leverage should only be fully closed through liquidation.

## Summary
Severity: Medium
Reporter: Yuki
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L233
Type: audit-issue

## Details
# A position exceeding the max leverage should only be fully closed through liquidation.

## Summary
A position exceeding the max leverage should only be fully closed through liquidation.

## Vulnerability Detail
When position's values exceed the maximum allowed leverage in the market, the position is available for liquidation.

```vy
@view
@internal
def _is_liquidatable(_position_uid: bytes32) -> bool:
    """
    @notice
        Checks if a position exceeds the maximum leverage
        allowed for that market.
    """
    position: Position = self.positions[_position_uid]
    leverage: uint256 = self._effective_leverage(_position_uid)
    return leverage > self.max_leverage[position.debt_token][position.position_token]
```

Prior to liquidating a position exceeding the maximum leverage, the owner of the position is charged a liquidation penalty incase the amount out received is bigger than the debt accrued.

```vy
@nonreentrant("lock")
@external
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
        self.margin[position.account][position.debt_token] -= penalty
        self._distribute_trading_fee(position.debt_token, penalty)

    log PositionLiquidated(position.account, _position_uid, position)

```

Currently when a position is eligible for liquidation, the owner is restricted from partially reducing the position's amount but the same restriction is not applied when closing the whole position with the function "def close_position".

When liquidating the position a penalty is issued duo to the owner of the position exceeding the maximum leverage allowed, this penalty shouldn't by bypassed by the owner closing the position himself. Therefore when a position is liquidatable, the only way for the position to be fully closed should be through liquidation.

```vy
@nonreentrant("lock")
@external
def reduce_position(
    _position_uid: bytes32, _reduce_by_amount: uint256, _min_amount_out: uint256
) -> uint256:
    """
    @notice
        Partially closes an existing position, by selling some of the 
        underlying position_token.
        Reduces both debt and margin in the position, leverage 
        remains as is.
    """
    assert self.is_whitelisted_dex[msg.sender], "unauthorized"
    assert not self._is_liquidatable(_position_uid), "in liquidation"
```

## Impact
The owner of a position exceeding the maximum allowed leverage can bypass the liquidation penalty by closing the position himself.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L233

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L346

## Tool used

Manual Review

## Recommendation
A position exceeding the maximum leverage allowed should be closed only through the function liquidate.

```vy
@nonreentrant("lock")
@external
def close_position(_position_uid: bytes32, _min_amount_out: uint256) -> uint256:
    assert not self._is_liquidatable(_position_uid), "position liquidateable"
    assert self.is_whitelisted_dex[msg.sender], "unauthorized"
    return self._close_position(_position_uid, _min_amount_out)
```
