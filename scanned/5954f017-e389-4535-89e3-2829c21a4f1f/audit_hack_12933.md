# [M] Check if position is still liquidatable is not made when adding margin.

## Summary
Severity: Medium
Reporter: Yuki
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L503
Type: audit-issue

## Details
# Check if position is still liquidatable is not made when adding margin.

## Summary
Check if position is still liquidatable is not made when adding margin.

## Vulnerability Detail
Currently the function add_margin is used to reduce the leverage of a position by adding more margin to the position.
However the function forgets to check whether the position is still exceeds the maximum allowed leverage even after adding margin to the position.

This is problematic considering that the position is still eligible for liquidation, given this scenario if a user adds an amount of margin but the margin is not enough to reduce the leverage below the maximum allowed leverage. The user's position can still be liquidated, which results for the user to lose the extra margin he added to the position.

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

## Impact
By not checking if the position is still liquidatable even after adding margin to it, an user can still be liquidated resulting to him losing the extra margin of funds added to the position.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L503

## Tool used

Manual Review

## Recommendation
The function add_margin should check whether the position is still liquidatable even after adding margin to it.

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

    assert not self._is_liquidatable(_position_uid), "exceeds max leverage"

    log MarginAdded(_position_uid, _amount)
```
