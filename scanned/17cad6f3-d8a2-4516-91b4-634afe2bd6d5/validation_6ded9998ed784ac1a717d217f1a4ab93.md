### Title
Precision Truncation in `notifyRewardAmount` Permanently Freezes Reward Tokens — (`contracts/KERNEL/KernelDepositPool.sol`)

---

### Summary

`KernelDepositPool.notifyRewardAmount` computes `rewardRate` via integer division, permanently locking the truncated remainder of every reward deposit in the contract with no recovery mechanism.

---

### Finding Description

In `KernelDepositPool.notifyRewardAmount`, the reward rate is computed as:

```solidity
// Line 580
rewardRate = receivedAmount / duration;
// or, when a period is still active (line 583):
rewardRate = (receivedAmount + remaining) / duration;
``` [1](#0-0) 

Solidity integer division truncates. The actual tokens distributed over the full period equal `rewardRate * duration`, which is strictly less than `receivedAmount` (or `receivedAmount + remaining`) whenever the numerator is not perfectly divisible by `duration`. The difference — `receivedAmount % duration` (or `(receivedAmount + remaining) % duration`) — is transferred into the contract via `safeTransferFrom` but is never accounted for in `rewardPerTokenStored` and can never be claimed by any staker.

The `earned` function confirms that stakers can only ever claim up to `rewardRate * duration` worth of tokens:

```solidity
// Line 421-423
function earned(address _account) public view returns (uint256) {
    return (balanceOf[_account] * (rewardPerToken() - userRewardPerTokenPaid[_account]) / DECIMAL_PRECISION)
        + rewards[_account];
}
``` [2](#0-1) 

There is no `rescue`, `sweep`, or token-recovery function anywhere in the contract. The entire admin function set consists only of `setRewardsDuration`, `notifyRewardAmount`, `setWithdrawalDelay`, and `setMaxNumberOfWithdrawalsPerUser` — none of which can retrieve stuck `rewardsToken` balances. [3](#0-2) 

This is structurally identical to the FeeSplitter finding: in both cases a division-by-integer operation discards a remainder that has already been deposited into the contract, and no withdrawal path exists for the residual.

---

### Impact Explanation

Every call to `notifyRewardAmount` permanently freezes `receivedAmount % duration` reward tokens. With a typical `duration` of, e.g., 7 days (604,800 seconds), any reward amount not divisible by 604,800 loses up to 604,799 wei per call. Over many reward periods this accumulates into a non-trivial permanently frozen balance of `rewardsToken` that stakers are entitled to but can never receive.

**Impact**: Permanent freezing of unclaimed yield (Medium per scope).

---

### Likelihood Explanation

This triggers on every single call to `notifyRewardAmount` in normal protocol operation. No adversarial action is required — the precision loss is an inherent property of the integer arithmetic. The admin calling `notifyRewardAmount` is the intended operational flow, not a compromise scenario. Likelihood is **high**.

---

### Recommendation

Track the undistributed remainder and roll it into the next reward period, or add it back to the distributed amount:

```solidity
if (block.timestamp >= finishAt) {
    rewardRate = receivedAmount / duration;
    // remainder: receivedAmount % duration is now tracked or rolled forward
} else {
    uint256 remaining = (finishAt - block.timestamp) * rewardRate;
    rewardRate = (receivedAmount + remaining) / duration;
}
// Optionally: emit the dust amount so it can be accounted for off-chain,
// or accumulate it in a `dustAccumulator` and include it in the next notifyRewardAmount call.
```

The standard mitigation used by Synthetix forks is to carry the remainder forward into the next `notifyRewardAmount` call by storing it in a state variable and adding it to `receivedAmount` on the next invocation.

---

### Proof of Concept

1. Admin sets `duration = 604_800` (7 days in seconds).
2. Admin calls `notifyRewardAmount(1_000_000)`.
3. `rewardRate = 1_000_000 / 604_800 = 1` (truncated).
4. Total distributed over the period = `1 * 604_800 = 604_800` tokens.
5. Stuck forever = `1_000_000 - 604_800 = 395_200` tokens — **39.5% of the reward deposit is permanently frozen**.
6. All stakers call `getReward()` and collectively receive only 604,800 tokens despite 1,000,000 being deposited.
7. `rewardsToken.balanceOf(address(kernelDepositPool))` exceeds the sum of all claimable rewards by 395,200 tokens with no path to recover them. [4](#0-3)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L421-423)
```text
    function earned(address _account) public view returns (uint256) {
        return (balanceOf[_account] * (rewardPerToken() - userRewardPerTokenPaid[_account]) / DECIMAL_PRECISION)
            + rewards[_account];
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
