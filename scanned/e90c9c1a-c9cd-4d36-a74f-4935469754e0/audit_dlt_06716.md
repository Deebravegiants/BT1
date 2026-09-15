# [M] DOS of `removeSupportedAsset()` function

## Summary
Severity: Medium
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-16
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/23
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** --
  **HATS Profile:** ---

  **Beneficiary:** 0x3828b7Dff72E340B44f3A0270574dDE9276D5FD3
  **Submission hash (on-chain):** 0xe14f1ad8ea4a5227bde1634b1e99538bf5395dbbfb05c4988e48a72072bb67ab
  **Severity:** medium
  
  **Description:**
  The removeSupportedAsset() function in DStakeCollateralVault contract can be avoided by malcious user by just sending 1 wei of vaultAsset to the DStakeCollateralVault contract.

```solidity
function removeSupportedAsset(
        address vaultAsset
    ) external onlyRole(ROUTER_ROLE) {
        if (!_isSupported(vaultAsset)) revert AssetNotSupported(vaultAsset);
        if (IERC20(vaultAsset).balanceOf(address(this)) > 0) {
            revert NonZeroBalance(vaultAsset);
        }

        _supportedAssets.remove(vaultAsset);
        emit SupportedAssetRemoved(vaultAsset);
    }
```
as we can see the above check going to revert if balance of vaultAsset is greater than zero. so it can be abused by just directly sending 1 wei of vaultAsset token to this contract.
## Impact
DOS of removeSupportedAsset() function

## Recommendation
Consider using internal balance system to avoid this issue.
