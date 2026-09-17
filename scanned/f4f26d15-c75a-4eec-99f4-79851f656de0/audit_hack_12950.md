# [H] Calculation in `is_liquidable is bricked` and user will be wrongly lqiuidated for max leverage.

## Summary
Severity: High
Reporter: BugBusters
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L346-L375
Type: audit-issue

## Details
# Calculation in `is_liquidable is bricked` and user will be wrongly lqiuidated for max leverage.

## Summary
Calculation in `is_liquidable is bricked` and user will be wrongly lqiuidated for max leverage.
## Vulnerability Detail
`is_liquitable` function checks the effective leverage and if the effective leverage is grater than max leverage, user can be liquidated.

But the problem is if the user is operating on max leverage, a slight change in price make the user liquitable even if there is alot of margin availible.

The mechanism of liquidation in traditional finance operates different than that, a user is Liquadated only if the margin in account is less than the required margin, not if price movement change the leverage.

Consider the following scenerio.

1. Alice longed btc at 10K with max leverage available that is 10.
2. And margin of alice is also 10K.
3. So to liquidate the alice in true scenerio, price of bitcoin should move down by 10% to 9K and alice will be liquidated.
4. But in current scnerio even if the price of bitcoin moves to 9.5K the margin will easily cross the maximum leverage and now alice can be liquidated which is unfair and wrong.

```solidity
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
## Impact
User is wrongly liquidated.
## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L346-L375
## Tool used

Manual Review

## Recommendation
Liquidate based upon the margin being used and availible not the max leverage that is calculated based upon the changing price.
