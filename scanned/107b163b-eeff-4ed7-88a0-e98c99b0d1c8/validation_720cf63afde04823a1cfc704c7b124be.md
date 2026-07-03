### Title
Rewards Permanently Frozen When `totalKernelStaked` Drops to Zero During Active Reward Period - (File: `contracts/KERNEL/KernelDepositPool.sol`)

---

### Summary

`KernelDepositPool` implements a Synthetix-style staking mechanism. If all stakers withdraw during an active reward distribution window, `totalKernelStaked` drops to zero and `rewardPerToken()` freezes. The ongoing `rewardRate` continues to tick with no recipients, permanently locking those reward tokens in the contract with no recovery path.

---

### Finding Description

When `notifyRewardAmount` is called, it sets a `rewardRate` and a `finishAt` deadline. Reward accumulation is governed by:

```solidity
function rewardPerToken() public view returns (uint256) {
    if (totalKernelStaked == 0) {
        return rewardPerTokenStored;
    }
    return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
        / totalKernelStaked;
}
``` [1](#0-0) 

When `totalKernelStaked == 0`, `rewardPerToken()` returns the frozen `rewardPerTokenStored`. The `rewardRate` continues to accrue over time but no address accumulates any share of it. Those rewards are permanently unclaimable.

`notifyRewardAmount` does guard against starting a reward period with zero stakers:

```solidity
if (totalKernelStaked == 0) revert NoStakedTokens();
``` [2](#0-1) 

However, this check only applies at the instant `notifyRewardAmount` is called. Any user can subsequently call `initiateWithdrawal`, which immediately reduces `totalKernelStaked`:

```solidity
balanceOf[msg.sender] -= _amount;
totalKernelStaked -= _amount;
``` [3](#0-2) 

If the last staker withdraws, `totalKernelStaked` hits zero mid-period and all remaining rewards for that window are permanently frozen. The contract itself acknowledges this in its NatSpec but relies entirely on an off-chain deployment strategy rather than any on-chain protection:

> *"If `totalKernelStaked` ever hits zero during a reward distribution window, any remaining rewards for that period will stay locked in the contract."* [4](#0-3) 

There is no `sweep`, `rescue`, or `recoverERC20` function in `KernelDepositPool`. The only path for `rewardsToken` to leave the contract is through `getReward()`, which requires a non-zero accumulated reward balance — impossible when `totalKernelStaked` was zero for the entire accrual window.

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

Reward tokens injected via `notifyRewardAmount` for any time window where `totalKernelStaked == 0` are permanently locked in the contract. No user can claim them, and no admin function exists to recover them.

---

### Likelihood Explanation

**Medium.**

Any unprivileged staker can call `initiateWithdrawal` at any time. In a pool with few participants — or even a single staker — one withdrawal drops `totalKernelStaked` to zero. This is realistic during low-participation periods, market stress, or when a single large staker exits. The withdrawal delay does not prevent the accounting freeze; `totalKernelStaked` is decremented immediately at `initiateWithdrawal`, not at `claimWithdrawal`. [5](#0-4) 

---

### Recommendation

When the last staker withdraws (i.e., `totalKernelStaked` becomes zero), checkpoint `updatedAt` to the current timestamp so that the frozen interval is not counted against the reward window. This mirrors the fix pattern from the referenced report — guard the reward-accrual path against zero-recipient periods:

```diff
function initiateWithdrawal(uint256 _amount) external nonReentrant updateReward(msg.sender) {
    ...
    balanceOf[msg.sender] -= _amount;
    totalKernelStaked -= _amount;
+   // Freeze reward accrual when no tokens remain staked
+   if (totalKernelStaked == 0) {
+       updatedAt = block.timestamp;
+   }
    ...
}
```

Alternatively, add an admin-only `recoverUnallocatedRewards()` function that can sweep rewards that accrued during zero-staked windows after `finishAt`.

---

### Proof of Concept

1. Admin calls `notifyRewardAmount(1_000e18)` while one staker holds `1_000e18` KERNEL. The `NoStakedTokens` guard passes. `rewardRate` is set, `finishAt = block.timestamp + duration`.
2. The staker immediately calls `initiateWithdrawal(1_000e18)`. `totalKernelStaked` drops to `0`. The `updateReward` modifier snapshots their earned rewards correctly up to this point.
3. Time advances to `finishAt`. During this entire window, `rewardPerToken()` returns the frozen `rewardPerTokenStored` because `totalKernelStaked == 0`.
4. The full `rewardRate * duration` worth of tokens that were not yet accrued at step 2 remain in the contract. No address has accumulated them. No function can extract them.
5. Rewards are permanently frozen.

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

**File:** contracts/KERNEL/KernelDepositPool.sol (L320-337)
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L569-570)
```text
        // Prevent starting a reward period when no tokens are staked to avoid unallocated rewards
        if (totalKernelStaked == 0) revert NoStakedTokens();
```
