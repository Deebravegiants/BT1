### Title
Precision Loss in `notifyRewardAmount` Permanently Locks Reward Dust in Contract - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary

`KernelDepositPool.notifyRewardAmount` computes `rewardRate` via integer division of `receivedAmount / duration`. The truncated remainder (`receivedAmount % duration`) is transferred into the contract but can never be distributed to stakers, permanently locking it. This is the same vulnerability class as H-01: precision loss in a time-based reward rate calculation causing the actual rewards delivered to differ from the amount deposited.

### Finding Description

In `notifyRewardAmount`, the reward rate is set as:

```solidity
// Line 580
rewardRate = receivedAmount / duration;
```

and for mid-period top-ups:

```solidity
// Lines 582-583
uint256 remaining = (finishAt - block.timestamp) * rewardRate;
rewardRate = (receivedAmount + remaining) / duration;
```

Both branches perform integer division, truncating the fractional part. The truncated dust — `receivedAmount % duration` in the fresh-period case, and `(receivedAmount + remaining) % duration` in the mid-period case — is transferred into the contract by the `safeTransferFrom` call at line 574 but is never accounted for in any subsequent distribution. Because `rewardRate` is the sole mechanism by which tokens flow out to stakers (via `rewardPerToken` → `earned` → `getReward`), and `rewardRate` is always set strictly below the true per-second rate, the dust is irrecoverable.

There is no sweep, rescue, or residual-distribution function in the contract.

### Impact Explanation

Every call to `notifyRewardAmount` permanently locks up to `duration - 1` wei of the reward token. Over repeated reward top-ups across the lifetime of the pool, this dust accumulates. Stakers collectively receive fewer rewards than the total amount deposited by the admin. The locked tokens cannot be recovered by any party.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

### Likelihood Explanation

`notifyRewardAmount` is an admin-only function, but it is a routine operational call expected to be invoked repeatedly (once per reward period or more). Every single invocation silently discards dust. The likelihood of this occurring is **certain** — it happens on every call by design of integer arithmetic.

### Recommendation

Track the undistributed dust and either:
1. Roll it into the next reward period by adding it to `receivedAmount` in the next `notifyRewardAmount` call, or
2. Use a higher-precision intermediate (e.g., scale `rewardRate` by `1e18` and divide at distribution time), consistent with how `rewardPerToken` already uses `DECIMAL_PRECISION`.

A minimal fix for the fresh-period case:

```solidity
// Instead of:
rewardRate = receivedAmount / duration;

// Track leftover and include it next time:
uint256 leftover = receivedAmount % duration;
rewardRate = (receivedAmount - leftover) / duration;
// store leftover to be added to next receivedAmount
```

### Proof of Concept

**Setup:** `duration = 604800` (7 days in seconds), admin calls `notifyRewardAmount` with `receivedAmount = 1_000_000e18`.

**Step 1 — Rate computation:**
```
rewardRate = 1_000_000e18 / 604800
           = 1_653_439_153_439_153_439  (truncated)
```

**Step 2 — Total distributed over full period:**
```
distributed = rewardRate * duration
            = 1_653_439_153_439_153_439 * 604800
            = 999_999_999_999_999_744_000_000_000_000  (< 1_000_000e18)
```

**Step 3 — Dust permanently locked:**
```
dust = 1_000_000e18 - distributed = 256_000_000_000_000  (~256 wei at 1e18 scale)
```

Per call the dust is small, but with `N` calls over the pool's lifetime the total locked amount is `N * (duration - 1)` wei at worst. There is no mechanism to recover or redistribute this amount. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L408-413)
```text
    function rewardPerToken() public view returns (uint256) {
        if (totalKernelStaked == 0) {
            return rewardPerTokenStored;
        }
        return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
            / totalKernelStaked;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L572-577)
```text
        // Transfer reward tokens into the contract
        uint256 balanceBefore = rewardsToken.balanceOf(address(this));
        rewardsToken.safeTransferFrom(msg.sender, address(this), _amount);
        uint256 balanceAfter = rewardsToken.balanceOf(address(this));
        // Calculate the actual amount of tokens received in case of a transfer fee (tax)
        uint256 receivedAmount = balanceAfter - balanceBefore;
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
