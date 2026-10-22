# [M] Division before multiplication result in loss of

## Summary
Severity: Medium
Contest weight: 0.5882
Dataset id: 20189
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Division before multiplication result in loss of token reward. When calculating the reward, we are calling
```solidity
function currentRewardsPerToken() public view returns (uint256) {
    // Rewards do not accrue if the total balance is zero
    if (totalBalance == 0) return rewardsPerTokenStored;
    // loss of precision
    // The number of rewards to apply is based on the reward rate and the amount of time that has passed since the last reward update
    uint256 rewardsToApply = ((block.timestamp - lastRewardUpdate) *
        rewardRate) /
        REWARD_PERIOD;
    // The rewards per token is the current rewards per token plus the rewards to apply divided by the total staked balance
    return rewardsPerTokenStored + (rewardsToApply * 10 ** stakedTokenDecimals) / totalBalance;
}
```
The precision loss can be high because the accumulated reward depends on the time elapse: (block.timestamp - lastRewardUpdate) and the REWARD_PERIOD is hardcoded to one days:
```solidity
/// @notice Amount of time (in seconds) that the reward rate is distributed over
uint48 public constant REWARD_PERIOD = uint48(1 days);
```
If the time elapse is short and the currentRewardsPerToken is updated frequently, the precision loss can be heavy and even rounded to zero. The lower the token precision, the heavier the precision loss. https://github.com/d-xo/weird-erc20#low-decimals. Some tokens have low decimals (e.g. USDC has 6). Even more extreme, some tokens like Gemini USD only have 2 decimals. Consider as extreme case, if the reward token is Gemini USD, the reward rate is set to 1000 * 10 = 10 ** 4 = 10000. If the update reward keep getting called within 8 seconds: 8 * 10000 / 86400 is already rounded down to zero and no reward is accruing for user. Division before multiplication result in loss of token reward if the reward update time elapse is small.

## Recommendation
Avoid division before multiplication and only perform division at last.
