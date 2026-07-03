### Title
Rewards Permanently Stuck in `KernelDepositPool` When `totalKernelStaked` Drops to Zero During Active Reward Period - (File: contracts/KERNEL/KernelDepositPool.sol)

---

### Summary

`KernelDepositPool` implements a Synthetix-style staking rewards mechanism. When `totalKernelStaked` reaches zero during an active reward distribution window, the reward tokens that should have been distributed during that empty period are permanently locked in the contract. There is no admin recovery function to reclaim them.

---

### Finding Description

The contract's own NatSpec explicitly acknowledges the issue:

> *"If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards for that period will stay locked in the contract."* [1](#0-0) 

The root cause is in `rewardPerToken()`:

```solidity
function rewardPerToken() public view returns (uint256) {
    if (totalKernelStaked == 0) {
        return rewardPerTokenStored;
    }
    return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
        / totalKernelStaked;
}
``` [2](#0-1) 

When `totalKernelStaked == 0`, `rewardPerTokenStored` is returned unchanged. The `updateReward` modifier, however, always advances `updatedAt` to `lastTimeRewardApplicable()`:

```solidity
modifier updateReward(address _account) {
    rewardPerTokenStored = rewardPerToken();
    updatedAt = lastTimeRewardApplicable();
    ...
}
``` [3](#0-2) 

**Step-by-step mechanics of the loss:**

1. At time `T1`, all stakers call `initiateWithdrawal`, reducing `totalKernelStaked` to 0. `updatedAt = T1`, `rewardPerTokenStored = X`.
2. During `[T1, T2]`, `rewardRate` continues to emit rewards (the `finishAt` timestamp is unchanged), but since `totalKernelStaked == 0`, `rewardPerToken()` always returns `X`.
3. At time `T2`, a new staker calls `stake()`, triggering `updateReward`:
   - `rewardPerTokenStored = rewardPerToken() = X` (no change, because `totalKernelStaked` was 0 at the time of the call — it is updated *after* the modifier runs)
   - `updatedAt = T2`
4. The rewards for the period `[T1, T2]` — equal to `rewardRate × (T2 − T1)` — are permanently unaccounted for. No user can ever claim them, and there is no admin sweep function.

`notifyRewardAmount` guards against starting a reward period with zero stakers:

```solidity
if (totalKernelStaked == 0) revert NoStakedTokens();
``` [4](#0-3) 

But this guard only applies at the moment of reward notification. It does not prevent all stakers from withdrawing *after* the reward period has started, which is the actual vulnerable path.

Critically, `KernelDepositPool` has **no `withdrawTokens` or emergency sweep function** for the admin to recover stranded reward tokens. The entire contract has no such mechanism, unlike `KernelTop100MerkleDistributor` which does include `withdrawTokens`. [5](#0-4) 

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

Any reward tokens that accrue during a period where `totalKernelStaked == 0` are permanently locked in the contract. They cannot be claimed by any user (no staker was present to earn them) and cannot be recovered by the admin (no sweep function exists). The magnitude of loss equals `rewardRate × duration_of_empty_period`.

---

### Likelihood Explanation

**Low-Medium.** The scenario requires `totalKernelStaked` to reach exactly zero during an active reward window. This can happen if:
- A single large staker (or the last remaining staker) calls `initiateWithdrawal`, reducing `totalKernelStaked` to 0.
- A coordinated exit by multiple stakers occurs simultaneously.

The contract's own comment acknowledges this is a known risk and relies purely on the operational assumption that "there are always some tokens staked." There is no on-chain enforcement of this invariant after `notifyRewardAmount` is called. Any unprivileged staker can trigger this by being the last to withdraw.

---

### Recommendation

1. **Add an admin recovery function** to sweep undistributed reward tokens back to the treasury when the reward period has ended and `totalKernelStaked` is zero, analogous to `withdrawTokens` in `KernelTop100MerkleDistributor`.
2. **Alternatively**, when `totalKernelStaked == 0` is detected inside `updateReward`, freeze `updatedAt` (do not advance it) so that rewards for the empty period are preserved and can be distributed once staking resumes. This is the standard fix for this class of Synthetix fork bug.

---

### Proof of Concept

```
Setup:
  - rewardRate = 100 tokens/second
  - duration = 1000 seconds (finishAt = T0 + 1000)
  - Alice stakes 1000 KERNEL at T0

At T0 + 100:
  - Alice calls initiateWithdrawal(1000)
  - totalKernelStaked = 0
  - updatedAt = T0 + 100

At T0 + 600 (500 seconds later):
  - Bob calls stake(1 wei)
  - updateReward fires:
      rewardPerToken() → returns rewardPerTokenStored (unchanged, totalKernelStaked was 0)
      updatedAt = T0 + 600

Rewards for [T0+100, T0+600] = 100 * 500 = 50,000 tokens
→ These 50,000 tokens are permanently stuck in KernelDepositPool.
→ No function exists to recover them.
```

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L17-23)
```text
 * @dev Modified from https://github.com/Synthetixio/synthetix/blob/develop/contracts/StakingRewards.sol
 * @dev If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards
 *      for that period will stay locked in the contract. In this deployment, we're avoiding this issue by
 *      ensuring there are always some tokens staked before admin calls the `notifyRewardAmount` function,
 *      as well as for the entire duration of the reward period. Otherwise, staking just 1 wei by any address
 *      will ensure that the contract never has any unallocated rewards.
 */
```

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L544-621)
```text
    /*//////////////////////////////////////////////////////////////
                            ADMIN FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /**
     * @notice Sets the duration for rewards distribution
     * @param _duration The duration in seconds
     */
    function setRewardsDuration(uint256 _duration) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (finishAt >= block.timestamp) revert RewardDurationNotFinished();
        if (_duration == 0) revert InvalidDuration();
        duration = _duration;
        emit RewardsDurationUpdated(_duration);
    }

    /**
     * @notice Notifies the contract about a new reward amount
     * @dev Uses a transfer-in pattern to determine the exact reward amount received.
     *      Also, to avoid undistributed rewards when no one is staked, this function reverts if totalKernelStaked is
     *      zero.
     * @param _amount The amount of reward tokens to add
     */
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

    /**
     * @notice Updates the withdrawal delay
     * @param _withdrawalDelay The new withdrawal delay
     */
    function setWithdrawalDelay(uint256 _withdrawalDelay) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_withdrawalDelay == 0) revert InvalidWithdrawalDelay();
        if (_withdrawalDelay > MAX_WITHDRAWAL_DELAY) revert MaximumWithdrawalDelayExceeded();

        withdrawalDelay = _withdrawalDelay;
        emit WithdrawalDelayUpdated(_withdrawalDelay);
    }

    /**
     * @notice Updates the maximum number of withdrawals per user
     * @param _maxNumberOfWithdrawalsPerUser The new maximum number of withdrawals per user
     */
    function setMaxNumberOfWithdrawalsPerUser(uint256 _maxNumberOfWithdrawalsPerUser)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        if (_maxNumberOfWithdrawalsPerUser == 0 || _maxNumberOfWithdrawalsPerUser > MAX_WITHDRAWALS_PER_USER) {
            revert InvalidMaxNumberOfWithdrawalsPerUser();
        }

        maxNumberOfWithdrawalsPerUser = _maxNumberOfWithdrawalsPerUser;
        emit MaxNumberOfWithdrawalsPerUserUpdated(_maxNumberOfWithdrawalsPerUser);
    }
}
```
