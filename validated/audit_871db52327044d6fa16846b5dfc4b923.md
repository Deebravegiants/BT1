### Title
Rewards Permanently Locked in `KernelDepositPool` When `totalKernelStaked` Drops to Zero During Active Reward Period - (File: contracts/KERNEL/KernelDepositPool.sol)

---

### Summary

`KernelDepositPool` contains the same class of vulnerability described in M-07: when `totalKernelStaked` drops to zero during an active reward distribution window, all rewards accruing during that zero-staked period are permanently locked in the contract with no recovery path.

---

### Finding Description

`KernelDepositPool.rewardPerToken()` returns `rewardPerTokenStored` unchanged whenever `totalKernelStaked == 0`: [1](#0-0) 

This means that for every second `totalKernelStaked == 0` while `rewardRate > 0` and `block.timestamp < finishAt`, the reward tokens that would have been distributed (`rewardRate * elapsed`) are silently skipped — they remain in the contract balance but are never credited to any staker's `rewardPerTokenStored` accumulator.

The `updateReward` modifier advances `updatedAt` to `lastTimeRewardApplicable()` on every call: [2](#0-1) 

So once `updatedAt` advances past a zero-staked interval, those rewards are irrecoverably skipped — `rewardPerTokenStored` never catches up.

**The partial mitigation is insufficient.** The developers added a guard in `notifyRewardAmount` to block starting a reward period with zero stakers: [3](#0-2) 

The NatSpec comment at the top of the contract also acknowledges the issue and states the operational assumption that tokens will always be staked: [4](#0-3) 

However, this guard only prevents starting a reward period with zero stakers. It does **not** prevent `totalKernelStaked` from reaching zero **during** an already-active reward period. The critical gap is in `initiateWithdrawal`, which immediately decrements `totalKernelStaked` at the moment of initiation — not at the moment of claim: [5](#0-4) 

`claimWithdrawal` does not touch `totalKernelStaked` at all: [6](#0-5) 

So the window between `initiateWithdrawal` and `claimWithdrawal` (up to `MAX_WITHDRAWAL_DELAY = 30 days`) is a period during which `totalKernelStaked` can be zero while a reward period is still active.

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

Reward tokens sent to the contract via `notifyRewardAmount` that accrue during any zero-staked interval are permanently locked. There is no admin rescue function, no sweep mechanism, and no way to re-distribute them. The `rewardsToken` balance of the contract will exceed what is actually claimable by stakers, and the excess is irrecoverable.

---

### Likelihood Explanation

This is a realistic scenario requiring only normal user behavior:

1. Admin calls `notifyRewardAmount` with stakers present (passes the guard).
2. All current stakers call `initiateWithdrawal` — a normal, permissionless user action.
3. `totalKernelStaked` immediately drops to zero.
4. The reward period continues running (up to `duration` seconds, e.g. weeks/months) with `rewardRate > 0` but no stakers.
5. All rewards accruing during this interval are permanently locked.

The withdrawal delay (`withdrawalDelay`, up to `MAX_WITHDRAWAL_DELAY = 30 days`) means the zero-staked window can persist for up to 30 days within a single reward period. No attacker coordination is required — organic mass-exit by stakers is sufficient.

---

### Recommendation

Two complementary fixes:

1. **Defer `totalKernelStaked` decrement to `claimWithdrawal`**, not `initiateWithdrawal`. This keeps stakers "economically present" until they actually receive their tokens, preventing zero-staked gaps during active reward periods.

2. **Alternatively, track and carry forward unallocated rewards**: when `totalKernelStaked == 0` in `rewardPerToken()`, accumulate the skipped reward amount into a separate `unallocatedRewards` variable, and add it back into the next `notifyRewardAmount` call so it is not lost.

---

### Proof of Concept

**Step-by-step attack path:**

1. Admin calls `setRewardsDuration(30 days)` and then `notifyRewardAmount(1_000_000e18)` while Alice has `1e18` KERNEL staked. `rewardRate = 1_000_000e18 / 30 days`. Guard passes because `totalKernelStaked == 1e18 > 0`.

2. Alice immediately calls `initiateWithdrawal(1e18)`. `totalKernelStaked` drops to `0` at line 326. `balanceOf[Alice]` drops to `0`.

3. For the next 30 days, every call to `rewardPerToken()` hits the `totalKernelStaked == 0` branch and returns `rewardPerTokenStored` unchanged (line 409-410). `updatedAt` advances on every `updateReward` trigger, permanently skipping the reward accumulation.

4. After `withdrawalDelay`, Alice calls `claimWithdrawal` and receives her KERNEL back. But the `1_000_000e18` reward tokens (minus the tiny slice before step 2) remain locked in the contract forever — no staker has a non-zero `balanceOf` during the reward period, so `earned()` returns 0 for everyone, and `getReward()` transfers nothing.

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L320-327)
```text
    function initiateWithdrawal(uint256 _amount) external nonReentrant updateReward(msg.sender) {
        if (_amount == 0) revert AmountZero();
        if (balanceOf[msg.sender] < _amount) revert InsufficientStakedBalance();
        if (userWithdrawalIds[msg.sender].length >= maxNumberOfWithdrawalsPerUser) revert WithdrawalLimitReached();

        balanceOf[msg.sender] -= _amount;
        totalKernelStaked -= _amount;

```

**File:** contracts/KERNEL/KernelDepositPool.sol (L344-379)
```text
    function claimWithdrawal(uint256 _withdrawalId) external nonReentrant {
        Withdrawal storage withdrawal = withdrawals[_withdrawalId];

        if (withdrawal.user == address(0)) {
            revert WithdrawalDoesNotExist();
        }

        if (withdrawal.user != msg.sender) {
            revert NotYourWithdrawal();
        }

        if (block.timestamp < withdrawal.unlockTime) {
            revert WithdrawalNotReady();
        }

        if (withdrawal.claimed) {
            revert WithdrawalAlreadyClaimed();
        }

        withdrawal.claimed = true;

        // Remove the withdrawal ID from the user's list of withdrawal IDs
        uint256[] storage userWithdrawalIdsArray = userWithdrawalIds[msg.sender];
        for (uint256 i = 0; i < userWithdrawalIdsArray.length; ++i) {
            if (userWithdrawalIdsArray[i] == _withdrawalId) {
                userWithdrawalIdsArray[i] = userWithdrawalIdsArray[userWithdrawalIdsArray.length - 1];
                userWithdrawalIdsArray.pop();
                break;
            }
        }

        // Transfer the KERNEL tokens from contract to user
        kernelToken.safeTransfer(msg.sender, withdrawal.amount);

        emit WithdrawalClaimed(msg.sender, withdrawal.amount, _withdrawalId);
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L566-570)
```text
    function notifyRewardAmount(uint256 _amount) external onlyRole(DEFAULT_ADMIN_ROLE) updateReward(address(0)) {
        if (_amount == 0) revert AmountZero();

        // Prevent starting a reward period when no tokens are staked to avoid unallocated rewards
        if (totalKernelStaked == 0) revert NoStakedTokens();
```
