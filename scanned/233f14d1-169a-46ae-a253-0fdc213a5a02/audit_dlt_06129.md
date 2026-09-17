# [H] Users can `migrate()` before the first harvest to gain more shares

## Summary
Severity: High
Chain: Smart contract
Component: StakeWise
Published: 2023-08-28
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/120
Type: hats-finding

## Details
**Github username:** @milotruck
**Submission hash (on-chain):** 0x94439e5b5e5d0bccba8f5ac662c98fc182f53885b4787b1749143d12e491d8f4
**Severity:** high

**Description:**
## Bug Description

In `EthGenesisVault.sol`, on the first harvest, the total rewards accumulated in the legacy pool is deducted:

[EthGenesisVault.sol#L107-L110](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/ethereum/EthGenesisVault.sol#L107-L110)

```solidity
    if (!isCollateralized) {
      // it's the first harvest, deduct rewards accumulated so far in legacy pool
      totalAssetsDelta -= SafeCast.toInt256(_rewardEthToken.totalRewards());
    }
```

Since almost all assets will still be in the legacy pool, most of the deduction penalty will be passed on to V2's `RewardETHToken` contract by calling [`updateTotalRewards()`](https://github.com/stakewise/contracts/blob/v3-migration/contracts/tokens/RewardEthToken.sol#L228-L301):

[EthGenesisVault.sol#L115-L125](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/ethereum/EthGenesisVault.sol#L115-L125)

```solidity
    // calculate total principal
    uint256 totalPrincipal = _totalAssets + legacyPrincipal;
    if (totalAssetsDelta < 0) {
      // calculate and update penalty for legacy pool
      int256 legacyPenalty = SafeCast.toInt256(
        Math.mulDiv(uint256(-totalAssetsDelta), legacyPrincipal, totalPrincipal)
      );
      _rewardEthToken.updateTotalRewards(-legacyPenalty);
      // deduct penalty from total assets delta
      totalAssetsDelta += legacyPenalty;
    } else {
```

In the `RewardEthToken` contract, the penalty will be added to `totalPenalty`:

[RewardEthToken.sol#L246-L251](https://github.com/stakewise/contracts/blob/v3-migration/contracts/tokens/RewardEthToken.sol#L246-L251)

```solidity
        } else if (rewardsDelta < 0) {
            uint256 _totalPenalty = totalPenalty; // gas savings
            _totalPenalty = _totalPenalty.add(uint256(- rewardsDelta));
            require(_totalPenalty <= totalAssets(), "RewardEthToken: invalid penalty amount");
            totalPenalty = _totalPenalty;
        }
```

Therefore, after the first harvest, users from V2 that are migrating to V3 will receive shares based on only their assets in `StakedEthToken`, and will not receive shares for accrued rewards, due to `totalPenalty`:

[RewardEthToken.sol#L323-L330](https://github.com/stakewise/contracts/blob/v3-migration/contracts/tokens/RewardEthToken.sol#L323-L330)

```solidity
        uint256 _totalPenalty = totalPenalty; // gas savings
        if (_totalPenalty > 0) {
            uint256 _totalAssets = totalAssets(); // gas savings
            // apply penalty to assets
            uint256 assetsAfterPenalty = assets.mul(_totalAssets.sub(_totalPenalty)).div(_totalAssets);
            totalPenalty = _totalPenalty.add(assetsAfterPenalty).sub(assets);
            assets = assetsAfterPenalty;
        }
```

However, there is no check in [`migrate()`](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/ethereum/EthGenesisVault.sol#L145-L161) that ensures the vault is collateralized, which means users can call `migrate()` before `updateState()` has been called once.

Therefore, users can migrate from V2 to V3 before the first harvest, which means `totalPenalty` would not have been initialized yet. As such, both their assets and rewards in V2 will be migrated, allowing them to unfairly gain more shares in the Genesis Vault compared to users who migrate after the first harvest.

## Impact

Users can migrate from V2 before the first harvest to unfairly gain more shares in the Genesis Vault, as compared to users who migrate after the first harvest is made.

This results in a direct loss of funds for users who migrate after the first harvest, as they will gain less shares for migrating the same amount of assets and rewards from V2.

## Recommended Mitigation

Consider allowing `migrate()` to only be called after the Genesis Vault has been collateralized:

[EthGenesisVault.sol#L146-L149](https://github.com/stakewise/v3-core/blob/main/contracts/vaults/ethereum/EthGenesisVault.sol#L146-L149)

```diff
  function migrate(address receiver, uint256 assets) external override returns (uint256 shares) {
    if (msg.sender != address(_rewardEthToken)) revert Errors.AccessDenied();

    _checkHarvested();
+   _checkCollateralized();
```
