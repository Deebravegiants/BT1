# [M] claim all rewards function fails to accrue rewards correctly.

## Summary
Severity: Medium
Chain: Smart contract
Component: VMEX
Published: 2023-06-21
Source: https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/issues/38
Type: hats-finding

## Details
**Github username:** @ArnieGod
**Submission hash (on-chain):** 0x5719a34f5400575f90b590069b529599686f752ffacaa11896483ee11599d99b
**Severity:** medium severity

**Description:**
## Vulnerability Report
**Description**
<!-- Describe the context and the effect of the vulnerability. -->
In IncentivesController.sol
```solidity
  function claimReward(
    address[] calldata incentivizedAssets,
    address reward,
    uint256 amountToClaim,
    address to
  ) external override returns (uint256) {
    if (amountToClaim == 0) {
      return 0;
    }

    address user = msg.sender;
    DistributionTypes.UserAssetState[] memory userState = _getUserState(incentivizedAssets, user);
    _batchUpdate(user, userState);
```
the function above calls into 
```solidity
_batchUpdate(user, userState);
```
this function call will accrue rewards and update the reward timestamp. However when we call `claimAllRewards`
```solidity
  function claimAllRewards(
    address[] calldata incentivizedAssets,
    address to
  ) external override returns (address[] memory, uint256[] memory) {
    address[] memory rewards = _allRewards;
    uint256[] memory amounts = new uint256[](_allRewards.length);
    address user = msg.sender;
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/issues/38_
