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
the `_batchUpdate(user, userState)` function is not called, therefore the accrued rewards and the rewards timestamp is never updated.
additionally,
```solidity
 function _updateReward(
    DistributionTypes.Reward storage reward,
    uint256 totalSupply,
    uint8 decimals
  ) internal returns (uint256, bool) {
    bool updated;
    uint256 newIndex = _getAssetIndex(reward, totalSupply, decimals);

    if (newIndex != reward.index) {
      reward.index = newIndex;
      updated = true;
    }
    reward.lastUpdateTimestamp = uint128(block.timestamp);

    return (newIndex, updated);
  }
```
the  reward.lastUpdateTimestamp is not updated correctly as well, the impact is the lastUpdateTimestamp can be stale and make the check below ineffective
```solidity
 function _getAssetIndex(
    DistributionTypes.Reward storage reward,
    uint256 totalSupply,
    uint8 decimals
  ) internal view returns (uint256) {
    if (
      reward.emissionPerSecond == 0 ||
      totalSupply == 0 ||
      reward.lastUpdateTimestamp == block.timestamp ||
      reward.lastUpdateTimestamp >= reward.endTimestamp
    ) {
      return reward.index;
    }
```

**impact**

claimAllRewards does not take the pending accured reward into consideration and the lastUpdateTimestamp can be stale.

**code snippet**

https://github.com/hats-finance/VMEX-0x050183b53cf62bcd6c2a932632f8156953fd146f/blob/fb396a3fa412e643de7d8a1fd8a0268ab3a2f993/packages/contracts/contracts/protocol/incentives/IncentivesController.sol#L203-L220

**recommendation**

I recommend adding `_batchUpdate(user, userState)` to the `claimAllRewards` function.
