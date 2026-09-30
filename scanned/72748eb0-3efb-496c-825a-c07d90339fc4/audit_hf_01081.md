# [C] incentiveToken is not verified within incentivizeRecurPool

## Summary
Severity: Critical
Contest weight: 0.2987
Dataset id: 4138
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When incentivizeRecurPool is called, it will iterate through params and update state.rewardRate based on the provided incentiveAmount.
```solidity
function incentivizeRecurPool(
    RecurIncentiveParams[] calldata params,
    address incentiveToken
) external returns (uint256 totalIncentiveAmount) {
    address msgSender = LibMulticaller.senderOrSigner();
    for (uint256 i; i < params.length; i++) {
        // -----------------------------------------------------------------------
        /// Validation
        // -----------------------------------------------------------------------
        if (params[i].incentiveAmount == 0) continue;
        RecurPoolKey calldata key = params[i].key;
        if (!isValidRecurPoolKey(key)) continue;
        // ...
        // -----------------------------------------------------------------------
        /// State updates
        // -----------------------------------------------------------------------
        // ...
        // record new reward
        uint256 newRewardRate;
        if (block.timestamp >= periodFinish) {
            // current period is over
            // uint256 internal constant REWARD_RATE_PRECISION = 1e6;
            newRewardRate = params[i].incentiveAmount.mulDiv(REWARD_RATE_PRECISION, key.duration);
            state.rewardRate = newRewardRate;
            state.lastUpdateTime = uint64(block.timestamp);
            state.periodFinish = uint64(block.timestamp + key.duration);
        } else {
            // period is still active
            // add the new reward to the existing period
            uint256 remaining = periodFinish - block.timestamp;
            newRewardRate += params[i].incentiveAmount.mulDiv(REWARD_RATE_PRECISION, remaining);
            state.rewardRate = newRewardRate;
            state.lastUpdateTime = uint64(block.timestamp);
            // prevent overflow when computing rewardPerToken
            if (newRewardRate >= ((type(uint256).max / PRECISION_DIV_REWARD_RATE_PRECISION) / key.duration)) {
                revert MasterBunni__AmountTooLarge();
            }
        }
        totalIncentiveAmount += params[i].incentiveAmount;
    }
    // transfer incentive tokens from msgSender to this contract
    if (totalIncentiveAmount != 0) {
        incentiveToken.safeTransferFrom2(msgSender, address(this), totalIncentiveAmount);
    }
    // ...
}
```
However, within the loop, it never validates that the current rewardToken is equal to incentiveToken, allowing an attacker to increase state.rewardRate without providing the actual rewardToken. This results in users being unable to claim the reward due to the unavailability of rewardToken in the contract, even when legitimate incentives exist.

## Recommendation
Validate that rewardToken is equal to incentiveToken within the incentivizeRecurPool calls.
