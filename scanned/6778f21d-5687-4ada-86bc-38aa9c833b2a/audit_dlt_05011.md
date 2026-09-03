# [M] totalAsset() can be manipulated in Junior Vault and Senior Vault.sol, affecting minted share.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-rage-trade
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/58
Type: sherlock-finding

## Details
ctf_sec

medium

# totalAsset() can be manipulated in Junior Vault and Senior Vault.sol, affecting minted share.

## Summary

totalAsset() can be manipulated in Junior Vault and Senior Vault.sol, affecting share value.

## Vulnerability Detail

The DnGmxSeniorVault.sol totalAsset() function is implemented below:

```solidity
    /// @notice derive total assets managed by senior vault
    /// @return amount total usdc under management
    function totalAssets() public view override(IERC4626, ERC4626Upgradeable) returns (uint256 amount) {
        amount = aUsdc.balanceOf(address(this));
        amount += totalUsdcBorrowed();
    }
```

If the user send aUSDC balance directly to the senior vault address, the totalAssets() value is inflated.

In ERC4626 implementation, if the totalAssets() is inflated, the convertToShares can be rounded to low value.

```solidity
    function convertToShares(uint256 assets) public view virtual returns (uint256) {
        uint256 supply = totalSupply(); // Saves an extra SLOAD if totalSupply is non-zero.

        return supply == 0 ? assets : assets.mulDivDown(supply, totalAssets());
    }
```

and convertToAssets's value goes up, means that the shares value goes up.

```solidity
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-rage-trade-judging/issues/58_
