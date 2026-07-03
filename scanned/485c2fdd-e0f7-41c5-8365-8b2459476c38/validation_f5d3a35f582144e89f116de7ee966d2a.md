### Title
Reward Rate Integer Division Truncation in `notifyRewardAmount` Causes Permanent Freezing of Unclaimed Yield - (File: contracts/KERNEL/KernelDepositPool.sol)

---

### Summary

In `KernelDepositPool.notifyRewardAmount`, `rewardRate` is computed as a plain integer division of `receivedAmount / duration` with no precision scaling applied at the rate-storage step. The remainder `receivedAmount % duration` is silently discarded and permanently locked in the contract on every reward notification, causing unclaimed yield to be frozen.

---

### Finding Description

`notifyRewardAmount` computes `rewardRate` as:

```solidity
// Line 580
rewardRate = receivedAmount / duration;

// Line 583 (mid-period top-up)
rewardRate = (receivedAmount + remaining) / duration;
```

`rewardRate` is stored as raw tokens-per-second with no precision multiplier. Solidity integer division truncates the result, so `receivedAmount % duration` tokens are transferred into the contract but never accounted for in `rewardRate`. They cannot be recovered by any function in the contract — there is no sweep, rescue, or remainder-return mechanism.

The `rewardPerToken()` function does apply `DECIMAL_PRECISION = 1e18` when accumulating rewards for stakers, but this scaling happens *after* the rate is already truncated:

```solidity
// Line 412-413
return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
    / totalKernelStaked;
```

The precision multiplier in `rewardPerToken()` does not recover the tokens lost to truncation in `rewardRate` — those tokens are already gone from the distributable pool.

The `rewardRate == 0` guard at line 586 only prevents the degenerate case where the entire amount is lost, but does nothing about the systematic per-call remainder loss.

---

### Impact Explanation

On every call to `notifyRewardAmount`, up to `duration - 1` wei of reward tokens are permanently frozen in the contract. For a 7-day duration (`604800` seconds), up to `604799` wei are stuck per call. For reward tokens with low decimals (e.g., 6-decimal USDC), this is up to ~0.6 USDC per call. Over many reward cycles, the cumulative stuck amount grows unboundedly. Stakers (reward claimants) receive less yield than was deposited, and the difference is irrecoverable.

**Impact class**: Medium — Permanent freezing of unclaimed yield.

---

### Likelihood Explanation

This truncation occurs on **every** invocation of `notifyRewardAmount`. No special conditions, attacker actions, or edge-case inputs are required. The admin calling the function as designed is sufficient to trigger the loss. The effect is deterministic and cumulative across all reward periods.

---

### Recommendation

Scale `rewardRate` by a precision factor (e.g., `1e18`) at storage time and divide by the same factor when computing `rewardPerToken`, matching the pattern already used in `rewardPerToken()`:

```solidity
// Store with precision
rewardRate = (receivedAmount * DECIMAL_PRECISION) / duration;

// rewardPerToken() then divides by DECIMAL_PRECISION (already done)
```

This eliminates the truncation loss entirely, as the remainder is now sub-wei after scaling.

---

### Proof of Concept

**Setup**:
- `duration = 604800` (7 days in seconds)
- Admin calls `notifyRewardAmount` with `_amount = 1_000_000` (e.g., 1 USDC, 6 decimals)

**Execution**:
```
receivedAmount = 1_000_000
rewardRate = 1_000_000 / 604_800 = 1  (truncated)
tokens distributed = 1 * 604_800 = 604_800
tokens stuck = 1_000_000 - 604_800 = 395_200  (≈ 0.395 USDC permanently frozen)
```

After `finishAt`, all stakers claim their rewards. The contract holds `395_200` wei of reward token with no mechanism to distribute or recover it. Repeating across 10 reward cycles freezes ~3.95 USDC with zero attacker involvement. [1](#0-0) [2](#0-1) [3](#0-2)

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L579-584)
```text
        if (block.timestamp >= finishAt) {
            rewardRate = receivedAmount / duration;
        } else {
            uint256 remaining = (finishAt - block.timestamp) * rewardRate;
            rewardRate = (receivedAmount + remaining) / duration;
        }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L586-586)
```text
        if (rewardRate == 0) revert RewardRateZero();
```
