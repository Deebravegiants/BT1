### Title
Rewards Permanently Locked When `totalKernelStaked` Drops to Zero During Active Reward Period - (`contracts/KERNEL/KernelDepositPool.sol`)

---

### Summary

`KernelDepositPool` is a Synthetix-style staking rewards contract. Its `updateReward` modifier always advances `updatedAt` to `lastTimeRewardApplicable()`, even when `totalKernelStaked == 0`. If all stakers exit during an active reward window, the rewards accrued during the zero-staker interval are permanently locked in the contract and can never be claimed.

---

### Finding Description

The `updateReward` modifier unconditionally updates `updatedAt`:

```solidity
modifier updateReward(address _account) {
    rewardPerTokenStored = rewardPerToken();
    updatedAt = lastTimeRewardApplicable();   // always advances
    ...
}
``` [1](#0-0) 

`rewardPerToken()` correctly short-circuits accumulation when `totalKernelStaked == 0`:

```solidity
function rewardPerToken() public view returns (uint256) {
    if (totalKernelStaked == 0) {
        return rewardPerTokenStored;   // no accumulation — correct
    }
    ...
}
``` [2](#0-1) 

However, because `updatedAt` is still advanced in the modifier, the time elapsed during the zero-staker gap is silently consumed. When the next staker arrives and `totalKernelStaked > 0` again, the formula `rewardRate * (lastTimeRewardApplicable() - updatedAt)` starts from the post-gap timestamp, permanently skipping the rewards that should have been preserved for future stakers.

`initiateWithdrawal` decrements `totalKernelStaked` before the function body returns, and it is callable by any staker at any time:

```solidity
function initiateWithdrawal(uint256 _amount) external nonReentrant updateReward(msg.sender) {
    ...
    balanceOf[msg.sender] -= _amount;
    totalKernelStaked -= _amount;
    ...
}
``` [3](#0-2) 

The `notifyRewardAmount` guard (`if (totalKernelStaked == 0) revert NoStakedTokens()`) only prevents starting a reward period with zero stakers; it does not prevent all stakers from exiting mid-period. [4](#0-3) 

The contract's own NatSpec comment explicitly acknowledges this risk but relies on an off-chain operational guarantee rather than on-chain enforcement:

> "If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards for that period will stay locked in the contract. In this deployment, we're avoiding this issue by ensuring there are always some tokens staked..." [5](#0-4) 

---

### Impact Explanation

Reward tokens transferred into the contract via `notifyRewardAmount` and accrued during a zero-staker interval are permanently unclaimable. There is no recovery function. The impact is **permanent freezing of unclaimed yield**.

---

### Likelihood Explanation

The scenario requires all stakers to withdraw during an active reward period. `initiateWithdrawal` is permissionless — any staker can reduce their position at any time. The contract's own comment acknowledges this is a known risk. A coordinated or organic full-exit during a reward window (e.g., due to a market event or a better yield opportunity) is realistic.

---

### Recommendation

In the `updateReward` modifier, only advance `updatedAt` when `totalKernelStaked > 0`, mirroring the guard already present in `rewardPerToken()`:

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

This ensures that time elapsed with no stakers does not consume the reward budget, preserving those rewards for future stakers — consistent with the Synthetix reference implementation's intent.

---

### Proof of Concept

1. Admin calls `notifyRewardAmount(1_000e18)` with one staker present (`totalKernelStaked > 0`). Reward period starts; `finishAt = block.timestamp + duration`.
2. The sole staker calls `initiateWithdrawal(totalStake)`. Inside `updateReward`, `updatedAt` is set to `block.timestamp` (T0). Then `totalKernelStaked` becomes 0.
3. 15 days pass (half the reward period). No staker calls any function, so `updatedAt` stays at T0.
4. A new staker calls `stake(amount)`. `updateReward` fires: `rewardPerToken()` returns `rewardPerTokenStored` unchanged (because `totalKernelStaked == 0` at modifier execution time). Then `updatedAt = lastTimeRewardApplicable()` = T0 + 15 days.
5. The new staker earns rewards only for the remaining half of the period. The 15 days of rewards (~500e18 tokens) are permanently locked in the contract with no mechanism to recover them.

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L18-22)
```text
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L566-570)
```text
    function notifyRewardAmount(uint256 _amount) external onlyRole(DEFAULT_ADMIN_ROLE) updateReward(address(0)) {
        if (_amount == 0) revert AmountZero();

        // Prevent starting a reward period when no tokens are staked to avoid unallocated rewards
        if (totalKernelStaked == 0) revert NoStakedTokens();
```
