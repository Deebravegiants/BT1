# [H] _requestedTip is not deduced

## Summary
Severity: High
Contest weight: 0.8721
Dataset id: 1942
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description
GovernanceStaker introduces the concept of bumping earning power to control the amount of rewards claimable by depositors who delegate to inactive delegatees. The bumpEarningPower function enables keepers to update earningPower on behalf of depositors, and take a fee to do so.
GovernanceStaker.sol#L508:
```solidity
// Send tip to the receiver
SafeERC20.safeTransfer(REWARD_TOKEN, _tipReceiver, _requestedTip);
```
Some checks are done to ensure that depositor has enough rewards so that the _requestedTip can be covered out of the rewards.
GovernanceStaker.sol#L489-L497:
```solidity
if (_newEarningPower > deposit.earningPower && _unclaimedRewards < _requestedTip) {
    revert GovernanceStaker__InsufficientUnclaimedRewards();
}
```
tip is more than unclaimed rewards
```solidity
if (_newEarningPower < deposit.earningPower && (_unclaimedRewards - _requestedTip) < maxBumpTip) {
    revert GovernanceStaker__InsufficientUnclaimedRewards();
}
```
Unfortunately, the requested tip is never deducted from the depositor rewards. Which means that the accounting is incorrect, and some legitimate participants would not be able to claim their rewards.
Rewards are denied to legitimate participants (rewards insolvency)

## Recommendation
Consider subtracting the tip from the depositor rewards:
GovernanceStaker.sol#L508:
```solidity
// Send tip to the receiver
SafeERC20.safeTransfer(REWARD_TOKEN, _tipReceiver, _requestedTip);
+
deposit.scaledUnclaimedRewardCheckpoint =
+
deposit.scaledUnclaimedRewardCheckpoint - (_requestedTip * SCALE_FACTOR);
```
