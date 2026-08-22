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


_Trimmed to 38 lines — full report: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/120_
