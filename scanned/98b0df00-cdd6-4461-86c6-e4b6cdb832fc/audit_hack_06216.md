# [M] Funds stuck if not claimed before liquidation

## Summary
Severity: Medium
Reporter: minhtrng
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L318-L352
Type: audit-issue

## Details
# Funds stuck if not claimed before liquidation

## Summary

Funds can get stuck permanently if they arent claimed before liquidation.

## Vulnerability Detail

If WETH get withdrawn from alchemix and gets marked as claimable, every share gets assigned a a portion of it to be claimed:

```py
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

If someone liquidates his shares before claiming the WETH that he was eligible to, they will be locked in the contract forever. They could be potentially retrieved via a migration, which currently is not working though and which is not the purpose of the migration mechanism either.

A simple example: 
1. There are 100 shares and after some time 100 WETH are withdrawn from alchemix. Now every share can claim 1 WETH.
2. A user liquidates his 20 shares without claiming his fraction of WETH from step 1 first. Now there are only 80 shares, each eligible to still claim 1 WETH each. 20 WETH from the 100 above will be stuck in the contract.

## Impact

Assets getting locked in the contract.

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L318-L352

## Tool used

Manual Review

## Recommendation

When performing a liquidation, assert that the liquidator has no claimable assets. Maybe even perform the claim for them in case they have.
