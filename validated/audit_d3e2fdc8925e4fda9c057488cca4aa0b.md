### Title
Reward Tokens Permanently Stuck in `KernelDepositPool` When `totalKernelStaked` Drops to Zero Mid-Period - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool` contains a Synthetix-style staking rewards mechanism. If `totalKernelStaked` drops to zero during an active reward distribution window, the reward tokens accruing during the zero-supply interval are permanently locked in the contract with no recovery path.

### Finding Description

The contract's own NatSpec explicitly acknowledges the risk:

> *"If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards for that period will stay locked in the contract."* [1](#0-0) 

The `rewardPerToken()` function freezes accumulation when `totalKernelStaked == 0`:

```solidity
function rewardPerToken() public view returns (uint256) {
    if (totalKernelStaked == 0) {
        return rewardPerTokenStored;  // accumulation halts
    }
    return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
        / totalKernelStaked;
}
``` [2](#0-1) 

The `initiateWithdrawal` function immediately decrements `totalKernelStaked` (before the delay expires), so the last staker's withdrawal brings the total to zero mid-period: [3](#0-2) 

When `totalKernelStaked` reaches zero mid-period, `updatedAt` is snapped to the current timestamp via the `updateReward` modifier on `initiateWithdrawal`. All reward tokens that would have accrued from that point to `finishAt` are never attributed to any user and remain as excess `rewardsToken` balance in the contract.

When the next `notifyRewardAmount` is called (after someone stakes again), the calculation uses only the newly provided amount — the stranded excess balance from the prior period is **not** rolled in:

```solidity
if (block.timestamp >= finishAt) {
    rewardRate = receivedAmount / duration;  // stranded balance ignored
}
``` [4](#0-3) 

Critically, `KernelDepositPool` has **no rescue or recovery function** for `rewardsToken`. It does not inherit from `Recoverable`, and no admin function exists to extract stuck reward tokens from the contract. [5](#0-4) 

### Impact Explanation

Reward tokens accruing during any zero-supply interval within an active reward period are permanently frozen inside `KernelDepositPool`. There is no on-chain path to recover them. This constitutes **permanent freezing of unclaimed yield** — a Medium-severity impact per the allowed scope.

### Likelihood Explanation

**Low.** Requires all stakers to call `initiateWithdrawal` during an active reward period, reducing `totalKernelStaked` to zero. This is realistic in a low-participation pool, during a market stress event, or if a single large staker holds the entire stake. The contract's own comment treats this as a known operational risk managed off-chain, but provides no on-chain safeguard.

### Recommendation

Add an admin-only rescue function for `rewardsToken` that can only transfer the **excess** balance (i.e., `rewardsToken.balanceOf(address(this))` minus the sum of all `rewards[user]` entries), preventing recovery of legitimately owed user rewards while allowing stranded tokens to be reclaimed.

### Proof of Concept

1. Admin calls `notifyRewardAmount(1_000e18)` with `totalKernelStaked = 100e18`. `rewardRate = 1_000e18 / duration`. `finishAt = block.timestamp + duration`.
2. Halfway through the period, all stakers call `initiateWithdrawal`. The last call sets `totalKernelStaked = 0` and snaps `updatedAt = block.timestamp` (via `updateReward` modifier).
3. For the remaining half of the period, `rewardPerToken()` returns the frozen `rewardPerTokenStored`. Approximately `500e18` reward tokens accrue to no one.
4. After `finishAt`, admin calls `notifyRewardAmount` again (after someone stakes). New `rewardRate = newAmount / duration` — the `500e18` stranded tokens are not included.
5. The `500e18` tokens remain in the contract forever with no function to extract them. [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L18-22)
```text
 * @dev If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards
 *      for that period will stay locked in the contract. In this deployment, we're avoiding this issue by
 *      ensuring there are always some tokens staked before admin calls the `notifyRewardAmount` function,
 *      as well as for the entire duration of the reward period. Otherwise, staking just 1 wei by any address
 *      will ensure that the contract never has any unallocated rewards.
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L320-327)
```text
    function initiateWithdrawal(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();
        if (balanceOf[msg.sender] < _amount) revert InsufficientStakedBalance();
        if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();

        balanceOf[msg.sender] -= _amount;
        totalKernelStaked -= _amount;

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
