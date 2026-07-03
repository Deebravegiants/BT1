### Title
Precision Loss in `rewardPerToken()` Causes Permanent Reward Loss When Low-Decimal Reward Tokens Are Used - (`contracts/KERNEL/KernelDepositPool.sol`)

### Summary

`KernelDepositPool.rewardPerToken()` can return zero increments for every `updateReward` call when the reward token has low decimals (e.g., USDC with 6 decimals) and `totalKernelStaked` is large. This causes all accrued rewards for those intervals to be permanently lost, never distributed to stakers.

### Finding Description

`notifyRewardAmount` stores `rewardRate` without any scaling factor:

```solidity
rewardRate = receivedAmount / duration;
```

`rewardPerToken()` then computes the per-token increment as:

```solidity
return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
    / totalKernelStaked;
``` [1](#0-0) 

When the reward token has 6 decimals (e.g., USDC), `rewardRate` is in units of `USDC_units / second`. For a realistic scenario:

- `receivedAmount = 1000 USDC = 1e9` (6 decimals)
- `duration = 30 days = 2,592,000 seconds`
- `rewardRate = 1e9 / 2,592,000 = 385` (USDC units/second)
- `totalKernelStaked = 1e24` (1 million KERNEL with 18 decimals)

For a `timeDelta` of 1 second:

```
rewardRate * timeDelta * DECIMAL_PRECISION / totalKernelStaked
= 385 * 1 * 1e18 / 1e24
= 385e18 / 1e24
= 0  (integer truncation)
```

The increment to `rewardPerTokenStored` is zero. The threshold `timeDelta` for a non-zero increment is:

```
timeDelta >= totalKernelStaked / (rewardRate * DECIMAL_PRECISION)
           = 1e24 / (385 * 1e18)
           ≈ 2,597 seconds (~43 minutes)
```

Every call to `updateReward` with `timeDelta < 43 minutes` permanently discards the rewards for that interval. The `updateReward` modifier fires on every `stake()`, `withdraw()`, and `getReward()` call. [2](#0-1) 

The `rewardRate` itself also suffers a first-order truncation at `notifyRewardAmount`:

```solidity
rewardRate = receivedAmount / duration;
``` [3](#0-2) 

For 1000 USDC over 30 days, `receivedAmount % duration = 1e9 % 2,592,000 = 1,280,000` micro-USDC ($1.28) is immediately lost. But the compounding precision loss in `rewardPerToken()` is far more severe.

### Impact Explanation

Rewards are permanently frozen in the contract — `rewardPerTokenStored` never increases for short-interval calls, so stakers can never claim those rewards. The reward tokens remain locked in the contract with no recovery path. This matches **Medium: Permanent freezing of unclaimed yield**.

In the worst case (frequent user interactions, large `totalKernelStaked`, low-decimal reward token), nearly all rewards for a distribution period can be permanently lost.

### Likelihood Explanation

- `KernelDepositPool` accepts an arbitrary `rewardsToken` at initialization; USDC is a natural choice for a staking rewards token.
- Any user can trigger `updateReward` by calling `stake(1 wei)` or `getReward()`, making frequent calls trivially achievable.
- With a large staking base (1M+ KERNEL), the threshold interval of ~43 minutes means normal user activity (multiple interactions per hour) is sufficient to trigger the loss without any deliberate attack. [4](#0-3) 

### Recommendation

Scale `rewardRate` by `DECIMAL_PRECISION` when storing it, and divide by `DECIMAL_PRECISION` when computing `rewardPerToken()`:

```solidity
// In notifyRewardAmount:
rewardRate = receivedAmount * DECIMAL_PRECISION / duration;

// In rewardPerToken():
return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt))
    / totalKernelStaked;

// In earned():
return (balanceOf[_account] * (rewardPerToken() - userRewardPerTokenPaid[_account]) / DECIMAL_PRECISION)
    + rewards[_account];
```

This mirrors the fix recommended in the external report (multiplying the numerator by `BASE_SCALE = 1e18` before division).

### Proof of Concept

1. Admin deploys `KernelDepositPool` with USDC (6 decimals) as `rewardsToken`.
2. 1,000,000 KERNEL (1e24 units) are staked by users.
3. Admin calls `notifyRewardAmount(1000e6)` (1000 USDC) with `duration = 30 days`.
   - `rewardRate = 1e9 / 2,592,000 = 385`
4. User A calls `stake(1 wei)` every 60 seconds (triggering `updateReward`).
   - Each call: `385 * 60 * 1e18 / 1e24 = 23,100e18 / 1e24 = 0`
   - `rewardPerTokenStored` never increases.
5. After 30 days, all stakers call `getReward()` and receive 0 rewards.
6. 1000 USDC remains permanently locked in the contract. [5](#0-4)

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
