# [M] If there is no incentive for liquidation, the liquidator bot will not deal with it

## Summary
Severity: Medium
Reporter: kutugu
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L368-L373
Type: audit-issue

## Details
# If there is no incentive for liquidation, the liquidator bot will not deal with it

## Summary

When `amount_out_received > debt_amount`, there is no incentive for liquidation, the liquidator bot will not deal with it, resulting in continuous loss of user funds.

## Vulnerability Detail

```vyper
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

When the position token price falls, the leverage ratio rises and the liquidation process is triggered after the max_leverage is reached.
The liquidation is generally monitored by the off-chain robot in real time, and ordinary users rarely handle the liquidation themselves, which is generally an incentive to discount the robot during the liquidation.
In this protocol, the liquidation will penalize the user and the penalty will add value to the share. But the incentive is only exist when `amount_out_received > debt_amount`.
That means, when the user's position token is sold and becomes insolvent, the user will not be punished, which will cause the liquidation robot to deal with the liquidation inactively when it detects no income, and the user's position will continue to exist. 
As the position token price continues to fall, the user's funds will continue to lose and cannot be stopped.

## Impact

When incentives do not exist, the liquidator will basically not handle the liquidation process, resulting in further user losses.

## Code Snippet

- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L368-L373

## Tool used

Manual Review

## Recommendation

What is the need to penalize users and incentivize liquidators in any case.
