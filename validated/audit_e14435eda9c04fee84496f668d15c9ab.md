Audit Report

## Title
Rewards Permanently Locked When `totalKernelStaked` Drops to Zero Mid-Period - (File: contracts/KERNEL/KernelDepositPool.sol)

## Summary
`KernelDepositPool` implements a Synthetix-style staking rewards accumulator. While `notifyRewardAmount` correctly guards against starting a reward period with zero stakers, it provides no protection against `totalKernelStaked` dropping to zero mid-period. When this occurs, `rewardPerToken()` stops advancing and all reward tokens that should have been distributed during the zero-staking interval become permanently locked in the contract with no recovery path.

## Finding Description
`notifyRewardAmount` (L570) reverts with `NoStakedTokens` if `totalKernelStaked == 0` at call time — this guard is present and correct. However, it does not prevent the pool from reaching `totalKernelStaked == 0` after a reward period has started.

`rewardPerToken()` (L408–414) short-circuits when `totalKernelStaked == 0`:
```solidity
if (totalKernelStaked == 0) {
    return rewardPerTokenStored;
}
```
During any interval where `totalKernelStaked == 0`, `rewardRate` continues to tick but `rewardPerTokenStored` does not advance. No user's `rewards[user]` mapping is credited for that interval. The reward tokens (already transferred in by `notifyRewardAmount`) accumulate as unallocated balance.

There is no admin sweep, rescue, or re-injection function in the contract. The admin functions are limited to `setRewardsDuration`, `notifyRewardAmount`, `setWithdrawalDelay`, and `setMaxNumberOfWithdrawalsPerUser` — none of which can recover stranded reward tokens.

The exploit path is straightforward:
1. Admin calls `notifyRewardAmount` while `totalKernelStaked > 0` (passes the L570 guard).
2. All stakers call `initiateWithdrawal`, wait out `withdrawalDelay`, and call `claimWithdrawal`. `totalKernelStaked` reaches 0.
3. For the remainder of the reward window, `rewardPerToken()` returns `rewardPerTokenStored` unchanged.
4. `rewardRate * remainingSeconds` worth of reward tokens are permanently locked.

The contract's own NatSpec (L17–22) acknowledges this behavior and relies on an operational convention (keeping ≥1 wei staked at all times) rather than any on-chain enforcement.

## Impact Explanation
Reward tokens transferred into the contract via `notifyRewardAmount` that correspond to a zero-staking interval are permanently unrecoverable. This constitutes **permanent freezing of unclaimed yield** — a valid Medium impact per the allowed scope.

## Likelihood Explanation
Any scenario where all stakers exit during an active reward window triggers the bug. This is reachable by normal user actions (`initiateWithdrawal` + `claimWithdrawal`) with no special privileges required. Realistic paths include a single large staker who is the sole depositor exiting, or a coordinated exit during early deployment when staker count is low. The contract provides no on-chain minimum-stake floor to prevent this state.

## Recommendation
1. Track the cumulative duration during which `totalKernelStaked == 0` and extend `finishAt` by that amount when staking resumes, so no rewards are skipped.
2. Alternatively, add an admin-callable rescue function to recover unallocated reward tokens (i.e., `rewardsToken.balanceOf(address(this))` minus the sum of all `rewards[user]` balances) after a reward period ends.
3. Enforce a minimum staked amount on-chain (e.g., require `totalKernelStaked >= MIN_STAKE` before allowing `initiateWithdrawal` to reduce it to zero during an active reward period).

## Proof of Concept
```
1. Admin calls setRewardsDuration(7 days).
2. Alice stakes 100e18 KERNEL. totalKernelStaked = 100e18.
3. Admin calls notifyRewardAmount(1000e18). rewardRate = 1000e18 / 7 days. Passes L570 guard.
4. 3 days pass. Alice calls initiateWithdrawal(100e18). totalKernelStaked = 0.
5. After withdrawalDelay, Alice calls claimWithdrawal. Her earned rewards up to day 3 are correctly credited.
6. For the remaining 4 days, rewardPerToken() returns rewardPerTokenStored unchanged (L409–411).
7. ~571e18 reward tokens (rewardRate * 4 days) remain permanently locked. No function exists to recover them.
```
A Foundry test can confirm this by asserting `rewardsToken.balanceOf(address(pool)) > 0` after `finishAt` has passed and all users have claimed, with no callable function able to reduce that balance.