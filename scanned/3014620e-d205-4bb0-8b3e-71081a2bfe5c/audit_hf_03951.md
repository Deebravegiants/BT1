# [H] Destination Vault rewards are not added to

## Summary
Severity: High
Contest weight: 0.7795
Dataset id: 20293
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _withdraw function, Destination Vault rewards will be first recorded in info.IdleIncrease by info.idleIncrease += _baseAsset.balanceOf(address(this)) - assetPreBal - assetPulled;. But when info.totalAssetsPulled > info.totalAssetsToPull, info.idleIncrease is directly assigned as info.totalAssetsPulled - info.totalAssetsToPull, and info.totalAssetsPulled is assetPulled without considering Destination Vault rewards.
3-07-14/src/vault/LMPVault.sol#L482-L497
```solidity
uint256 assetPreBal = _baseAsset.balanceOf(address(this));
uint256 assetPulled = destVault.withdrawBaseAsset(sharesToBurn, address(this));
// Destination Vault rewards will be transferred to us as part of burning out shares
// Back into what that amount is and make sure it gets into idle
info.idleIncrease += _baseAsset.balanceOf(address(this)) - assetPreBal - assetPulled;

info.totalAssetsPulled += assetPulled;
info.debtDecrease += totalDebtBurn;
// It's possible we'll get back more assets than we anticipate from a swap
// so if we do, throw it in idle and stop processing. You don't get more than we've calculated

if (info.totalAssetsPulled > info.totalAssetsToPull) {
    info.idleIncrease = info.totalAssetsPulled - info.totalAssetsToPull;
    info.totalAssetsPulled = info.totalAssetsToPull;
    break;
}
```
For example,
// preBal == 100 pulled == 10 reward == 5 toPull == 6
// idleIncrease = 115 - 100 - 10 == 5
// totalPulled(0) += assetPulled == 10 > toPull
// idleIncrease = totalPulled - toPull == 4 < reward
ultimately recorded by the Vault.
ultimately recorded by the Vault.
Meanwhile, due to the recover function's inability to extract the baseAsset, this will result in no operations being able to handle these Destination Vault rewards, ultimately causing these assets to be frozen within the contract.

## Recommendation
```solidity
info.idleIncrease = info.totalAssetsPulled - info.totalAssetsToPull; ->
info.idleIncrease += info.totalAssetsPulled - info.totalAssetsToPull;
```
