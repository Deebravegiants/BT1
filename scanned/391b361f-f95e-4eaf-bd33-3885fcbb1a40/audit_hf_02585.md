# [H] Increasing self.totalAssets before share calculation in NativeVault._increaseBalance() mints less shares

## Summary
Severity: High
Contest weight: 0.7483
Dataset id: 13956
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In NativeVault._increaseBalance(), self.totalAssets is increased by assets before calculating the amount of shares to mint to the receiver:
```solidity
self.totalAssets += assets;
uint256 shares = convertToShares(assets);
_mint(_of, shares);
```
However, increasing self.totalAssets first causes convertToShares() to calculate less shares to be minted than expected, since totalAssets() is increased beforehand.
A naive example:
• Assume the following:
– self.totalAssets = 100e18
– totalSupply = 100e18
• _increaseBalance() is called with assets = 100e18:
– self.totalAssets = 100e18 + 100e18 = 200e18
• convertToShares() calculates shares as 50e18 as:
assets * (totalSupply + 1) / (totalAssets + 1) = 100e18 * (100e18 + 1) / (200e18 + 1) = 50e18
• However, 50e18 shares is only worth roughly 66.6e18 of assets as:
shares * (totalAssets + 1) / (totalSupply + 1) = 50e18 * (200e18 + 1) / (150e18 + 1) = ~66.6e18
In the example above, the user loses around 33.3e18 assets.

## Recommendation
The correct order of operator would be to increase self.totalAssets after calling convertToShares():
```solidity
- self.totalAssets += assets;
uint256 shares = convertToShares(assets);
_mint(_of, shares);
+ self.totalAssets += assets;
```
