# [M] User will loose rewards if `escrowPool` is set to address(0)

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-merit-circle
Published: 2022-10-14
Source: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/115
Type: sherlock-finding

## Details
saian

medium

# User will loose rewards if `escrowPool` is set to address(0)

## Summary

Since `escrowPool` is not validated during initialization, if the value is set to address(0) user will loose rewards

## Impact

In `claimRewards` function a portion of the reward amount is subtracted from the reward amount and sent to the escrow pool. If the `escrowPool` is set to address(0), the reward amount is not deposited to the escrow pool and remains in the contract. Only the remaining amount is sent to the user

## Code Snippet

https://github.com/Merit-Circle/merit-liquidity-mining/blob/ce5feaae19126079d309ac8dd9a81372648437f1/contracts/base/BasePool.sol#L105

```
    function claimRewards(address _receiver) external {
        uint256 rewardAmount = _prepareCollect(_msgSender());
        uint256 escrowedRewardAmount = rewardAmount * escrowPortion / 1e18;
        uint256 nonEscrowedRewardAmount = rewardAmount - escrowedRewardAmount;

        if(escrowedRewardAmount != 0 && address(escrowPool) != address(0)) {
            escrowPool.deposit(escrowedRewardAmount, escrowDuration, _receiver);
        }
        
        // ignore dust
        if(nonEscrowedRewardAmount > 1) {
            rewardToken.safeTransfer(_receiver, nonEscrowedRewardAmount);
        }
```

## Tool used

Manual Review


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/115_
