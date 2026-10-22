# [M] It is possible for `_calculate_mintable_amount` to revert

## Summary
Severity: Medium
Reporter: tsvetanovv
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L243
Type: audit-issue

## Details
# It is possible for `_calculate_mintable_amount` to revert

## Summary
In `Vault.vy._calculate_mintable_amount()`, the mintable amount is calculated. This function do not check if the value of  `_amount_shares` is 0. If that is the case, the call will revert due to the division by zero error.

## Vulnerability Detail
See summary

## Impact

```vyper
@internal
@view
def _calculate_mintable_amount(_amount_shares: uint256) -> uint256:
    """
    @notice
        Calculate the mintable amount of debt tokens given _amount_shares new
        shares as collateral.
        This function does not account for existing debts on Alchemix.
    """
    min_collateralization: uint256 = IAlchemist(self.alchemist).minimumCollateralization()
    amount_shares_collateralized: uint256 = _amount_shares * DECIMALS / min_collateralization
    amount_underlying: uint256 = IAlchemist(self.alchemist).convertSharesToUnderlyingTokens(ALCX_YVWETH, amount_shares_collateralized)
    mintable_debt: uint256 = IAlchemist(self.alchemist).normalizeUnderlyingTokensToDebt(WETH, amount_underlying)
    if mintable_debt > 0:
        mintable_debt -= 1 # to pass "<" collateralisation check on Alchemix
    return mintable_debt
```

## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L243

## Tool used

Manual Review

## Recommendation
Check `_amount_shares` is not zero, because we will get division by zero error. Consider adding a assert statement in the functions to ensure `_amount_shares` > 0.
