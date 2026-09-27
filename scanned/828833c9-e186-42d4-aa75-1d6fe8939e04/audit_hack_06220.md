# [M] Liquidation may fail due to insufficient share

## Summary
Severity: Medium
Reporter: Bauer
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L393-L404
Type: audit-issue

## Details
# Liquidation may fail due to insufficient share

## Summary
When call function ```withdraw_underlying_to_claim()```  to withdraw WETH from Alchemix to be distributed ,the reduced share is not updated on the variable ```total_shares``` resulting in liquidating debt fail.
## Vulnerability Detail
```vyper
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
The function ```liquidate()``` allows the owner of NFT to liquidate the underlying debt of position[_token_id] by burning a corresponding amount of shares.
The function ```withdraw_underlying_to_claim()``` is used to withdraw WETH from Alchemix to be distributed.It will burn shares to get WETH. However ,the reduced share is not updated on the variable ```total_shares```. The value of the variable ```total_shares```  is more than the share recorded in the alchemist protocol.If a large number of users liquidate their assets, there may not be enough share to burn, causing the transaction to fail

## Impact
If a large number of users liquidate their assets, there may not be enough share to burn, causing the transaction to fail

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L393-L404
## Tool used

Manual Review

## Recommendation
