# [M] Incorrect rounding in _convertToShares for withdrawal-based actions leads to 1 dead share for users

## Summary
Severity: Medium
Contest weight: 0.4696
Dataset id: 6022
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _convertToShares function currently does floor rounding in all cases. This works correctly for any deposit actions. In the case of withdrawals, it ends up rounding down the shares needed to withdraw for a set amount of equity. Thereby, this leads to instances where if users attempt to withdraw all equity they have that requires more than 1 share, such as in the case of 50 shares representing the user's entire equity, they will have 1 share remaining. The final effect is different depending on a combination of decimal and price differential between the associated collateral and debt tokens for a Leveraged Token.  
In the ETH2x Long case, the collateral asset is ETH represented with 18 decimals, while the debt asset is USDC represented with 6. If there's a lone user in the LT and withdraws all their equity, they will succeed in withdrawing it and repaying all debt. Following this, all equity is withdrawn, but the user will remain with 1 dead share. Even if more equity enters, this dead share is unusable in this case, and can't be withdrawn.  
In the ETH2x Short case, the collateral is USDC and ETH is the debt. Since ETH as the debt has more precision, it leads to a case where requesting all equity, results in 1 leftover share, with fractional equity and debt being represented in that share. A secondary withdrawal action is required with 1 share to completely remove a user's position. This case doesn't lead to dead shares, but requires 2 withdrawal actions.  
Other than the dead share that can't be withdrawn or leftover share requiring 2 withdrawals, the effect this can have on Leveraged Tokens in the first case is an artificial overinflation of the total supply (as these shares will permanently keep it increased even though there's no equity backing it) that can't be removed. This results in an increased dilution to current Leveraged Token holders proportional to the amount of unique accounts that have attempted a complete withdrawal and have 1 dead share remaining, to the benefit of future deposits. This effect should generally not be significant enough in non-inflation attacked tokens, however, this effect can be greatly amplified if a token has been inflated.

## Recommendation
```solidity
function _convertToShares(ILeverageToken token, uint256 equityInCollateralAsset, ExternalAction action)
internal
view
returns (uint256 shares)
{
    ILendingAdapter lendingAdapter = getLeverageTokenLendingAdapter(token);
    return Math.mulDiv(
        equityInCollateralAsset,
        token.totalSupply() + 10 ** DECIMALS_OFFSET,
        lendingAdapter.getEquityInCollateralAsset() + 1,
        action == ExternalAction.Deposit ? Math.Rounding.Floor : Math.Rounding.Ceil
    );
}
```
an appropriately updating all relevant calls with the action in context being passed.
