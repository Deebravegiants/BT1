# [H] Users in EthGenesisVault gain more than users in of StakeWise v2

## Summary
Severity: High
Chain: Smart contract
Component: StakeWise
Published: 2023-08-28
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/124
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Submission hash (on-chain):** 0x3d2c2c7c13630e5a2800350391d904c78b2abc04f1c525f0dbbf8d0fc2125a42
**Severity:** high

**Description:**
**Description**\

In EthGenesisVault, updateState() calculated in this way, [https://github.com/stakewise/v3-core/blob/c82fc57d013a19967576f683c5e41900cbdd0e67/contracts/vaults/ethereum/EthGenesisVault.sol#L99-L133](https://github.com/stakewise/v3-core/blob/c82fc57d013a19967576f683c5e41900cbdd0e67/contracts/vaults/ethereum/EthGenesisVault.sol#L99-L133)
```solidity
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
      // calculate and update reward for legacy pool
      int256 legacyReward = SafeCast.toInt256(
        Math.mulDiv(uint256(totalAssetsDelta), legacyPrincipal, totalPrincipal)
      );
      _rewardEthToken.updateTotalRewards(legacyReward);
      // deduct reward from total assets delta
      totalAssetsDelta -= legacyReward;
```
and ```_totalAssets``` is used for the calculation of ```totalPrincipal```.
any change in `_totalAssets `affects `totalAssetsDelta `for EthGenesisVault and `legacyReward `for StakeWise v2.
`_totalAssets `could be changed by updatestate() so in the next updatestate() `totalAssetsDelta `will be changed.

The problem is `totalAssetsDelta `which increases totalAssets to gain more rewards for the next updatestate(), But It's fair if totalAssetsDelta(ETH) is used by validators or exits.

**Attack Scenario**\

- _totalAssets is 64 Amount
- updateState()  called (totalAssetsDelta will be 1 Amount as well)
- _totalAssets will be 65 Amount(but this 1 Amount is fair if used by vault)

_Trimmed to 38 lines — full report: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/124_
