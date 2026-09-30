# [M] _rebalancePosition() will rebalance to a incorrect target position due to incorrect calculation of currentAssets

## Summary
Severity: Medium
Contest weight: 0.2108
Dataset id: 19722
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
_rebalancePosition() will rebalance to a incorrect target position due to incorrect calculation of currentAssets. See code snippets and POC below for more detail.
https://github.com/equilibria-xyz/perennial-mono/blob/ea722b43df29b9693f4b4e8ebecb31d8258dbe1b/packages/perennial-vaults/contracts/BalancedVault.sol#L400-L41
https://github.com/equilibria-xyz/perennial-mono/blob/ea722b43df29b9693f4b4e8ebecb31d8258dbe1b/packages/perennial-vaults/contracts/BalancedVault.sol#L578-L58

## Proof of Concept
Given:
● longCollateral == 150 (50 of which belongs to exitsing stakeholders and 100 to the new _deposit)
● shortCollateral == 150 (same as above)
● idleCollateral == 0
● _deposit == 200
● totalShares == 100
Alice redeem() 40 shares;
● totalShares: 100 -> 60
● _redemption: 0 -> 40
L170, _rebalance():
● _totalAssetsAtVersion() => (150 + 150 + 0) - (0 + 200) == 100
● L401, currentAssets => 100 + 200 == 300;
● L406, currentUtilized => 300 * 60 / 100 == 180;
● L408, targetPosition => 180 * targetLeverage / currentPrice / 2
The expected result is that all of the _deposit (200) should be invested, with 60 of the existing position collateral (100) kept and only 40 removed. So the targetPosition should be 260 * targetLeverage / currentPrice / 2.

## Recommendation
L401 currentAssets should not include _deposit; _deposit should be added to currentUtilized at L408 instead: The fix of M-01 is good.
