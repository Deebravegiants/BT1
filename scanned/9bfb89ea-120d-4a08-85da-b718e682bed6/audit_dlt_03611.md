# [M] Rounding of `user.virtualRewards` happens in user's favour inside `claimAllRewards()`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-03-saltyio-mitigation
Published: 2024-03-03
Source: https://github.com/code-423n4/2024-03-saltyio-mitigation-findings/issues/25
Type: code-finding

## Details
# Lines of code

https://github.com/othernet-global/salty-io/blob/main/src/staking/StakingRewards.sol#L161-L166
https://github.com/othernet-global/salty-io/blob/main/src/staking/StakingRewards.sol#L250-L256
https://github.com/othernet-global/salty-io/blob/main/src/staking/StakingRewards.sol#L122-L123


# Vulnerability details

## Summary
[These lines](https://github.com/othernet-global/salty-io/blob/main/src/staking/StakingRewards.sol#L122-L123) were changed as a fix to M-01. `virtualRewardsToRemove` is now rounded up since it needs to be deducted later on from `claimableRewards` on L138.
While this is okay here, it has now led to a rounding of `user.virtualRewards` against the protocol, causing loss inside [claimAllRewards()](https://github.com/othernet-global/salty-io/blob/main/src/staking/StakingRewards.sol#L161-L166).

## New Issue
`_decreaseShare()` is not the only function which enables a user to claim rewards. `claimAllRewards()` can be called too by the user. `claimAllRewards()` internally calls [userRewardForPool()](https://github.com/othernet-global/salty-io/blob/main/src/staking/StakingRewards.sol#L237) which makes use of the `user.virtualRewards` variable in [L250-256](https://github.com/othernet-global/salty-io/blob/main/src/staking/StakingRewards.sol#L250-L256). Since the new fix reduced `user.virtualRewards` to a greater extent than it did in the previous implementation, [L256](https://github.com/othernet-global/salty-io/blob/main/src/staking/StakingRewards.sol#L256) can now return a user reward greater than it did in the previous implementation. The fix has caused the rounding of userRewardForPool against the protocol.

## Impact
Calculation does not round in favour of the protocol, which means that value may leak from the system in favour of the users. This vulnerability enables users to claim more rewards than they are entitled to. Although each instance might involve a small amount, the cumulative effect could be significant due to the frequency of occurrences.

More importantly, this may even cause the last reward claim to witness a scenario where there are not enough rewards to pay them out.

## Recommended Mitigation Steps
While this can be approached in multiple ways, to avoid confusion let's have two separate variables for `virtualRewardsToRemove` accounting, one rounded-up and one rounded-down:
```diff
  File: src/staking/StakingRewards.sol

  // Decrease a user's share for the pool and have any pending rewards sent to them.
  // Does not require the pool to be valid (in case the pool was recently unwhitelisted).
  function _decreaseUserShare( address wallet, bytes32 poolID, uint256 decreaseShareAmount, bool useCooldown ) internal
  {
    require( decreaseShareAmount != 0, "Cannot decrease zero share" );

    UserShareInfo storage user = _userShareInfo[wallet][poolID];
    require( decreaseShareAmount <= user.userShare, "Cannot decrease more than existing user share" );

    if ( useCooldown )
      if ( msg.sender != address(exchangeConfig.dao()) ) // DAO doesn't use the cooldown
      {
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-03-saltyio-mitigation-findings/issues/25_
