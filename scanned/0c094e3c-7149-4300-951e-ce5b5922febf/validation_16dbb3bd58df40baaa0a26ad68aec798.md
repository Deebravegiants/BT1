### Title
Truncated `rewardRate` in `notifyRewardAmount` permanently freezes unclaimed yield - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool.notifyRewardAmount` computes `rewardRate` via integer division (`receivedAmount / duration`), discarding the remainder. That truncated remainder is never distributed to stakers and is permanently locked in the contract. This is the direct analog of the reported "multiplication on result of division" precision-loss pattern: a division is performed first, and the truncated quotient is then multiplied in downstream reward accounting, compounding the loss.

### Finding Description
In `notifyRewardAmount`, the reward rate is set as:

```solidity
rewardRate = receivedAmount / duration;          // line 580
```

and for mid-period top-ups:

```solidity
uint256 remaining = (finishAt - block.timestamp) * rewardRate;
rewardRate = (receivedAmount + remaining) / duration;  // line 583
```

Both paths perform integer division that truncates `receivedAmount % duration` tokens. The truncated dust is never accounted for in any subsequent calculation and stays locked in the contract forever.

`rewardRate` is then used in `rewardPerToken()`:

```solidity
return rewardPerTokenStored
    + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
    / totalKernelStaked;                          // lines 412-413
```

This is the classic "divide first, multiply later" pattern: the division in `notifyRewardAmount` truncates the rate, and every subsequent multiplication in `rewardPerToken` propagates the under-counted value to all stakers. The `earned()` function then uses this under-counted `rewardPerToken` to compute each user's claimable amount:

```solidity
return (balanceOf[_account] * (rewardPerToken() - userRewardPerTokenPaid[_account]) / DECIMAL_PRECISION)
    + rewards[_account];                          // lines 422-423
```

The `receivedAmount % duration` tokens are permanently irrecoverable — there is no sweep or recovery function for the contract's reward token balance.

### Impact Explanation
Every call to `notifyRewardAmount` permanently freezes up to `duration - 1` wei of reward tokens. For the default 7-day duration (`604800` seconds), up to `604799` wei are lost per period. Over many reward periods this accumulates. Mid-period top-ups compound the loss because `remaining` is already computed from a truncated `rewardRate`, and the new rate is truncated again. The frozen tokens sit in the contract's `rewardsToken` balance with no mechanism to recover them.

**Impact class:** Medium — Permanent freezing of unclaimed yield.

### Likelihood Explanation
This is triggered unconditionally on every `notifyRewardAmount` call whenever `receivedAmount` is not an exact multiple of `duration`. Any staker who calls `getReward()` receives a slightly smaller amount than they are entitled to. No special conditions, attacker actions, or privileged compromise are required — the loss occurs automatically as part of normal protocol operation.

### Recommendation
Scale `rewardRate` by `DECIMAL_PRECISION` before dividing, then divide by `DECIMAL_PRECISION` when consuming it, so the remainder is preserved in the rate rather than discarded:

```diff
- rewardRate = receivedAmount / duration;
+ rewardRate = (receivedAmount * DECIMAL_PRECISION) / duration;
```

and adjust `rewardPerToken` accordingly:

```diff
- return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
-     / totalKernelStaked;
+ return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt))
+     / totalKernelStaked;
```

Alternatively, track the undistributed dust and roll it into the next reward period.

### Proof of Concept
```solidity
// Concrete numbers showing the loss
uint256 duration      = 7 days;          // 604800 seconds
uint256 receivedAmount = 1_000e18;       // 1000 reward tokens

// Current code
uint256 rewardRate = receivedAmount / duration;
// rewardRate = 1_000e18 / 604800 = 1_653_439_153_439_153 (truncated)

uint256 totalDistributed = rewardRate * duration;
// = 1_653_439_153_439_153 * 604800 = 999_999_999_999_999_974_400

uint256 permanentlyFrozen = receivedAmount - totalDistributed;
// = 1_000e18 - 999_999_999_999_999_974_400 = 25_600 wei per period

// Mid-period top-up compounds the loss:
// remaining = (finishAt - block.timestamp) * rewardRate  (already truncated)
// new rewardRate = (receivedAmount + remaining) / duration  (truncated again)
```

Over 52 weekly reward periods, `52 * 25_600 = 1_331_200` wei of reward tokens are permanently frozen. With higher-value tokens or shorter durations the absolute loss scales proportionally. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

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
