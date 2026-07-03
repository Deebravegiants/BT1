### Title
Reward Tokens Permanently Locked When `totalKernelStaked` Drops to Zero During an Active Reward Period — (File: `contracts/KERNEL/KernelDepositPool.sol`)

---

### Summary

`KernelDepositPool` is a Synthetix-style staking rewards contract. If `totalKernelStaked` reaches zero at any point during an active reward distribution window, the reward tokens that should have been distributed during that zero-staked interval are permanently locked in the contract. There is no admin rescue or recovery function for stranded reward tokens.

---

### Finding Description

`KernelDepositPool.notifyRewardAmount()` transfers reward tokens into the contract and sets a `rewardRate` and `finishAt` timestamp. The reward accounting relies on `rewardPerToken()`:

```solidity
// contracts/KERNEL/KernelDepositPool.sol:408-413
function rewardPerToken() public view returns (uint256) {
    if (totalKernelStaked == 0) {
        return rewardPerTokenStored;
    }
    return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
        / totalKernelStaked;
}
```

When `totalKernelStaked == 0`, the function returns the frozen `rewardPerTokenStored`. The `rewardRate` continues to tick, but no staker accumulates those rewards. The tokens corresponding to the zero-staked interval are never credited to anyone and remain in the contract balance.

The `notifyRewardAmount()` function guards against starting a reward period with zero stakers:

```solidity
// contracts/KERNEL/KernelDepositPool.sol:570
if (totalKernelStaked == 0) revert NoStakedTokens();
```

However, this guard only applies at the moment `notifyRewardAmount` is called. It does not prevent `totalKernelStaked` from dropping to zero **during** an already-active reward window. Any staker can call `initiateWithdrawal()` at any time, which immediately decrements `totalKernelStaked`:

```solidity
// contracts/KERNEL/KernelDepositPool.sol:325-326
balanceOf[msg.sender] -= _amount;
totalKernelStaked -= _amount;
```

Once the reward period ends (`block.timestamp >= finishAt`), the reward tokens that accrued during the zero-staked interval are permanently stranded. The contract has no `rescueTokens`, `recoverERC20`, or equivalent admin function to retrieve them. The contract's own NatSpec acknowledges this:

> *"If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards for that period will stay locked in the contract."* [1](#0-0) 

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

Reward tokens deposited via `notifyRewardAmount()` that correspond to any zero-staked interval within the reward window are permanently locked in `KernelDepositPool`. They cannot be redistributed in a future reward period (because `notifyRewardAmount` only adds new tokens on top of the existing balance, not the stranded ones — the stranded tokens inflate the contract balance but are never re-accounted), and there is no recovery path. [2](#0-1) 

---

### Likelihood Explanation

**Medium.** The scenario requires all stakers to withdraw during an active reward period. This is realistic: stakers may exit en masse in response to market conditions, a better yield opportunity, or simply because the reward period is long (admin-configurable `duration`). The `initiateWithdrawal()` path is fully permissionless and requires no special role. The `withdrawalDelay` only delays the final token transfer, not the `totalKernelStaked` decrement — so the accounting damage occurs immediately upon `initiateWithdrawal()`. [3](#0-2) 

---

### Recommendation

Add an admin-only function to recover reward tokens that were not distributed due to zero-staked intervals, callable only after the reward period has ended. For example:

```solidity
function recoverUndistributedRewards(address recipient) external onlyRole(DEFAULT_ADMIN_ROLE) {
    if (block.timestamp < finishAt) revert RewardDurationNotFinished();
    uint256 undistributed = rewardsToken.balanceOf(address(this));
    rewardsToken.safeTransfer(recipient, undistributed);
}
```

Alternatively, track the total rewards committed vs. distributed and only allow recovery of the difference.

---

### Proof of Concept

1. Admin calls `notifyRewardAmount(1_000_000e18)` with `duration = 30 days`. `totalKernelStaked = 1000e18` at this point (passes the guard). `rewardRate = 1_000_000e18 / 30 days`.
2. On day 1, all stakers call `initiateWithdrawal()`. `totalKernelStaked` drops to `0` immediately.
3. For the remaining 29 days, `rewardPerToken()` returns the frozen `rewardPerTokenStored` — no rewards accumulate for anyone.
4. On day 31, `finishAt` passes. The ~967,000 reward tokens corresponding to the 29 zero-staked days remain in the contract.
5. No function exists to recover them. They are permanently locked. [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L14-23)
```text
/**
 * @title Kernel Staking Rewards Contract
 * @dev Implements a basic staking mechanism with rewards
 * @dev Modified from https://github.com/Synthetixio/synthetix/blob/develop/contracts/StakingRewards.sol
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
