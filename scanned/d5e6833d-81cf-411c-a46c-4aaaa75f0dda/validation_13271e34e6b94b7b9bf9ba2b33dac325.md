### Title
Sole-Staker Reward Theft via Minimal Stake After `totalKernelStaked` Drops to Zero - (File: contracts/KERNEL/KernelDepositPool.sol)

---

### Summary

`KernelDepositPool` uses a Synthetix-style reward distribution mechanism. When all stakers withdraw during an active reward period, `totalKernelStaked` drops to zero. An unprivileged attacker can then stake as little as 1 wei of KERNEL and capture **all remaining rewards** for the rest of the reward period, because the `rewardPerToken()` accumulator divides by `totalKernelStaked = 1`, yielding the full `rewardRate` per second to the sole staker.

---

### Finding Description

`KernelDepositPool.rewardPerToken()` is:

```solidity
function rewardPerToken() public view returns (uint256) {
    if (totalKernelStaked == 0) {
        return rewardPerTokenStored;
    }
    return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
        / totalKernelStaked;
}
``` [1](#0-0) 

When `totalKernelStaked == 0`, the accumulator is frozen and `updatedAt` is not advanced. The `updateReward` modifier, called on every state-changing function, sets `updatedAt = lastTimeRewardApplicable()`:

```solidity
modifier updateReward(address _account) {
    rewardPerTokenStored = rewardPerToken();
    updatedAt = lastTimeRewardApplicable();
    ...
}
``` [2](#0-1) 

When an attacker calls `stake(1)` while `totalKernelStaked == 0`:

1. `updateReward(attacker)` fires **before** the balance update.
2. `rewardPerToken()` returns the frozen `rewardPerTokenStored` (since `totalKernelStaked` is still 0 at this point).
3. `updatedAt` is advanced to `block.timestamp` (or `finishAt`).
4. `userRewardPerTokenPaid[attacker] = rewardPerTokenStored`.
5. Then `balanceOf[attacker] += 1` and `totalKernelStaked = 1`. [3](#0-2) 

From this moment forward, every second the attacker accrues:

```
rewardRate * elapsed * 1e18 / 1  →  full rewardRate per second
```

The attacker with 1 wei of KERNEL earns the same reward tokens per second as if they had staked the entire supply. All rewards from the moment they stake until `finishAt` flow exclusively to them.

The `notifyRewardAmount` guard (`if (totalKernelStaked == 0) revert NoStakedTokens()`) only prevents **starting** a new reward period with zero stakers. It does not prevent stakers from all withdrawing **during** an active period, which is the root cause here. [4](#0-3) 

The contract's own NatSpec comment acknowledges the zero-staking risk but frames it as a deployment concern, not a live-period attack vector: [5](#0-4) 

---

### Impact Explanation

**High — Theft of unclaimed yield.**

An attacker with 1 wei of KERNEL can drain all reward tokens remaining in an active reward period. For example, if a 100-day period has 50 days remaining and `rewardRate` distributes 500 KERNEL over those 50 days, the attacker claims all 500 KERNEL. The reward tokens are transferred out of the contract to the attacker via `getReward()`: [6](#0-5) 

---

### Likelihood Explanation

**Medium.** The attack requires `totalKernelStaked` to reach zero during an active reward period. This is realistic because:

- `initiateWithdrawal` immediately reduces `totalKernelStaked` (tokens are not locked during the delay period).
- Early in the protocol's life, there may be very few stakers.
- A single large staker withdrawing can bring `totalKernelStaked` to zero.
- No front-running is required — the attacker simply monitors `totalKernelStaked` on-chain and calls `stake(1)`. [7](#0-6) 

---

### Recommendation

1. **Track "dead time"**: When `totalKernelStaked` drops to zero, record the timestamp. When the next staker arrives, advance `updatedAt` to `block.timestamp` (already done) but also reduce `finishAt` by the dead-time duration, or zero out the remaining reward allocation.
2. **Minimum stake enforcement**: Require a meaningful minimum stake amount that makes the attack economically unviable relative to the reward pool size.
3. **Pause rewards on zero supply**: When `totalKernelStaked` reaches zero, set `rewardRate = 0` and allow the admin to reclaim undistributed rewards, then restart with `notifyRewardAmount` once stakers return.

---

### Proof of Concept

```
1. Admin calls setRewardsDuration(100 days).
2. Alice calls stake(1000e18 KERNEL).
3. Admin calls notifyRewardAmount(1000e18 rewardToken).
   → rewardRate = 1000e18 / (100 days) ≈ 1.157e14 tokens/second
   → finishAt = block.timestamp + 100 days
4. 50 days pass. Alice has earned ~500e18 reward tokens.
5. Alice calls initiateWithdrawal(1000e18).
   → updateReward(Alice): rewards[Alice] = 500e18, rewardPerTokenStored updated, updatedAt = day 50
   → totalKernelStaked = 0
6. Attacker calls stake(1) (1 wei of KERNEL).
   → updateReward(attacker): rewardPerToken() returns frozen rewardPerTokenStored (totalKernelStaked==0)
   → updatedAt = day 50 (current time, same moment)
   → userRewardPerTokenPaid[attacker] = rewardPerTokenStored
   → totalKernelStaked = 1
7. 50 more days pass (reward period ends at day 100).
8. Attacker calls getReward().
   → earned(attacker) = 1 * (rewardRate * 50days * 1e18 / 1) / 1e18
                       = rewardRate * 50 days
                       ≈ 500e18 reward tokens
9. Attacker receives ~500e18 reward tokens with only 1 wei of KERNEL staked.
```

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L281-289)
```text
    function stake(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();

        balanceOf[msg.sender] += _amount;
        totalKernelStaked += _amount;
        kernelToken.safeTransferFrom(msg.sender, address(this), _amount);

        emit Staked(msg.sender, _amount);
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L382-390)
```text
    function getReward() external nonReentrant updateReward(msg.sender) {
        uint256 rewardAmount = rewards[msg.sender];

        if (rewardAmount > 0) {
            rewards[msg.sender] = 0;
            rewardsToken.safeTransfer(msg.sender, rewardAmount);
            emit RewardsClaimed(msg.sender, rewardAmount);
        }
    }
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
