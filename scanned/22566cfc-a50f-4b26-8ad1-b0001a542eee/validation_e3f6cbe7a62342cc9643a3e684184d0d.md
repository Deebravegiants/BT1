### Title
Divide-Before-Multiply Precision Loss in `notifyRewardAmount()` Permanently Freezes Unclaimed Yield - (`contracts/KERNEL/KernelDepositPool.sol`)

### Summary
`KernelDepositPool.notifyRewardAmount()` computes `rewardRate` via integer division before that rate is later multiplied by elapsed time. The truncated remainder (`receivedAmount % duration`) is permanently locked in the contract and never distributed to stakers, constituting a permanent freezing of unclaimed yield.

### Finding Description
In `notifyRewardAmount()`, the per-second reward rate is computed as:

```solidity
rewardRate = receivedAmount / duration;          // line 580
// or, for mid-period top-ups:
rewardRate = (receivedAmount + remaining) / duration;  // line 583
``` [1](#0-0) 

Due to Solidity integer truncation, `receivedAmount % duration` reward tokens are silently discarded from the rate. These tokens remain in the contract balance but are never accounted for in `rewardPerToken()` or `earned()`, so no staker can ever claim them.

The downstream accumulation in `rewardPerToken()` then multiplies the already-truncated `rewardRate`:

```solidity
return rewardPerTokenStored
    + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
    / totalKernelStaked;
``` [2](#0-1) 

The pattern is: **divide first** (`receivedAmount / duration` → `rewardRate`), **then multiply** (`rewardRate * elapsed`). This is the same divide-then-multiply ordering as the referenced vulnerability. The lost amount per period is `receivedAmount % duration` tokens, which is permanently irrecoverable because the contract has no sweep or recovery function for the `rewardsToken`.

For the rollover case (line 582–583), the compounding is worse: `remaining` is itself derived from the already-truncated `rewardRate`, so the new `rewardRate` is truncated a second time on top of an already-imprecise base. [3](#0-2) 

### Impact Explanation
**Medium — Permanent freezing of unclaimed yield.**

Every call to `notifyRewardAmount()` silently discards `receivedAmount % duration` reward tokens into the contract with no recovery path. For a 7-day period (`duration = 604800 s`) and a 6-decimal reward token (e.g., USDC), the maximum loss per period is `604799 / 1e6 ≈ 0.60 USDC`. Over many reward periods and with larger reward amounts or lower-decimal tokens, the cumulative locked amount grows monotonically. There is no admin sweep function for `rewardsToken` in the contract.

### Likelihood Explanation
**High.** The truncation occurs on virtually every call to `notifyRewardAmount()` because reward amounts are almost never perfectly divisible by `duration` in seconds. The function is called by the admin at the start of each reward period, making this a near-certain, recurring loss.

### Recommendation
Scale `rewardRate` by `DECIMAL_PRECISION` (1e18) at storage time and divide by it when computing `rewardPerToken`, reducing the per-period truncation loss from up to `duration - 1` raw token units to at most `duration - 1` wei of the scaled representation:

```solidity
// Store rate scaled by 1e18
rewardRate = (receivedAmount * DECIMAL_PRECISION) / duration;

// In rewardPerToken(), remove the extra DECIMAL_PRECISION multiplication:
return rewardPerTokenStored
    + (rewardRate * (lastTimeRewardApplicable() - updatedAt))
    / totalKernelStaked;
```

Alternatively, track the undistributed remainder and roll it into the next `notifyRewardAmount()` call.

### Proof of Concept
**Setup:** `duration = 7 days = 604800 seconds`, `rewardsToken` is a 6-decimal token, admin calls `notifyRewardAmount` with `1000e6` (1000 USDC).

```
receivedAmount = 1_000_000_000   (1000 USDC in raw units)
rewardRate     = 1_000_000_000 / 604_800 = 1653   (truncated)

Total distributed over full period:
  1653 * 604_800 = 999_734_400 units = 999.7344 USDC

Permanently locked:
  1_000_000_000 - 999_734_400 = 265_600 units = 0.2656 USDC per period
```

After 100 reward periods, 26.56 USDC is permanently frozen in the contract. The `getReward()` function only transfers `rewards[msg.sender]`, which is derived from the truncated `rewardRate`, so no user can ever recover the locked remainder. [4](#0-3)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L382-390)
```text
    function getReward() external nonReentrant updateReward(msg.sender) {
        uint256 rewardAmount = rewards[msg.sender];

        if (rewardAmount > 0) {
            rewards[msg.sender] = 0;
            rewardsToken.safeTransfer(msg.sender, rewardAmount);
            emit RewardsClaimed(msg.sender, rewardAmount);
        }
    }
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L579-584)
```text
        if (block.timestamp >= finishAt) {
            rewardRate = receivedAmount / duration;
        } else {
            uint256 remaining = (finishAt - block.timestamp) * rewardRate;
            rewardRate = (receivedAmount + remaining) / duration;
        }
```
