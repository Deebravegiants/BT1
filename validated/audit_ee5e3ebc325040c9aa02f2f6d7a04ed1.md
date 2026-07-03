### Title
Premature Division in `notifyRewardAmount` Permanently Locks Reward Tokens - (File: `contracts/KERNEL/KernelDepositPool.sol`)

---

### Summary

`KernelDepositPool::notifyRewardAmount` divides `receivedAmount` by `duration` to compute `rewardRate` before any subsequent multiplication. The integer truncation discards `receivedAmount % duration` tokens every reward period. Those tokens remain in the contract balance permanently with no recovery path, constituting a systematic permanent freeze of unclaimed yield for every staker.

---

### Finding Description

`notifyRewardAmount` sets the per-second reward rate as:

```solidity
// contracts/KERNEL/KernelDepositPool.sol line 580
rewardRate = receivedAmount / duration;
```

Integer division truncates the result. The total tokens that will ever be emitted over the full period is `rewardRate * duration = (receivedAmount / duration) * duration`, which is strictly less than `receivedAmount` whenever `receivedAmount % duration != 0`. The remainder `receivedAmount % duration` is added to the contract's `rewardsToken` balance by the `safeTransferFrom` call on line 574 but is never accounted for in any distribution variable (`rewardRate`, `rewardPerTokenStored`, `rewards`). No sweep or recovery function exists.

The same truncation compounds when a period is extended before expiry:

```solidity
// contracts/KERNEL/KernelDepositPool.sol lines 582-583
uint256 remaining = (finishAt - block.timestamp) * rewardRate;
rewardRate = (receivedAmount + remaining) / duration;
```

`remaining` is computed from the already-truncated `rewardRate`, so the undercount from the previous period is baked into the new rate, and a second truncation occurs on the combined sum.

The downstream `rewardPerToken` and `earned` functions multiply by the truncated `rewardRate`, so every staker's claimable balance is computed from the reduced rate:

```solidity
// contracts/KERNEL/KernelDepositPool.sol lines 412-413
return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
    / totalKernelStaked;
```

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

The locked amount per call is `receivedAmount % duration` tokens. For an 18-decimal reward token this is at most `duration − 1` wei per period (negligible in isolation), but:

1. It accumulates across every `notifyRewardAmount` call with no bound on the number of periods.
2. For reward tokens with fewer decimals (e.g., 6-decimal USDC-style tokens), the loss is material. Example: `receivedAmount = 1,000,000` (1 token, 6 decimals), `duration = 604,800` (7 days) → `rewardRate = 1`, distributed = `604,800`, **permanently locked = 395,200 (≈ 39.5% of the reward)**.
3. The locked tokens are irrecoverable — there is no admin sweep, no `rescueTokens`, and no mechanism to roll the remainder into the next period.

---

### Likelihood Explanation

**High.** The truncation occurs unconditionally on every invocation of `notifyRewardAmount`. The function is callable by `DEFAULT_ADMIN_ROLE` and is the normal operational path for funding reward periods. No special conditions are required; the loss is deterministic.

---

### Recommendation

Accumulate the undistributed remainder and roll it into the next period, or use a higher-precision intermediate:

```diff
// contracts/KERNEL/KernelDepositPool.sol
if (block.timestamp >= finishAt) {
-   rewardRate = receivedAmount / duration;
+   rewardRate = receivedAmount / duration;
+   // roll dust into next period by tracking it explicitly, or:
+   // use: rewardRate = receivedAmount / duration (keep remainder in a `dustAccumulator`)
} else {
    uint256 remaining = (finishAt - block.timestamp) * rewardRate;
-   rewardRate = (receivedAmount + remaining) / duration;
+   rewardRate = (receivedAmount + remaining) / duration;
}
```

The cleanest fix is to track `undistributedRewards` and add it to `receivedAmount` on the next `notifyRewardAmount` call, ensuring no tokens are ever stranded.

---

### Proof of Concept

Scenario with a 6-decimal reward token:

```
duration        = 604_800  (7 days in seconds)
receivedAmount  = 1_000_000 (1.000000 tokens, 6 decimals)

rewardRate      = 1_000_000 / 604_800 = 1 (truncated from 1.6534...)
total emitted   = 1 * 604_800         = 604_800
permanently locked = 1_000_000 - 604_800 = 395_200  (~39.5% of rewards)
```

For an 18-decimal token the per-period loss is at most `duration − 1` wei, but across N periods the cumulative locked amount is `N * (receivedAmount_i % duration)` with no recovery path. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L14-22)
```text
/**
 * @title Kernel Staking Rewards Contract
 * @dev Implements a basic staking mechanism with rewards
 * @dev Modified from https://github.com/Synthetixio/synthetix/blob/develop/contracts/StakingRewards.sol
 * @dev If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards
 *      for that period will stay locked in the contract. In this deployment, we're avoiding this issue by
 *      ensuring there are always some tokens staked before admin calls the `notifyRewardAmount` function,
 *      as well as for the entire duration of the reward period. Otherwise, staking just 1 wei by any address
 *      will ensure that the contract never has any unallocated rewards.
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L408-414)
```text
    function rewardPerToken() public view returns (uint256) {
        if (totalKernelStaked == 0) {
            return rewardPerTokenStored;
        }
        return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
            / totalKernelStaked;
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L421-424)
```text
    function earned(address _account) public view returns (uint256) {
        return (balanceOf[_account] * (rewardPerToken() - userRewardPerTokenPaid[_account]) / DECIMAL_PRECISION)
            + rewards[_account];
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L579-584)
```text
        if (block.timestamp >= finishAt) {
            rewardRate = receivedAmount / duration;
        } else {
            uint256 remaining = (finishAt - block.timestamp) * rewardRate;
            rewardRate = (receivedAmount + remaining) / duration;
        }
```
