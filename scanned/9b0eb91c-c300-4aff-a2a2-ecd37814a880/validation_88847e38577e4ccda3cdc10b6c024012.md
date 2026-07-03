### Title
Reward Tokens Permanently Locked When `totalKernelStaked` Drops to Zero Mid-Period - (`contracts/KERNEL/KernelDepositPool.sol`)

---

### Summary

`KernelDepositPool` uses a Synthetix-style reward accounting model. When all stakers call `initiateWithdrawal()` during an active reward period, `totalKernelStaked` immediately drops to zero. The `rewardPerToken()` function returns `rewardPerTokenStored` unchanged during this zero-staking window, but the `updateReward` modifier still advances `updatedAt` to the current time. Rewards emitted during the zero-staking window are never credited to any user and are permanently locked in the contract with no recovery path.

---

### Finding Description

`initiateWithdrawal()` immediately decrements `totalKernelStaked` before the withdrawal delay elapses: [1](#0-0) 

This means `totalKernelStaked` can reach zero while `rewardRate > 0` and `block.timestamp < finishAt`.

The `rewardPerToken()` view function short-circuits when `totalKernelStaked == 0`, returning the stored value unchanged: [2](#0-1) 

However, the `updateReward` modifier unconditionally advances `updatedAt` to `lastTimeRewardApplicable()`: [3](#0-2) 

The combination is fatal: when the next user stakes after the zero-staking window, `updateReward` runs with `totalKernelStaked == 0`, so `rewardPerTokenStored` is not increased, but `updatedAt` is pushed forward to the current time. The rewards emitted during the entire zero-staking window are silently skipped and can never be claimed by anyone.

`notifyRewardAmount()` guards against starting a reward period with zero stakers: [4](#0-3) 

But this guard only applies at the moment of reward notification. It does not prevent all stakers from exiting mid-period, which is the actual trigger for the bug.

There is no admin or user function to recover the stranded reward tokens. The full admin surface is `setRewardsDuration`, `notifyRewardAmount`, `setWithdrawalDelay`, and `setMaxNumberOfWithdrawalsPerUser` — none of which can sweep stuck rewards. [5](#0-4) 

---

### Impact Explanation

Reward tokens (`rewardsToken`) accumulate in the contract balance but are never credited to `rewardPerTokenStored` during the zero-staking window. The shortfall between the contract's `rewardsToken` balance and the sum of all claimable `rewards[user]` values grows monotonically and is irrecoverable. This is a **permanent freezing of unclaimed yield** (Medium severity).

---

### Likelihood Explanation

The withdrawal delay (`withdrawalDelay`) can be up to 30 days (`MAX_WITHDRAWAL_DELAY`). During this entire window, `totalKernelStaked` is already zero even though the tokens have not left the contract. A single large staker (or coordinated exit by all stakers) during an active reward period is sufficient to trigger the bug. The `KernelMerkleDistributor` uses `stakeFor` to auto-stake claimed KERNEL, meaning staker composition can change rapidly after a distribution event, making a temporary zero-staking window realistic.

---

### Recommendation

Mirror the fix pattern from the reference report: when `totalKernelStaked == 0` during an active reward period, either pause reward emission (do not advance `updatedAt`) or add an admin sweep function. The cleanest fix is to not advance `updatedAt` when `totalKernelStaked == 0`:

```solidity
modifier updateReward(address _account) {
    rewardPerTokenStored = rewardPerToken();
    // Only advance updatedAt when there are stakers, so rewards
    // are not silently lost during zero-staking windows.
    if (totalKernelStaked > 0) {
        updatedAt = lastTimeRewardApplicable();
    }
    if (_account != address(0)) {
        rewards[_account] = earned(_account);
        userRewardPerTokenPaid[_account] = rewardPerTokenStored;
    }
    _;
}
```

Alternatively, add an admin-only `recoverStrandedRewards()` function that transfers the difference between the contract balance and the sum of all pending rewards to the treasury after `finishAt`.

---

### Proof of Concept

```
Setup:
  - duration = 100 seconds, rewardRate = 10 KERNEL/second (1000 KERNEL total)
  - Alice stakes 100 KERNEL; admin calls notifyRewardAmount(1000)

t=0:   notifyRewardAmount called; finishAt = t+100; rewardRate = 10/s
t=10:  Alice calls initiateWithdrawal(100)
         → updateReward(Alice): rewardPerTokenStored += 10*10/100 = 1.0; updatedAt = t10
         → totalKernelStaked = 0
         → Alice's pending reward = 100 * 1.0 = 100 KERNEL ✓

t=10 to t=60: totalKernelStaked == 0; 500 KERNEL emitted but credited to nobody
         → rewardPerTokenStored stays at 1.0; updatedAt stays at t10

t=60:  Bob stakes 100 KERNEL
         → updateReward(Bob): rewardPerToken() returns 1.0 (totalKernelStaked==0 branch)
         → updatedAt advances to t60 ← the 50-second gap is silently consumed
         → totalKernelStaked = 100

t=100: Bob calls getReward()
         → earned(Bob) = 100 * (rewardPerToken() - 0) / 1e18
         → rewardPerToken() = 1.0 + 10*(100-60)/100 = 1.0 + 4.0 = 5.0
         → Bob earns 500 KERNEL

Result:
  Alice claims 100 KERNEL
  Bob claims 500 KERNEL
  Total claimed: 600 KERNEL
  Contract holds: 400 KERNEL permanently locked (the 50-second zero-staking window)
```

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L320-327)
```text
    function initiateWithdrawal(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();
        if (balanceOf[msg.sender] < _amount) revert InsufficientStakedBalance();
        if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L552-592)
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
```
