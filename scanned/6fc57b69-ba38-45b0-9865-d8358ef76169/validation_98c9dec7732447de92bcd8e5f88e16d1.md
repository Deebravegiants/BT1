### Title
Rewards Permanently Stuck When `totalKernelStaked` Drops to Zero Mid-Period - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool` guards against starting a reward period with zero stakers via a check in `notifyRewardAmount`, but provides no protection against all stakers withdrawing during an active reward period. When `totalKernelStaked` reaches zero mid-period, `rewardPerToken()` freezes while `updatedAt` advances on the next interaction, permanently losing all rewards emitted during the zero-staked window.

### Finding Description

The contract's own NatSpec comment explicitly acknowledges the risk:

> "If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards for that period will stay locked in the contract." [1](#0-0) 

The `notifyRewardAmount` function enforces `totalKernelStaked > 0` at the moment rewards are set: [2](#0-1) 

However, nothing prevents all stakers from withdrawing after `notifyRewardAmount` is called. When `totalKernelStaked == 0`, `rewardPerToken()` short-circuits and returns the stored value unchanged: [3](#0-2) 

Meanwhile, the `updateReward` modifier always advances `updatedAt` to `lastTimeRewardApplicable()` regardless of whether any tokens are staked: [4](#0-3) 

The combination means: when the first new staker arrives after a zero-staked gap, `rewardPerToken()` is called with `totalKernelStaked > 0` but `updatedAt` was already advanced to the moment of the last interaction (when `totalKernelStaked` was still 0). The time gap during which no one was staked is consumed without distributing any rewards, and those reward tokens remain permanently locked in the contract with no recovery mechanism.

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

Reward tokens transferred into the contract via `notifyRewardAmount` that correspond to any time window where `totalKernelStaked == 0` are irrecoverable. There is no admin sweep, no rescue function, and no mechanism to redistribute them. The loss is proportional to `rewardRate × (duration of zero-staked window)`.

### Likelihood Explanation

Realistic. Any staker can call `initiateWithdrawal` at any time. If the last remaining staker withdraws (or if all stakers coordinate to exit), `totalKernelStaked` drops to zero. The withdrawal delay (`withdrawalDelay`) only delays the token transfer, not the reduction of `totalKernelStaked` — `initiateWithdrawal` decrements `totalKernelStaked` immediately: [5](#0-4) 

This can happen naturally (all stakers exit) or be triggered deliberately by a single large staker who holds the majority of stake.

### Recommendation

Add a check in `initiateWithdrawal` (or a separate guard) that prevents `totalKernelStaked` from reaching zero while a reward period is active (`block.timestamp < finishAt`). Alternatively, implement a recovery function that allows the admin to reclaim unallocated rewards after a reward period ends, or track the "lost" reward window and redistribute it in the next period.

### Proof of Concept

1. Admin calls `setRewardsDuration(86400)` (1 day).
2. Alice stakes 1000 KERNEL tokens. `totalKernelStaked = 1000`.
3. Admin calls `notifyRewardAmount(86400e18)` — passes the `totalKernelStaked > 0` check. `rewardRate = 1e18/s`, `finishAt = T+86400`, `updatedAt = T`.
4. At `T+3600` (1 hour in), Alice calls `initiateWithdrawal(1000)`:
   - `updateReward(Alice)` runs: `rewardPerTokenStored` is updated, `updatedAt = T+3600`, Alice's earned rewards are checkpointed.
   - `totalKernelStaked = 0`.
5. From `T+3600` to `T+7200` (1 hour gap), no one stakes.
6. At `T+7200`, Bob stakes 1000 KERNEL:
   - `updateReward(Bob)` runs: `rewardPerToken()` sees `totalKernelStaked == 0` → returns `rewardPerTokenStored` unchanged. `updatedAt` is set to `T+7200`. Bob's `userRewardPerTokenPaid` is set to the current (unchanged) `rewardPerTokenStored`.
   - `totalKernelStaked = 1000`.
7. The 3600 seconds × 1e18/s = **3600e18 reward tokens** emitted between `T+3600` and `T+7200` are permanently stuck in the contract. Bob will only earn rewards from `T+7200` onward, and Alice already claimed hers up to `T+3600`.

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L18-22)
```text
 * @dev If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards
 *      for that period will stay locked in the contract. In this deployment, we're avoiding this issue by
 *      ensuring there are always some tokens staked before admin calls the `notifyRewardAmount` function,
 *      as well as for the entire duration of the reward period. Otherwise, staking just 1 wei by any address
 *      will ensure that the contract never has any unallocated rewards.
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L232-241)
```text
    modifier updateReward(address _account) {
        rewardPerTokenStored = rewardPerToken();
        updatedAt = lastTimeRewardApplicable();

        if (_account != address(0)) {
            rewards[_account] = earned(_account);
            userRewardPerTokenPaid[_account] = rewardPerTokenStored;
        }

        _;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L325-326)
```text
        balanceOf[msg.sender] -= _amount;
        totalKernelStaked -= _amount;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L408-413)
```text
    function rewardPerToken() public view returns (uint256) {
        if (totalKernelStaked == 0) {
            return rewardPerTokenStored;
        }
        return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
            / totalKernelStaked;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L569-570)
```text
        // Prevent starting a reward period when no tokens are staked to avoid unallocated rewards
        if (totalKernelStaked == 0) revert NoStakedTokens();
```
