# [H] Stuck funds in the vault duo to wrong logic applied when adding margin to a position.

## Summary
Severity: High
Reporter: Yuki
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L233
Type: audit-issue

## Details
# Stuck funds in the vault duo to wrong logic applied when adding margin to a position.

## Summary
Stuck funds in the vault duo to wrong logic applied when adding margin to a position. 

## Vulnerability Detail
The function add_margin is used by user to reduce the leverage of the position, by adding margin to it. 

By using the function, the position's margin amount is updated with the new amount added, so that the position's leverage doesn't exceed the max leverage allowed and the function isn't eligible for liquidation. 

Once added this margin can't be removed from the position if it gets the position back in liquidation state.

```vy
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
```vy
@external
def remove_margin(_position_uid: bytes32, _amount: uint256):
    """
    @notice
        Allows to remove margin from a Position and 
        increase the leverage.
    """
    assert self.is_whitelisted_dex[msg.sender], "unauthorized"

    position: Position = self.positions[_position_uid]

    assert position.margin_amount >= _amount, "not enough margin"

    position.margin_amount -= _amount
    self.margin[position.account][position.debt_token] += _amount

    assert not self._is_liquidatable(_position_uid), "exceeds max leverage"
    
    self.positions[_position_uid] = position
    log MarginRemoved(_position_uid, _amount)
```

The only choice would be to close or partially close the position.

But if we look over the function we can see that the margin amount isn't accounted anywhere.

Fully closing the position: Even tho margin was added the position_amount stays the same, so the function doesn't count it and still process the closing with the old values. At the end the extra margin added is being deleted with the position, which means that the funds are stuck in the contract.

Partially closing the position: On the other hand partially closing counts the margin amount and calculates the debt ratio based on the new amount of margin, but still do the closing based on the old leverage before the extra margin was added. Which leads to the same stuck funds in the contract as fully closing the position.

The conclusion is that adding margin to the position can reduce the leverage of the position, so the position is not eligible for liquidation, but closing the position is still based on the old leverage before the extra margin was added to the position. In the end when closing the positions, these extra funds added to the position are not included anywhere   and are stuck in the contract.

```vy
@internal
def _close_position(_position_uid: bytes32, _min_amount_out: uint256) -> uint256:
    """
    @notice
        Closes an existing position, repays the debt plus
        accrued interest and credits/debits the users margin
        with the remaining PnL.
    """
    # fetch the position from the positions-dict by uid
    position: Position = self.positions[_position_uid]

    # assign to local variable to make it editable
    min_amount_out: uint256 = _min_amount_out
    if min_amount_out == 0:
        # market order, add some slippage protection
        min_amount_out = self._market_order_min_amount_out(
            position.position_token, position.debt_token, position.position_amount
        )

    position_debt_amount: uint256 = self._debt(_position_uid)
    amount_out_received: uint256 = self._swap(
        position.position_token,
        position.debt_token,
        position.position_amount,
        min_amount_out,
    )

    if amount_out_received >= position_debt_amount:
        # all good, LPs are paid back, remainder goes back to trader
        trader_pnl: uint256 = amount_out_received - position_debt_amount
        self.margin[position.account][position.debt_token] += trader_pnl
        self._repay(position.debt_token, position_debt_amount)
    else:
        # edge case: bad debt
        self.is_accepting_new_orders = False  # put protocol in defensive mode
        bad_debt: uint256 = position_debt_amount - amount_out_received
        self.bad_debt[position.debt_token] += bad_debt
        self._repay(
            position.debt_token, amount_out_received
        )  # repay LPs as much as possible
        log BadDebt(position.debt_token, bad_debt, position.uid)

    # cleanup position
    self.positions[_position_uid] = empty(Position)

    log PositionClosed(position.account, position.uid, position, amount_out_received)

    return amount_out_received
```

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
Duo to the wrong logic applied, this issue leads to permanent loss of funds as the funds are stuck in the vault.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L233

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L290

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L503

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L528

## Tool used

Manual Review

## Recommendation
Adding margin should not only update the position's margin but update whole position amount by doing a swap with the extra margin provided.

```vy
@external
def add_margin(_position_uid: bytes32, _amount: uint256, _min_position_amount_out: uint256):
    """
    @notice
        Allows to add additional margin to a Position and 
        reduce the leverage.
    """
    assert self.is_whitelisted_dex[msg.sender], "unauthorized"

    position: Position = self.positions[_position_uid]

    assert (self.margin[position.account][position.debt_token] >= _amount), "not enough margin"

    self.margin[position.account][position.debt_token] -= _amount

    amount_bought: uint256 = self._swap(
        _debt_token, _position_token, _amount, _min_position_amount_out
    )

    position.margin_amount += _amount
    position.position_amount += _amount

    fee: uint256 = _amount * self.trade_open_fee / PERCENTAGE_BASE
    assert self.margin[_account][_debt_token] >= fee, "not enough margin for fee"
    self.margin[_account][_debt_token] -= fee
    self._distribute_trading_fee(_debt_token, fee)

    self.positions[_position_uid] = position
    log MarginAdded(_position_uid, _amount)
```
