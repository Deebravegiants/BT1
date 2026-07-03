### Title
Undistributed Reward Tokens Permanently Stranded in `KernelDepositPool` When All Stakers Exit Before Reward Period Ends - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary

`KernelDepositPool.notifyRewardAmount()` calculates the new reward rate using only the delta of newly transferred tokens (`balanceAfter - balanceBefore`). When all stakers withdraw during an active reward period, the remaining undistributed rewards sit idle in the contract. Once the reward period expires, any subsequent call to `notifyRewardAmount` ignores those stranded tokens entirely, permanently freezing them.

### Finding Description

`notifyRewardAmount` determines the reward amount via a transfer-in pattern:

```solidity
uint256 balanceBefore = rewardsToken.balanceOf(address(this));
rewardsToken.safeTransferFrom(msg.sender, address(this), _amount);
uint256 balanceAfter = rewardsToken.balanceOf(address(this));
uint256 receivedAmount = balanceAfter - balanceBefore;
``` [1](#0-0) 

It then branches on whether the current period is still active:

```solidity
if (block.timestamp >= finishAt) {
    rewardRate = receivedAmount / duration;
} else {
    uint256 remaining = (finishAt - block.timestamp) * rewardRate;
    rewardRate = (receivedAmount + remaining) / duration;
}
``` [2](#0-1) 

When `block.timestamp >= finishAt` (the old period has ended), `remaining` is **not** computed and the new `rewardRate` is set solely from `receivedAmount`. Any tokens that were deposited in the previous period but never distributed (because `totalKernelStaked` dropped to zero) are already present in `balanceBefore` and are therefore invisible to the new rate calculation — they are never scheduled for distribution.

The guard that blocks distribution when no one is staked:

```solidity
if (totalKernelStaked == 0) revert NoStakedTokens();
``` [3](#0-2) 

prevents `notifyRewardAmount` from being called while the pool is empty, so the admin cannot "roll over" the stranded balance into a new period while `totalKernelStaked == 0`. By the time a new staker arrives and the admin can call `notifyRewardAmount` again, the old period has expired and the stranded tokens are silently excluded.

There is no sweep, rescue, or recovery function in `KernelDepositPool` that could reclaim these tokens. [4](#0-3) 

### Impact Explanation

Reward tokens (the `rewardsToken` ERC-20) that were legitimately deposited by the admin for distribution to stakers become permanently locked in the contract. No staker can ever claim them, and no admin function can recover them. This constitutes **permanent freezing of unclaimed yield**.

### Likelihood Explanation

The trigger is a normal user action — stakers calling `withdraw` — combined with the passage of time. No special privilege or coordination is required. In a pool with volatile participation (e.g., stakers exit en masse after a price drop or during a market event), the entire tail of a reward period can be stranded. The admin's only recourse would be to call `notifyRewardAmount` before `finishAt` while someone is still staked, but the `NoStakedTokens` guard makes that impossible if the pool empties first.

### Recommendation

When starting a new reward period after the previous one has ended, include any excess token balance already held by the contract in the new `rewardRate` calculation:

```solidity
if (block.timestamp >= finishAt) {
    // Include any previously unallocated balance
    uint256 leftover = rewardsToken.balanceOf(address(this)) - receivedAmount;
    rewardRate = (receivedAmount + leftover) / duration;
} else {
    uint256 remaining = (finishAt - block.timestamp) * rewardRate;
    rewardRate = (receivedAmount + remaining) / duration;
}
```

Alternatively, add an admin-callable rescue function that can re-queue stranded tokens into the next reward period.

### Proof of Concept

1. Admin calls `notifyRewardAmount(1000e18)` with `duration = 7 days`.  
   → `rewardRate ≈ 1000e18 / 604800`, `finishAt = T + 7 days`.

2. At `T + 3 days`, all stakers call `withdraw()`.  
   → `totalKernelStaked = 0`. `rewardPerToken()` freezes at `rewardPerTokenStored`.  
   → ~571e18 tokens remain unallocated in the contract.

3. Admin attempts `notifyRewardAmount(...)` to rescue the situation.  
   → Reverts: `NoStakedTokens()`. [3](#0-2) 

4. At `T + 7 days`, `finishAt` passes. A new staker deposits.

5. Admin calls `notifyRewardAmount(1000e18)` with new tokens.  
   → `block.timestamp >= finishAt`, so `rewardRate = 1000e18 / duration`.  
   → The 571e18 stranded tokens are already in `balanceBefore`; `receivedAmount = 1000e18` only.  
   → 571e18 tokens are permanently locked in the contract with no path to distribution. [5](#0-4)

### Citations

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
