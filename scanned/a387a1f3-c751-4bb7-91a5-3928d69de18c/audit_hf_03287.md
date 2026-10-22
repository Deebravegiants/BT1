# [M] `MultiRewardStaking.changeRewardSpeed

## Summary
Severity: Medium
Contest weight: 0.6293
Dataset id: 18049
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the function that changes the reward emission rate of a staking contract. When the reward speed is adjusted, the contract calls an internal routine to compute a new end timestamp for the reward distribution. The routine adds the remaining token balance to the amount that would have been emitted up to the previous end timestamp and then divides this inflated amount by the new rewards‑per‑second value. Because the calculation adds the already‑distributed portion again, increasing the reward speed paradoxically lengthens the distribution period instead of shortening it. As a result the contract believes it has more time to dispense rewards than it actually does, and it will attempt to pay out tokens that are not present in its balance. This flaw is triggered when the changeRewardSpeed function is called after the original schedule has started (i.e., block.timestamp is between the start and the previous end) and the new rewards‑per‑second value is higher than the old one. Users who have staked expect to receive a proportional share of the remaining rewards, but they may see their balances stay unchanged, receive zero tokens, or experience failed transfers because the contract runs out of tokens. The issue was discovered during a formal audit by Code4rena, which demonstrated the problem with a concrete example: an initial schedule of 200 tokens at 2 tokens per second ending at timestamp 100, changed at timestamp 50 to 4 tokens per second, incorrectly produced a new end timestamp of 125, causing the contract to promise distribution of 300 tokens while only 100 remained. The bug is hard to notice because the end timestamp appears later than expected, and the contract may still have enough tokens for a short period before the shortfall becomes evident. To fix the problem the contract must recompute the remaining undistributed amount without double‑counting the already‑emitted tokens and set the new end timestamp as current time plus remaining amount divided by the new reward rate. In abstract terms this is an accounting logic error in the reward schedule calculation, leading to over‑promised rewards and potential loss of trust in the protocol.

## Proof of Concept
Given that we have an existing reward with the following configuration:

  * startTimestamp = 0
  * endTimestamp = 100
  * rewardPerSecond = 2
  * initialBalance = 200

The reward speed is changed at `timestamp = 50`, meaning 100 tokens were already distributed. The new endTimestamp is calculated by calling `_calcRewardsEnd()`:

```solidity
// @audit using balanceOf() here has its own issues but let's ignore those for this submission
uint256 remainder = rewardToken.balanceOf(address(this));

uint32 prevEndTime = rewards.rewardsEndTimestamp;

uint32 rewardsEndTimestamp = _calcRewardsEnd(
  prevEndTime > block.timestamp ? prevEndTime : block.timestamp.safeCastTo32(),
  rewardsPerSecond,
  remainder
);
```

And the calculation is:

```solidity
function _calcRewardsEnd(
  uint32 rewardsEndTimestamp,
  uint160 rewardsPerSecond,
  uint256 amount
) internal returns (uint32) {
  if (rewardsEndTimestamp > block.timestamp)
    amount += uint256(rewardsPerSecond) * (rewardsEndTimestamp - block.timestamp);

  return (block.timestamp + (amount / uint256(rewardsPerSecond))).safeCastTo32();
}
```

  * `rewardsEndTimestamp = 100` (initial endTimestamp)
  * `block.timestamp = 50` (as described earlier)
  * `amount = 100`
  * `rewardsPerSecond = 4` (we update it by calling this function)

Because `rewardEndTimestamp > block.timestamp`, the if clause is executed and `amount` is increased:

$amountNew = 100 + 4 \ast (100 - 50) = 300$

Then it calculates the new `endTimestamp`:

$50 + (300 / 4) = 125$

Thus, by increasing the `rewardsPerSecond` from `2` to `4`, we’ve **increased** the `endTimestamp` from `100` to `125` instead of decreasing it. The total amount of rewards that are distributed are calculated using the `rewardsPerSecond` and `endTimestamp`. Meaning, the contract will also try to distribute tokens it doesn’t hold. It only has the remaining `100` tokens.

By increasing the `rewardsPerSecond` the whole distribution is broken.

## Recommendation
It’s not easy to fix this issue with the current implementation of the contract. There are a number of other issues. But, in essence:

  * determine the remaining amount of tokens that need to be distributed
  * calculate the new endTimestamp: `endTimestamp = remainingAmount / newRewardsPerSecond`
