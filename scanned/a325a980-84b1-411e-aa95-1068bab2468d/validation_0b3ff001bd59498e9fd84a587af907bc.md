### Title
Reward Tokens Permanently Locked in KernelDepositPool When `totalKernelStaked` Drops to Zero During Active Reward Period - (File: contracts/KERNEL/KernelDepositPool.sol)

---

### Summary

In `KernelDepositPool`, if all stakers withdraw their tokens during an active reward distribution window, `totalKernelStaked` drops to zero. The `rewardPerToken()` function returns `rewardPerTokenStored` unchanged when `totalKernelStaked == 0`, meaning rewards that continue to accrue at `rewardRate` are never distributed to anyone and become permanently locked in the contract. There is no admin sweep or recovery function for these stranded reward tokens.

---

### Finding Description

`KernelDepositPool` implements a Synthetix-style staking rewards mechanism. The `rewardPerToken()` function short-circuits when `totalKernelStaked == 0`: [1](#0-0) 

When `totalKernelStaked == 0`, `rewardPerTokenStored` is never incremented, so all reward tokens that should have been distributed during that zero-staked interval are silently absorbed into the contract balance with no recipient. The `initiateWithdrawal` function immediately reduces `totalKernelStaked` at the moment of call, before the withdrawal delay elapses: [2](#0-1) 

This means a staker (or the last remaining staker) can call `initiateWithdrawal` for their full balance during an active reward period, driving `totalKernelStaked` to zero and permanently locking all remaining rewards for that period.

The contract's own NatSpec comment explicitly acknowledges this design gap: [3](#0-2) 

The partial mitigation added to `notifyRewardAmount` — reverting when `totalKernelStaked == 0` — only prevents *starting* a new reward period with no stakers. It does not prevent stakers from withdrawing *during* an already-active period: [4](#0-3) 

There is no `sweep`, `recoverERC20`, or equivalent admin function in `KernelDepositPool` to rescue stranded reward tokens. The admin functions are limited to `setRewardsDuration`, `notifyRewardAmount`, `setWithdrawalDelay`, and `setMaxNumberOfWithdrawalsPerUser` — none of which can recover locked rewards. [5](#0-4) 

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

Reward tokens deposited by the admin via `notifyRewardAmount` are permanently locked in the contract for the portion of the reward period during which `totalKernelStaked == 0`. The admin cannot restart a new reward period (reverts with `NoStakedTokens`), and no recovery path exists. The locked tokens are irrecoverable without a contract upgrade.

---

### Likelihood Explanation

**Low.** The scenario requires `totalKernelStaked` to reach exactly zero during an active reward window. This is most realistic when there is a single dominant staker (or a small coordinated group) who withdraws all tokens immediately after `notifyRewardAmount` is called. The attacker sacrifices their own rewards for the remaining period, making this primarily a griefing vector against the protocol's reward budget rather than a direct profit-taking exploit. However, the code provides no on-chain enforcement to prevent it.

---

### Recommendation

Add an admin-accessible recovery function (e.g., `recoverUnallocatedRewards`) that can transfer reward tokens that were never distributed — identifiable as the difference between the contract's reward token balance and the sum of all outstanding `rewards[user]` values — to the protocol treasury after the reward period ends. Alternatively, track the cumulative "wasted" reward seconds when `totalKernelStaked == 0` and allow the admin to roll them into the next reward period via `notifyRewardAmount`.

---

### Proof of Concept

1. Admin calls `notifyRewardAmount(1_000e18)` while `totalKernelStaked > 0` (e.g., Alice has staked 100 KERNEL). A 30-day reward period begins with `rewardRate = 1_000e18 / 30 days`.
2. Alice immediately calls `initiateWithdrawal(100)`. The `updateReward(alice)` modifier snapshots her earned rewards up to this block; then `totalKernelStaked` is set to `0`.
3. For the remaining ~29.9 days, `rewardPerToken()` returns `rewardPerTokenStored` unchanged (line 409–411). Approximately `rewardRate * 29.9 days ≈ 997e18` reward tokens accrue at `rewardRate` but are never credited to any user.
4. After the period ends, the contract holds ~997e18 reward tokens with no claimant.
5. Admin attempts `notifyRewardAmount(...)` for the next period — reverts with `NoStakedTokens` until someone stakes again.
6. Even after a new staker arrives and a new period begins, the ~997e18 tokens from the previous period remain permanently stranded in the contract balance, silently inflating the apparent reward pool without being distributed. [1](#0-0) [6](#0-5)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L18-23)
```text
 * @dev If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards
 *      for that period will stay locked in the contract. In this deployment, we're avoiding this issue by
 *      ensuring there are always some tokens staked before admin calls the `notifyRewardAmount` function,
 *      as well as for the entire duration of the reward period. Otherwise, staking just 1 wei by any address
 *      will ensure that the contract never has any unallocated rewards.
 */
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L320-338)
```text
    function initiateWithdrawal(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();
        if (balanceOf[msg.sender] < _amount) revert InsufficientStakedBalance();
        if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();

        balanceOf[msg.sender] -= _amount;
        totalKernelStaked -= _amount;

        // Create a withdrawal record
        uint256 withdrawalId = ++withdrawalCounter;
        uint256 unlockTime = block.timestamp + withdrawalDelay;

        withdrawals[withdrawalId] = Withdrawal({
            user: msg.sender, amount: _amount, unlockTime: unlockTime, claimed: false, withdrawalId: withdrawalId
        });
        userWithdrawalIds[msg.sender].push(withdrawalId);

        emit WithdrawalInitiated(msg.sender, _amount, withdrawalId, unlockTime);
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L552-620)
```text
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
```
