# [M] Misconfigured pool can lead to rewards locked indefinitely

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-merit-circle
Published: 2022-10-14
Source: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/56
Type: sherlock-finding

## Details
Jeiwan

medium

# Misconfigured pool can lead to rewards locked indefinitely

## Summary
Due to weak validation of the BasePool initialization function ([__BasePool_init](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/base/BasePool.sol#L48)) it's possible to deploy a pool with a misconfigured escrow pool: `escrowPool` can be set to the zero address while `escrowPortion` is set to a valid value. In such a pool, depositors will get only a portion of reward tokens (as per `escrowPortion`) and the remaining part will remain locked in the pool and unclaimable indefinitely.
## Vulnerability Detail
The root cause is in [these lines](https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/base/BasePool.sol#L102-L107):
```solidity
function claimRewards(address _receiver) external {
    uint256 rewardAmount = _prepareCollect(_msgSender());
    // @audit escrow amount is extracted before escrow pool configuration is validated
    uint256 escrowedRewardAmount = rewardAmount * escrowPortion / 1e18;
    uint256 nonEscrowedRewardAmount = rewardAmount - escrowedRewardAmount;

    if(escrowedRewardAmount != 0 && address(escrowPool) != address(0)) {
        escrowPool.deposit(escrowedRewardAmount, escrowDuration, _receiver);
    }

    // ignore dust
    if(nonEscrowedRewardAmount > 1) {
        rewardToken.safeTransfer(_receiver, nonEscrowedRewardAmount);
    }
    ...
}
```
Here, `rewardAmount` is split into `escrowedRewardAmount` and `nonEscrowedRewardAmount` before the check for configured escrow pool is made. In case `escrowedRewardAmount` is non-zero and `escrowPool` is the zero address:
1. `escrowedRewardAmount` will be subtracted from `rewardAmount`;
1. `escrowedRewardAmount` won't be sent to `escrowPool` because it's not configured;
1. the user will get only `nonEscrowedRewardAmount`;
1. `escrowedRewardAmount` will remain unclaimable.
## Impact
Reward tokens that are expected to be distributed among users pro-rata get locked in a misconfigured pool indefinitely.
## Code Snippet
```javascript
// test/BasePool.ts
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/56_
