### Title
Reward Accumulation Rounds to Zero in `KernelDepositPool` When `totalKernelStaked` Is Large Relative to `rewardRate` — (File: `contracts/KERNEL/KernelDepositPool.sol`)

---

### Summary

`KernelDepositPool` implements a Synthetix-style staking rewards mechanism. The `rewardPerToken()` increment — `rewardRate * timeDelta * DECIMAL_PRECISION / totalKernelStaked` — can silently round down to zero when `totalKernelStaked` is large relative to `rewardRate`. Because the `updateReward` modifier always advances `updatedAt` regardless of whether any reward actually accumulated, the rewards for those time windows are permanently unclaimable. An unprivileged staker can deliberately trigger this by calling `stake(1)` repeatedly to force small `timeDelta` values.

---

### Finding Description

`KernelDepositPool` uses `DECIMAL_PRECISION = 1e18` and computes the global reward accumulator as:

```solidity
// contracts/KERNEL/KernelDepositPool.sol L412-413
return rewardPerTokenStored
    + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
    / totalKernelStaked;
``` [1](#0-0) 

The `updateReward` modifier, applied to every state-changing user function, always snapshots `updatedAt = lastTimeRewardApplicable()`:

```solidity
// contracts/KERNEL/KernelDepositPool.sol L232-242
modifier updateReward(address _account) {
    rewardPerTokenStored = rewardPerToken();
    updatedAt = lastTimeRewardApplicable();
    ...
}
``` [2](#0-1) 

If the increment `rewardRate * timeDelta * 1e18 / totalKernelStaked` rounds to zero, `rewardPerTokenStored` is unchanged but `updatedAt` is advanced. The rewards that should have accrued during `timeDelta` are permanently discarded — there is no mechanism to recover them.

A second, independent precision loss occurs in `notifyRewardAmount`:

```solidity
// contracts/KERNEL/KernelDepositPool.sol L580
rewardRate = receivedAmount / duration;
``` [3](#0-2) 

The remainder `receivedAmount % duration` is permanently stranded in the contract. For a low-decimal reward token (e.g., USDC at 6 decimals) with a 30-day duration, this is up to `2,591,999` USDC wei (~2.59 USDC) per reward period, with no recovery path.

---

### Impact Explanation

**Impact: Medium — Permanent freezing of unclaimed yield.**

Rewards that should be distributed to stakers are silently discarded:

1. **`notifyRewardAmount` truncation**: `receivedAmount % duration` tokens are permanently locked in the contract every reward period. For a 6-decimal reward token over a 30-day window, this is up to ~2.59 tokens per period, compounding across multiple periods.

2. **`rewardPerToken()` rounding to zero**: When `rewardRate * timeDelta * 1e18 < totalKernelStaked`, the per-token accumulator does not advance for that window. Stakers receive zero rewards for that period even though `rewardRate > 0` and tokens are present in the contract.

Both losses are permanent — there is no admin function to redistribute stranded rewards to stakers.

---

### Likelihood Explanation

**Likelihood: Medium.**

The rounding-to-zero condition `rewardRate * timeDelta * 1e18 < totalKernelStaked` is reachable under realistic conditions:

- If the reward token has 6 decimals (e.g., USDC) and 1,000 USDC is distributed over 30 days: `rewardRate = 1,000e6 / 2,592,000 = 385` (wei/second).
- For the per-second increment to round to zero: `385 * 1 * 1e18 < totalKernelStaked` → `totalKernelStaked > 3.85e20`, i.e., more than 385 KERNEL tokens staked.
- For the per-100-second increment to round to zero: `totalKernelStaked > 3.85e22`, i.e., more than 38,500 KERNEL tokens staked.

These are realistic staking levels for a live protocol. Additionally, any holder of KERNEL tokens can call `stake(1)` repeatedly to force `timeDelta = 1` second per call, deliberately triggering the rounding-to-zero condition as a griefing attack — directly analogous to the external report's `updateFarm` griefing vector.

The `notifyRewardAmount` truncation is unconditional and occurs on every reward period regardless of attacker action.

---

### Recommendation

1. **For `notifyRewardAmount` truncation**: Track the undistributed remainder and roll it into the next reward period:
   ```solidity
   uint256 leftover = rewardRate * (finishAt - block.timestamp); // if active
   rewardRate = (receivedAmount + leftover) / duration;
   // store remainder: undistributed = (receivedAmount + leftover) % duration
   ```
   This is the standard fix used in audited Synthetix forks.

2. **For `rewardPerToken()` rounding**: Use a higher internal precision multiplier (e.g., `1e36` instead of `1e18`) for the accumulator, scaling back down only in `earned()`. Alternatively, enforce a minimum `rewardRate` relative to `totalKernelStaked` in `notifyRewardAmount` to guarantee the per-second increment is always non-zero.

3. **Restrict reward token decimals**: Add a check in `initialize` that the reward token has at least 18 decimals, or document and enforce this invariant operationally.

---

### Proof of Concept

**Scenario**: USDC (6 decimals) as reward token, 1,000 USDC distributed over 30 days, 1,000,000 KERNEL tokens staked.

```
rewardRate = 1_000e6 / 2_592_000 = 385 (wei/second, truncated)
Stranded from truncation = 1_000e6 - 385 * 2_592_000 = 1_888_000 USDC wei ≈ 1.888 USDC (permanent)

Per-second rewardPerToken increment:
= 385 * 1 * 1e18 / 1_000_000e18
= 385e18 / 1e24
= 3.85e-4 → rounds to 0

Attack:
1. Attacker holds KERNEL tokens and calls stake(1) once per second.
2. Each call triggers updateReward: updatedAt advances by 1 second, but rewardPerTokenStored is unchanged.
3. Over 1 hour (3,600 calls): 3,600 seconds of rewards are permanently lost.
4. Lost rewards = rewardRate * 3600 = 385 * 3600 = 1,386,000 USDC wei ≈ 1.386 USDC per hour of griefing.
5. These rewards remain in the contract but are unclaimable by any staker.
``` [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L232-242)
```text
    modifier updateReward(address _account) {
        rewardPerTokenStored = rewardPerToken();
        updatedAt = lastTimeRewardApplicable();

        if (_account != address(0)) {
            rewards[_account] = earned(_account);
            userRewardPerTokenPaid[_account] = rewardPerTokenStored;
        }

        _;
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L281-289)
```text
    function stake(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();

        balanceOf[msg.sender] += _amount;
        totalKernelStaked += _amount;
        kernelToken.safeTransferFrom(msg.sender, address(this), _amount);

        emit Staked(msg.sender, _amount);
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L566-592)
```text
    function notifyRewardAmount(uint256 _amount) external onlyRole(DEFAULT_ADMIN_ROLE) updateReward(address(0)) {
        if (_amount == 0) revert AmountZero();

        // Prevent starting a reward period when no tokens are staked to avoid unallocated rewards
        if (totalKernelStaked == 0) revert NoStakedTokens();

        // Transfer reward tokens into the contract
        uint256 balanceBefore = rewardsToken.balanceOf(address(this));
        rewardsToken.safeTransferFrom(msg.sender, address(this), _amount);
        uint256 balanceAfter = rewardsToken.balanceOf(address(this));
        // Calculate the actual amount of tokens received in case of a transfer fee (tax)
        uint256 receivedAmount = balanceAfter - balanceBefore;

        if (block.timestamp >= finishAt) {
            rewardRate = receivedAmount / duration;
        } else {
            uint256 remaining = (finishAt - block.timestamp) * rewardRate;
            rewardRate = (receivedAmount + remaining) / duration;
        }

        if (rewardRate == 0) revert RewardRateZero();

        finishAt = block.timestamp + duration;
        updatedAt = block.timestamp;

        emit NotifyRewardAmount(receivedAmount, finishAt);
    }
```
