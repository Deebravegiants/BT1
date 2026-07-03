### Title
Rewards Permanently Locked When `totalKernelStaked` Drops to Zero During Active Reward Period - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary

`KernelDepositPool` uses a Synthetix-style continuous reward model. When `totalKernelStaked` reaches zero during an active reward window, the `rewardPerToken()` function freezes `rewardPerTokenStored` in place. When the next staker arrives, the `updateReward` modifier advances `updatedAt` past the zero-staked interval without accumulating the rewards that accrued during it. Those rewards are permanently locked in the contract.

### Finding Description

The `rewardPerToken()` function short-circuits when `totalKernelStaked == 0`:

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

The `updateReward` modifier always advances `updatedAt` to `lastTimeRewardApplicable()`, regardless of whether `totalKernelStaked` is zero:

```solidity
// contracts/KERNEL/KernelDepositPool.sol:232-241
modifier updateReward(address _account) {
    rewardPerTokenStored = rewardPerToken();
    updatedAt = lastTimeRewardApplicable();
    ...
}
```

The `initiateWithdrawal()` function immediately reduces both `balanceOf` and `totalKernelStaked`:

```solidity
// contracts/KERNEL/KernelDepositPool.sol:325-326
balanceOf[msg.sender] -= _amount;
totalKernelStaked -= _amount;
```

When the last staker calls `initiateWithdrawal()`, `totalKernelStaked` drops to zero. During the subsequent idle period, `rewardRate` continues to emit rewards but no one can receive them. When the next staker calls `stake()`, the `updateReward` modifier fires **before** `totalKernelStaked` is incremented. At that moment `totalKernelStaked` is still 0, so `rewardPerToken()` returns the stale `rewardPerTokenStored` and `updatedAt` is advanced to the present. The entire reward budget for the zero-staked interval is silently discarded and permanently locked in the contract.

The contract's own NatSpec acknowledges this:

```
// contracts/KERNEL/KernelDepositPool.sol:18-22
If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards
for that period will stay locked in the contract.
```

The stated mitigation is purely operational ("ensuring there are always some tokens staked"), with no on-chain enforcement preventing stakers from withdrawing during an active period.

### Impact Explanation

Rewards emitted during the zero-staked interval are permanently locked in the `KernelDepositPool` contract. No staker — present or future — can ever claim them. This is a permanent freezing of unclaimed yield.

**Impact: Medium — Permanent freezing of unclaimed yield.**

### Likelihood Explanation

Any staker can call `initiateWithdrawal()` at any time. If the last remaining staker exits during an active reward window (e.g., due to market conditions, a better opportunity, or deliberate griefing), `totalKernelStaked` hits zero and the vulnerability is triggered. No admin action or privileged role is required. The `withdrawalDelay` (up to 30 days) does not prevent the accounting loss — it only delays the token transfer; `totalKernelStaked` is reduced immediately at `initiateWithdrawal()` time.

### Recommendation

When `totalKernelStaked` is zero, do not advance `updatedAt`. This preserves the unallocated reward interval so it can be correctly distributed once staking resumes:

```solidity
modifier updateReward(address _account) {
    rewardPerTokenStored = rewardPerToken();
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

This is the standard fix applied in audited Synthetix forks.

### Proof of Concept

1. Admin calls `notifyRewardAmount(1000e18)` with `duration = 100 days`. `rewardRate = 10e18/day`. Alice is the only staker with 1000 KERNEL.
2. After 10 days, Alice calls `initiateWithdrawal(1000)`. `updateReward` runs: `rewardPerTokenStored` correctly captures 10 days of rewards; `updatedAt = block.timestamp`; `totalKernelStaked = 0`.
3. 50 days pass. `rewardRate * 50 days = 500e18` rewards are emitted but unallocated.
4. Bob calls `stake(1000)`. `updateReward` fires first: `totalKernelStaked == 0` → `rewardPerToken()` returns stale `rewardPerTokenStored`; `updatedAt` advances 50 days forward. Then `totalKernelStaked = 1000`.
5. The 500e18 rewards for the 50-day idle window are now permanently locked. Bob only earns rewards from day 60 onward. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L232-241)
```text
    modifier updateReward(address _account) {
        rewardPerTokenStored = rewardPerToken();
        updatedAt = lastTimeRewardApplicable();

        if (_account != address(0)) {
            rewards[_account] = earned(_account);
            userRewardPerTokenPaid[_account] = rewardPerTokenStored;
        }

        _;
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L566-591)
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
```
