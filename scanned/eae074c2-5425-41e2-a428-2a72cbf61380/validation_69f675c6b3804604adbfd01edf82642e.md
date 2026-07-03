### Title
Reward Accumulation Silently Skipped When `totalKernelStaked` Is Zero, Permanently Freezing Unclaimed Yield — (File: `contracts/KERNEL/KernelDepositPool.sol`)

---

### Summary

In `KernelDepositPool`, when `totalKernelStaked` drops to zero during an active reward period, `rewardPerToken()` returns the stored value unchanged while `updatedAt` still advances to the current timestamp. This consumes the time window without distributing rewards, permanently locking any reward tokens that accrued during the zero-staked period inside the contract with no recovery path.

---

### Finding Description

`rewardPerToken()` short-circuits and returns `rewardPerTokenStored` unchanged when `totalKernelStaked == 0`: [1](#0-0) 

The `updateReward` modifier calls `rewardPerToken()` to update `rewardPerTokenStored`, but **unconditionally** advances `updatedAt` to `lastTimeRewardApplicable()` regardless of whether `totalKernelStaked` is zero: [2](#0-1) 

`lastTimeRewardApplicable()` returns `min(finishAt, block.timestamp)`, so `updatedAt` advances through the zero-staked window: [3](#0-2) 

When the next staker calls `stake()`, `updateReward` fires again with `totalKernelStaked == 0` (before the new balance is added). At that point `lastTimeRewardApplicable() - updatedAt == 0`, so `rewardPerTokenStored` still does not advance. The entire reward emission for the zero-staked interval is permanently unclaimable — there is no sweep or recovery function in the contract.

`initiateWithdrawal` reduces `totalKernelStaked` immediately and atomically, so a coordinated or natural full exit by all stakers is sufficient to trigger the condition: [4](#0-3) 

The contract's own NatSpec acknowledges the root cause but relies entirely on an off-chain operational assumption rather than a code-level guard: [5](#0-4) 

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

Reward tokens transferred into the contract via `notifyRewardAmount` become permanently unclaimable for any period during which `totalKernelStaked == 0`. There is no admin sweep, no rescue function, and no way to re-distribute the lost rewards. The `rewardsToken` balance of the contract will exceed the sum of all claimable `rewards[user]` values, with the surplus irrecoverable.

---

### Likelihood Explanation

Any combination of stakers calling `initiateWithdrawal` that drives `totalKernelStaked` to zero during an active reward window triggers the bug. This requires no privileged access. A natural full exit (e.g., all stakers unstaking after a reward period is announced but before it ends) is sufficient. The contract provides no on-chain mechanism to prevent it.

---

### Recommendation

In the `updateReward` modifier, only advance `updatedAt` when `totalKernelStaked > 0`. When no tokens are staked, the timestamp should remain frozen so that the reward emission for the idle period is preserved and can be distributed once staking resumes:

```solidity
modifier updateReward(address _account) {
    rewardPerTokenStored = rewardPerToken();
    if (totalKernelStaked > 0) {          // only advance time when stakers exist
        updatedAt = lastTimeRewardApplicable();
    }
    if (_account != address(0)) {
        rewards[_account] = earned(_account);
        userRewardPerTokenPaid[_account] = rewardPerTokenStored;
    }
    _;
}
```

---

### Proof of Concept

1. Admin calls `notifyRewardAmount(1000e18)` while at least one staker exists (`totalKernelStaked > 0`). `finishAt = block.timestamp + duration`, `rewardRate = 1000e18 / duration`.
2. All stakers call `initiateWithdrawal` for their full balance. Each call triggers `updateReward` (correctly advancing `rewardPerTokenStored` up to that moment). After the last withdrawal, `totalKernelStaked == 0`.
3. Time advances by `T` seconds (still within the reward window, `block.timestamp < finishAt`). During this window, `rewardRate * T` worth of reward tokens should have been distributed but were not.
4. A new staker calls `stake(1e18)`. `updateReward` fires: `rewardPerToken()` returns `rewardPerTokenStored` unchanged (because `totalKernelStaked == 0` at the time of the call, before the new balance is added). `updatedAt` is set to `block.timestamp`.
5. From this point forward, `rewardPerToken()` calculates from the new `updatedAt`, skipping the entire idle window. The `rewardRate * T` tokens are permanently locked in the contract with no claimant.

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L400-402)
```text
    function lastTimeRewardApplicable() public view returns (uint256) {
        return finishAt < block.timestamp ? finishAt : block.timestamp;
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
