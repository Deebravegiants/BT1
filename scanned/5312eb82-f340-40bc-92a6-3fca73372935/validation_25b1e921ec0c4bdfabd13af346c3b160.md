### Title
Permanent Freezing of Unclaimed Yield When `totalKernelStaked` Drops to Zero During Active Reward Period - (File: contracts/KERNEL/KernelDepositPool.sol)

---

### Summary

`KernelDepositPool` uses a Synthetix-style staking rewards model. When `totalKernelStaked` reaches zero during an active reward distribution window, `rewardPerToken()` freezes while `updatedAt` continues to advance, permanently locking all rewards that should have accrued during the zero-staked interval. There is no on-chain enforcement preventing this and no recovery mechanism.

---

### Finding Description

The `rewardPerToken()` function short-circuits to return the frozen `rewardPerTokenStored` whenever `totalKernelStaked == 0`:

```solidity
function rewardPerToken() public view returns (uint256) {
    if (totalKernelStaked == 0) {
        return rewardPerTokenStored;  // frozen — no new rewards accumulate
    }
    return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
        / totalKernelStaked;
}
```

The `updateReward` modifier, however, unconditionally advances `updatedAt` to `lastTimeRewardApplicable()`:

```solidity
modifier updateReward(address _account) {
    rewardPerTokenStored = rewardPerToken();
    updatedAt = lastTimeRewardApplicable();   // advances past the zero-staked gap
    ...
}
```

When the next user stakes (or any state-changing function is called), `updateReward` fires. At that moment `totalKernelStaked` is still 0 (the stake hasn't been added yet), so `rewardPerToken()` returns the frozen value and `updatedAt` is advanced to the current timestamp. The rewards that should have accrued during the entire zero-staked interval are silently skipped and permanently locked in the contract.

Any staker can trigger this by calling `initiateWithdrawal()` for their full balance, which decrements `totalKernelStaked` immediately:

```solidity
function initiateWithdrawal(uint256 _amount) external nonReentrant updateReward(msg.sender) {
    ...
    balanceOf[msg.sender] -= _amount;
    totalKernelStaked -= _amount;   // can reach 0 with no guard
    ...
}
```

The contract's own NatSpec comment acknowledges the risk but relies entirely on an off-chain operational promise with zero on-chain enforcement:

> *"If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards for that period will stay locked in the contract. In this deployment, we're avoiding this issue by ensuring there are always some tokens staked…"*

There is no `recoverERC20` or equivalent function, so locked reward tokens are irrecoverable.

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

Reward tokens transferred into the contract via `notifyRewardAmount()` that correspond to the zero-staked interval are permanently locked. No staker — past or future — can ever claim them. The loss is proportional to `rewardRate × (duration of zero-staked gap)`.

---

### Likelihood Explanation

**Medium.** The scenario requires `totalKernelStaked` to reach zero during an active reward period. This is reachable by:

- A single large staker who holds 100 % of `totalKernelStaked` calling `initiateWithdrawal()` for their full balance (realistic in early-stage deployment).
- Multiple stakers coordinating or independently withdrawing during the same window.

The contract explicitly acknowledges the risk exists and that the only mitigation is operational. No on-chain guard prevents `initiateWithdrawal()` from reducing `totalKernelStaked` to zero mid-period.

---

### Recommendation

1. **On-chain guard in `initiateWithdrawal()`**: Revert if the withdrawal would reduce `totalKernelStaked` to zero while `block.timestamp < finishAt`.
2. **Admin recovery function**: Add a `recoverRewards()` function callable only after `finishAt` that allows the admin to reclaim any reward tokens in excess of what is owed to current stakers.
3. **Alternatively**: Track a `lockedRewards` accumulator that captures rewards accrued during zero-staked intervals and either redistributes them in the next period or makes them recoverable by the admin.

---

### Proof of Concept

```
State: duration = 30 days, rewardRate = 1e18/s, finishAt = T+30d

T=0:   Admin calls notifyRewardAmount(2592000e18)
       totalKernelStaked = 100e18 (Alice is the only staker)

T=15d: Alice calls initiateWithdrawal(100e18)
       → balanceOf[Alice] = 0, totalKernelStaked = 0
       → updateReward(Alice) fires: rewardPerTokenStored frozen, updatedAt = T+15d
       → Alice correctly receives her 15-day share of rewards via rewards[Alice]

T=15d–T=30d: totalKernelStaked == 0
       → rewardPerToken() returns frozen rewardPerTokenStored for all calls
       → updatedAt advances on every interaction, skipping the 15-day gap

T=20d: Bob calls stake(100e18)
       → updateReward(Bob) fires with totalKernelStaked still 0
       → rewardPerTokenStored unchanged, updatedAt = T+20d
       → Bob's userRewardPerTokenPaid = rewardPerTokenStored (frozen value)
       → The 5-day gap (T+15d → T+20d) rewards are permanently lost

T=30d: finishAt reached
       Rewards for T+15d → T+30d (15 days × rewardRate) = 1296000e18 tokens
       are permanently locked in the contract with no recovery path.
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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
