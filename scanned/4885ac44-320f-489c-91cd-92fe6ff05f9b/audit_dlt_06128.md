# [H] Wrong split of rewards in EthGenesisVault

## Summary
Severity: High
Chain: Smart contract
Component: StakeWise
Published: 2023-08-28
Source: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/121
Type: hats-finding

## Details
**Github username:** @0xmahdirostami
**Submission hash (on-chain):** 0xeae272a6525983761b70ae500e630f0871efc32ffcc999aec072d507ed1280c0
**Severity:** high

**Description:**
**Description**\
EthGenesisVault splits reward between v2 and v3 in the following way:
```solidity
    uint256 legacyPrincipal = _rewardEthToken.totalAssets() - _rewardEthToken.totalPenalty();


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
      // calculate and update reward for legacy pool
      int256 legacyReward = SafeCast.toInt256(
        Math.mulDiv(uint256(totalAssetsDelta), legacyPrincipal, totalPrincipal)
      );
      _rewardEthToken.updateTotalRewards(legacyReward);
      // deduct reward from total assets delta
      totalAssetsDelta -= legacyReward;
    }
```
If someone deposits ETH, the ```_totalAssets``` for EthGenesisVault will be increased and more rewards will be assigned to EthGenesisVault.
The problem is if **that deposited ETH is an unbounded ETH, so it shouldn't affect _totalAssets**

**Scenario**\

- _totalAssets is 32 ETH, legacyPrincipal is 32ETH
- some user deposit 5 ETH(**Unbounded ETH**)

_Trimmed to 38 lines — full report: https://github.com/hats-finance/StakeWise-0xd91cd6ed6c9a112fdc112b1a3c66e47697f522cd/issues/121_
