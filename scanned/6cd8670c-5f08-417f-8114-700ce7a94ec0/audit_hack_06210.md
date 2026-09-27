# [H] User can liquidate before claiming their share of pending WETH tokens

## Summary
Severity: High
Reporter: Ruhum
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L394
Type: audit-issue

## Details
# User can liquidate before claiming their share of pending WETH tokens

## Summary
A user can liquidate their position before they've claimed their share of the pending WETH. After the liquidation those funds won't be claimable and will be stuck in the Vault contract

## Vulnerability Detail
When shares are burned through `withdraw_underlying_to_claim()`, every share owner gets their share of the WETH that was withdrawn. They have to claim it by calling the `claim()` function. But, if a position was liquidated, those shares won't be claimable anymore. Thus, it's important that the owner of the position first claims the pending WETH and *then* liquidates the position. The contract doesn't handle that for the user.

The likelihood of a user forgetting to claim their share is pretty high.

## Impact
Unclaimed WETH will be stuck in the contract forever.

## Code Snippet
When shares are burned to withdraw WETH, it's awarded to share holders proportionally: 
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L394
```python
@external
def withdraw_underlying_to_claim(_amount_shares: uint256, _min_weth_out: uint256):
    """
    @notice
        Withdraws _amount_shares and _min_weth_out from Alchemix to be distributed
        to token holders.
        The WETH is held in this contract until it is `claim`ed.
    """
    amount_withdrawn: uint256 = self._withdraw_underlying_from_alchemix(_amount_shares, self, _min_weth_out)
    self._mark_as_claimable(amount_withdrawn)

    log Claimable(amount_withdrawn)
```

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L407-L420:
```python
@internal
def _mark_as_claimable(_amount: uint256):
    """
    @notice
        Marks _amount of WETH as claimable by token holders and
        calculates the amount_claimable_per_share.
    """
    if _amount == 0 or self.total_shares == 0:
        return

    assert ERC20(WETH).balanceOf(self) >= _amount

    self.amount_claimable_per_share += _amount * PRECISION / self.total_shares
```

After the position was liquidated, `_claimable_for_token()` will return `0`. The previously awarded WETH won't be claimable anymore.
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L428-L440
```python
@external
def claim(_token_id: uint256) -> uint256:
    """
    @notice
        Allows a token holder to claim his share of pending WETH.
    """
    token_owner: address = ERC721(NFT).ownerOf(_token_id)
    assert msg.sender == token_owner, "only token owner can claim"

    amount: uint256 = self._claimable_for_token(_token_id)
    assert amount > 0, "nothing to claim"

    position: Position = self.positions[_token_id]
    position.amount_claimed += amount
    self.positions[_token_id] = position
    
    ERC20(WETH).transfer(token_owner, amount)

    log Claimed(_token_id, token_owner, amount)
    return amount

@view
@internal
def _claimable_for_token(_token_id: uint256) -> uint256:
    """
    @notice
        Calculates the pending WETH for a given token_id.
    """
    position: Position = self.positions[_token_id]
    if position.is_liquidated:
        return 0
    
    total_claimable_for_position: uint256 = position.shares_owned * self.amount_claimable_per_share / PRECISION
    return total_claimable_for_position - position.amount_claimed
```

In `liquidate()` the contract doesn't check whether the user has already claimed their share: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L318-L352
```python
@nonreentrant("lock")
@external
def liquidate(_token_id: uint256, _min_weth_out: uint256) -> uint256:
    """
    @notice
        Liquidates the underlying debt of position[_token_id] by burning
        a corresponding amount of shares.
        Withdraws remaining value of shares as WETH to token_owner.
        Reverts if owner would receive less than _min_weth_out.
    """
    token_owner: address = ERC721(NFT).ownerOf(_token_id)
    assert token_owner == msg.sender, "only token owner can liquidate"

    position: Position = self.positions[_token_id]
    assert position.is_liquidated == False, "position already liquidated"
    
    position.is_liquidated = True
    self.positions[_token_id] = position
    self.total_shares -= position.shares_owned

    collateralisation: uint256 = self._latest_collateralisation()
    shares_to_liquidate: uint256 = position.shares_owned * DECIMALS / collateralisation

    amount_shares_liquidated: uint256 = IAlchemist(self.alchemist).liquidate(
        ALCX_YVWETH,                 # _yield_token: address,
        shares_to_liquidate,         # _shares: uint256,
        1                            # _min_amount_out: uint256 -> covered by _min_weth_out
    )

    amount_to_withdraw: uint256 = position.shares_owned - amount_shares_liquidated
    # _withdraw_underlying_from_alchemix reverts on < _min_weth_out
    amount_withdrawn: uint256 = self._withdraw_underlying_from_alchemix(amount_to_withdraw, token_owner, _min_weth_out)

    log Liquidated(_token_id, token_owner, amount_withdrawn)
    return amount_withdrawn

```
## Tool used

Manual Review

## Recommendation
In `liquidate()`, call `_claimable_for_token()` to check whether the caller still has any unclaimed WETH. If that's the case, claim those tokens and then proceed with the liquidation.
