# [H] User can be liquidated while fund_account is paused

## Summary
Severity: High
Reporter: BugBusters
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L659-L668
Type: audit-issue

## Details
# User can be liquidated while fund_account is paused

## Summary
User can be unfairly liquidated while adding margin is paused.
## Vulnerability Detail
The function `fund_account` or `fund_account_eth` can be paused while the function `liquidate` can never be paused which means user can be unfailry liquidated when adding margin to position is paused since account cannot be funded, which could have saved the user position from liquidating, but in pause scenario user will be liquidated.

```solidity
def fund_account(_token: address, _amount: uint256):
    """
    @notice
        Allows a user to fund his _token margin.
    """
    assert self.is_accepting_new_orders, "funding paused"
    assert self.is_whitelisted_token[_token], "token not whitelisted"
    self.margin[msg.sender][_token] += _amount
    self._safe_transfer_from(_token, msg.sender, self, _amount)
    log AccountFunded(msg.sender, _amount, _token)
```

```solidity
@external
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

So for above code snippets following scenerio can play out:

1. User opens a position with the intended leverage.
2. User is about to liquidate and want to fund account, add margin and save position.
3. Protocol is paused.
4. User can't fund and add margin and is liquidated unfairly.


## Impact
User is unfailry liqudiated.
## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L659-L668
https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L346-L375


For more reference read the following:

https://dacian.me/defi-slippage-attacks
## Tool used

Manual Review

## Recommendation
Pause the liquidation mechanism too when funding is paused.
