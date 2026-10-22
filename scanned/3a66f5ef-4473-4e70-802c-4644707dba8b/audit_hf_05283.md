# [M] MetaVault::redeemRequiredBaseAssets

## Summary
Severity: Medium
Contest weight: 0.0000
Dataset id: 23524
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: MetaVault::redeemRequiredBaseAssets is supposed to iterate through the supported vaults, re‑deeming assets until the required amount of base assets is obtained:
```solidity
/// @notice Iterates through supported vaults and redeems assets until the required amount of base
/// tokens is obtained,!
function redeemRequiredBaseAssets (uint baseTokens) internal {
    for (uint i = 0; i < assetsArr.length; i++) {
        IERC4626 vault = IERC4626(assetsArr[i].asset);
        uint totalBaseTokens = vault.previewRedeem(vault.balanceOf(address(this)));
        // @audit only withdraw if a single withdraw can satisfy desired amount
        if (totalBaseTokens >= baseTokens) {
            vault.withdraw(baseTokens, address(this), address(this));
            break;
        }
    }
}
```
Impact: This has a number of potential problems:
1) if no single withdraw can satisfy the desired amount, then the calling function will revert due to insufficient funds even if the desired amount could be satisfied by multiple smaller withdrawals from different supported vaults  
2) a single withdraw may be greater than the desired amount, leaving USDe tokens inside the vault contract. This is suboptimal as then they would not be earning yield by being staked in sUSDe, and there appears to be no way for the contract owner to trigger the staking once the yield phase has started, since supporting vaults can be added and deposits for them work during the yield phase

## Recommendation
Recommended Mitigation: MetaVault::redeemRequiredBaseAssets should:
- keep track of the total currently redeemed amount  
- calculate the remaining requested amount as the requested amount minus the total currently redeemed amount  
- if the current vault is not able to redeem the remaining requested amount, redeem as much as possible and increase the total currently redeemed amount by the amount redeemed  
- if the current vault could redeem more than the remaining requested amount, redeem only enough to satisfy the remaining requested amount  

The above strategy ensures that:
- small amounts from multiple vaults can be used to fulfill the requested amount  
- greater amounts than requested are not withdrawn, so no USDe tokens remain inside the vault unable to be staked and not earning yield
