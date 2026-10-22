# [M] [M] Liquidation increases collateralization and provides withdrawable amount for claim, NOT withdraw in time leads to improper allocation

## Summary
Severity: Medium
Reporter: oxcm
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L318-L353
Type: audit-issue

## Details
# [M] Liquidation increases collateralization and provides withdrawable amount for claim, NOT withdraw in time leads to improper allocation

## Summary

When a position is liquidated, the value of the position is realized and can be withdrawn by `withdraw_underlying_to_claim`. However, the contract does not automatically trigger `withdraw_underlying_to_claim` on liquidation. 

## Vulnerability Detail

### POC

Given:

* collateralization ratio = 200%

1. The system has a  with a total value of 100 ETH and a debt of 50 alETH.

2. A position with a value of 10 ETH is liquidated, and half of the share (5 ETH) are used to repay 5 alETH of debt.

3. The total value of the system is now `95 ETH`, which is sufficient to maintain a 200% collateralization ratio, as at least `90 ETH` worth of collateral is required.

4. The maximum amount of ETH that can be withdrawn is 5 ETH, which is the value of the collateral that was used to maintain the 200% collateralization ratio after the liquidation.

The key takeaway is that the liquidation of a position immediately increases the amount that can be withdrawn, and if not withdrawn before new shares are issued, this "profit" will be shared by new shareholders. It is recommended to withdraw all available funds by calling `withdraw_underlying_to_claim` before the liquidation is complete.

## Impact

In the case of overcollateralized positions, liquidating a position immediately increases the amount that can be withdrawn using `withdraw_underlying_to_claim`. If these funds are not immediately withdrawn, savvy users can take advantage of the increased amount by depositing new shares.

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L318-L353

```vyper=318
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

Manual Review / ChatGPT PLUS

## Recommendation

Call `withdraw_underlying_to_claim` Withdrawn new withdrawable share, immediately at end of `liquidate`.
