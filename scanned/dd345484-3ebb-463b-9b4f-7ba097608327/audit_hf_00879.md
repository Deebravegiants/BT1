# [M] Wrong slippage check in LSPRouter::

## Summary
Severity: Medium
Contest weight: 0.5825
Dataset id: 2635
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Usually, slippage related to ERC4626 vaults is either ensuring that users does not get less amount of assets when redeeming or does not burn more shares when withdrawing. In the LSPRouter::withdraw() implementation user can only provide minSharesWithdrawn which is not protects him from burning more shares than expected. The opposite check in redeem() is The following snippet is part of LSPRouter::withdraw():
```solidity
shares = lsp.withdraw(params.assets, arr.receiver, msg.sender);
require(shares >= params.minSharesWithdrawn, "LSPRouter: assetsWithdrawn < minAssetsWithdrawn");
```
ckend/src/periphery/LSPRouter.sol#L249 Another thing we have to take into consideration is the share:assets ratio in LSP. Usually, it should always be rising as more and more liquidations happen in LSP accrue funds from those liquidations. But there is a scenario in which the debt to offset from LSP is higher than the collateral to add leading to a decreasing ratio leading to more burned shares for the same amount. In LiquidStabilityPool: // Unlikely case in which LM offsets more debt value than collateral uint collSurplusAmount; if (_collToAdd > debtInCollateralAmount) { collSurplusAmount = _collToAdd - debtInCollateralAmount; } Apart from the potential ratio decrease, we have to take into consideration the prices of the underlying collateral (LSP consists of NECT + other priceable assets). A price change before the user transaction will affect the number of shares burned as well. Internal Pre-conditions N/A External Pre-conditions N/A Attack Path Users do not have a way to protect themselves from unexpected slippage. Loss of funds for users. N/A

## Recommendation
Consider changing the check to:
```solidity
require(shares <= params.maxSharesWithdrawn, "LSPRouter: assetsWithdrawn < minAssetsWithdrawn");
```
and the corresponding parameter.
