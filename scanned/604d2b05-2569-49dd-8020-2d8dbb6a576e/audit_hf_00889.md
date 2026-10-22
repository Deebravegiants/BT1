# [M] InfraredCollateralVault is incompatible

## Summary
Severity: Medium
Contest weight: 0.5930
Dataset id: 2645
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
InfraredCollateralVault always scales the totalAssets() result up to 18 decimals. I believe this is fixing the problem with totalAssets() accounting, it introduces another problem when doing shares conversion.
InfraredCollateralVault overrides the ERC4626 totalAssets() implementation to include reward tokens value and scale the result to 18 decimals. This makes huge inconsistency between the first minted shares and all subsequently minted shares.
Taking a look into the _convertToShares() method of inherited OZ ERC4626 implementation:
```solidity
function _convertToShares(uint256 assets, Math.Rounding rounding) internal view virtual returns (uint256) {
    return assets.mulDiv(totalSupply() + 10 ** _decimalsOffset(), totalAssets() + 1, rounding);
}
```
and we have for _decimalsOffset():
```solidity
function _decimalsOffset() internal view override virtual returns (uint8) {
    return 18 - assetDecimals();
}
```
Initially, totalAssets() and totalSupply() would be 0 as no assets have been deposited and donation is not possible. So, lets say that the first depositor want to add 100e6 (asset is with 6 decimals, decimalsOffset is 12) of the underlying assets, which would result in (100e6 * (0+1e12))/1 = 100e18 shares. This minting is correct and shares are correctly scaled up to 18 decimals because of the decimalsOffset.
Next depositor also want to deposit 100e6 assets. Going through the formula for shares but totalAssets() return is scaled to 18 decimals. Shares for the second mint are ~ 10000e24/100e18 = 100e6 which is significantly lower than the initially minted 100e18 shares.
lob/main/blockend/src/core/vaults/InfraredCollateralVault.sol#L134C1-L159C6
Internal Pre-conditions
Vault asset with < 18 decimals
External Pre-conditions
N/A
Attack Path
After initial mint, all subsequent minting will result in significantly lower amount of shares for the same amount of deposit (1e12 times lower for 6 decimals asset). Taking the example from the Root Cause section - second depositor would be able to claim 100e6/(100e18 + 100e6) of 200e6 (actual deposited balance) which is 0.
This bricks the whole vault as all depositors except the first one would lose their funds. There are or normal user. In both cases the issue persists and the vault cant function normally.

## Recommendation
Consider adjusting the asset amount to 18 decimals when doing shares/asset conversion.
