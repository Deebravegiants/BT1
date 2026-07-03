### Title
Reward Tokens Permanently Locked When `totalKernelStaked` Drops to Zero During Active Reward Period - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
In `KernelDepositPool`, if all stakers call `initiateWithdrawal()` during an active reward distribution window, `totalKernelStaked` drops to zero. The `rewardPerToken()` function freezes at `rewardPerTokenStored` and stops accumulating, causing all reward tokens allocated for the remaining period to be permanently locked in the contract with no recovery path.

### Finding Description
`KernelDepositPool` is a Synthetix-style staking rewards contract. When `notifyRewardAmount()` is called, a `rewardRate` is set and rewards are distributed linearly over `duration` seconds.

The `rewardPerToken()` function handles the zero-supply case by returning the frozen stored value:

```solidity
function rewardPerToken() public view returns (uint256) {
    if (totalKernelStaked == 0) {
        return rewardPerTokenStored;  // frozen — no new rewards accrue
    }
    return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
        / totalKernelStaked;
}
```

When `totalKernelStaked == 0`, `rewardPerTokenStored` stops increasing. The `rewardRate` continues to be non-zero and `finishAt` is still in the future, but the rewards that should have been distributed during the zero-staked interval are never credited to any user. They remain as `rewardsToken` balance in the contract.

The contract has **no admin rescue function** for `rewardsToken`. The only admin functions are `setRewardsDuration`, `notifyRewardAmount`, `setWithdrawalDelay`, and `setMaxNumberOfWithdrawalsPerUser`. The contract does not inherit `Recoverable` and has no `emergencyWithdraw` or `recoverTokens` for the rewards token. The contract itself acknowledges this in its NatSpec:

> *"If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards for that period will stay locked in the contract."*

The mitigation described in the comment is purely operational ("ensuring there are always some tokens staked"), not enforced by code.

### Impact Explanation
Reward tokens (the `rewardsToken` ERC20) allocated for the zero-staked interval are permanently locked in `KernelDepositPool` with no on-chain recovery path. This is a **permanent freezing of unclaimed yield** — the reward tokens are irrecoverable.

### Likelihood Explanation
Low. Requires all KERNEL stakers to call `initiateWithdrawal()` during an active reward period, reducing `totalKernelStaked` to zero. This can occur naturally during a protocol migration, a market panic, or a coordinated exit. No attacker action is required — ordinary user behavior (withdrawing stake) is sufficient.

### Recommendation
Add an admin-callable rescue function for the `rewardsToken` that can only be invoked after `finishAt` has passed and `totalKernelStaked` is zero, to recover any unallocated reward balance. Alternatively, enforce at the code level that `totalKernelStaked` cannot reach zero while a reward period is active (e.g., revert `initiateWithdrawal` if it would bring `totalKernelStaked` to zero before `finishAt`).

### Proof of Concept
1. Admin calls `notifyRewardAmount(1_000e18)` with `duration = 30 days`. `rewardRate = 1_000e18 / 30 days`. `finishAt = block.timestamp + 30 days`. `totalKernelStaked = 100e18`.
2. After 10 days, all stakers call `initiateWithdrawal(fullBalance)`. The `updateReward` modifier runs, snapshotting each user's earned rewards up to this point. `totalKernelStaked` becomes `0`.
3. For the remaining 20 days, `rewardPerToken()` returns the frozen `rewardPerTokenStored`. No user accrues any new rewards.
4. The unallocated rewards = `rewardRate * 20 days ≈ 666e18` tokens remain in the contract.
5. No function in `KernelDepositPool` allows these tokens to be recovered. Calling `notifyRewardAmount` again after `finishAt` would add *more* rewards on top of the locked balance, compounding the loss. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L14-22)
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
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L320-326)
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
