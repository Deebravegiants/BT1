# [M] Order's minimum amount out is calculated wrongly when partially closing a position.

## Summary
Severity: Medium
Reporter: Yuki
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L290
Type: audit-issue

## Details
# Order's minimum amount out is calculated wrongly when partially closing a position.

## Summary
Order's minimum amount out is calculated wrongly when partially closing a position.

## Vulnerability Detail
When a user partially closes a position, the user can either set the wanted _min_amount_out by himself or apply "_min_amount_out" as zero and let the function calculate the minimum amount out itself based on the position's info.

However the function makes the mistake to calculate the minimum amount out based on the whole position amount instead of calculating it based on the amount that the user wants to reduce the position for e.g - "_reduce_by_amount".

In the end the minimum amount out calculated by the function will be never met, as the user is partially closing an amount from the position and not closing the full amount of the position. Therefore this feature leads to permanent revert.

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

    position: Position = self.positions[_position_uid]
    assert position.position_amount >= _reduce_by_amount, "_reduce_by_amount > position"

    min_amount_out: uint256 = _min_amount_out
    if min_amount_out == 0:
        # market order, add some slippage protection
        min_amount_out = self._market_order_min_amount_out(
            position.position_token, position.debt_token, position.position_amount
        )

    debt_amount: uint256 = self._debt(_position_uid)
    margin_debt_ratio: uint256 = position.margin_amount * PRECISION / debt_amount

    amount_out_received: uint256 = self._swap(
        position.position_token, position.debt_token, _reduce_by_amount, min_amount_out
    )

    # reduce margin and debt, keep leverage as before
    reduce_margin_by_amount: uint256 = (
        amount_out_received * margin_debt_ratio / PRECISION
    )
    reduce_debt_by_amount: uint256 = amount_out_received - reduce_margin_by_amount

    position.margin_amount -= reduce_margin_by_amount

    burnt_debt_shares: uint256 = self._repay(position.debt_token, reduce_debt_by_amount)
    position.debt_shares -= burnt_debt_shares
    position.position_amount -= _reduce_by_amount

    self.positions[_position_uid] = position

    log PositionReduced(position.account, _position_uid, position, amount_out_received)

    return amount_out_received
```

## Impact
Duo to the logic error, the minimum amount calculated by the function will be incorrect which leads to the permanent revert of this feature.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L290

## Tool used

Manual Review

## Recommendation
As the function reduce_position is used to partially close a position, the min amount out should be calculated based on the user's _reduce_by_amount and not the whole position amount. As this problem leads to the incorrect calculation of the minimum amount out.

```vy
    min_amount_out: uint256 = _min_amount_out
    if min_amount_out == 0:
        # market order, add some slippage protection
        min_amount_out = self._market_order_min_amount_out(
            position.position_token, position.debt_token, _reduce_by_amount
        )

```
