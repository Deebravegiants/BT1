# [H] Staking rewards can be drained

## Summary
Severity: High
Chain: Smart contract
Component: 2023-01-popcorn
Published: 2023-02-07
Source: https://github.com/code-423n4/2023-01-popcorn-findings/issues/402
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-01-popcorn/blob/d95fc31449c260901811196d617366d6352258cd/src/utils/MultiRewardStaking.sol#L170-L187


# Vulnerability details

## Impact

If ERC777 tokens are used for rewards, the entire balance of rewards in the staking contract can get drained by an attacker.

## Proof of Concept

ERC777 allow users to register a hook to notify them when tokens are transferred to them. 

This hook can be used to reenter the contract and drain the rewards.

The issue is in the `claimRewards` in `MultiRewardStaking`.
The function does not follow the checks-effects-interactions pattern and therefore can be reentered when transferring tokens in the for loop.
https://github.com/code-423n4/2023-01-popcorn/blob/d95fc31449c260901811196d617366d6352258cd/src/utils/MultiRewardStaking.sol#L170-L187
```
  function claimRewards(address user, IERC20[] memory _rewardTokens) external accrueRewards(msg.sender, user) {
    for (uint8 i; i < _rewardTokens.length; i++) {
      uint256 rewardAmount = accruedRewards[user][_rewardTokens[i]];

      if (rewardAmount == 0) revert ZeroRewards(_rewardTokens[i]);

      EscrowInfo memory escrowInfo = escrowInfos[_rewardTokens[i]];

      if (escrowInfo.escrowPercentage > 0) {
        _lockToken(user, _rewardTokens[i], rewardAmount, escrowInfo);
        emit RewardsClaimed(user, _rewardTokens[i], rewardAmount, true);
      } else {
        _rewardTokens[i].transfer(user, rewardAmount);
        emit RewardsClaimed(user, _rewardTokens[i], rewardAmount, false);
      }

      accruedRewards[user][_rewardTokens[i]] = 0;
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-01-popcorn-findings/issues/402_
