# [M] M-05 MitigationConfirmed

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-09-reserve-mitigation
Published: 2023-09-27
Source: https://github.com/code-423n4/2023-09-reserve-mitigation-findings/issues/13
Type: code-finding

## Details
# Lines of code




# Vulnerability details

In the previous implementation
when `stakingContract.totalAllocPoint = 0`
`stakingContract.withdraw()` and `stakingContract.deposit()` will div 0 , `revert`
This results in `StargateRewardableWrapper` no longer being able to execute `StargateRewardableWrapper.withdraw()`
The user's token is locked

# Mitigation
[PR 896](https://github.com/reserve-protocol/protocol/pull/896)
Add determine if `poolInfo.allocPoint` is equal to 0.
If equal to 0, use `stakingContract.emergencyWithdraw()` instead of `stakingContract.deposit()` to avoid revert
the mitigation resolved the original issue.


# Suggestion
Since `allocPoint==0` is used instead of `totalAllocPoint==0`
there may be a case where `allocPoint == 0` but `totalAllocPoint> 0`.
But the modified version still uses `stakingContract.emergencyWithdraw()`, which discards all rewards.
It is recommended that if `totalAllocPoint> 0` ,we can execute the
`stakingContract.deposit(0)` to retrieve the reward first, then execute `stakingContract.emergencyWithdraw()`.
