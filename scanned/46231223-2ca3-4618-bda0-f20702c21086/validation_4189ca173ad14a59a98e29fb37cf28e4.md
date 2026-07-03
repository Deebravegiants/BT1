### Title
Truncated Division in `notifyRewardAmount` Permanently Freezes Reward Tokens — (`contracts/KERNEL/KernelDepositPool.sol`)

### Summary

`KernelDepositPool.notifyRewardAmount` computes `rewardRate` via integer division `receivedAmount / duration`. The remainder `receivedAmount % duration` is transferred into the contract but can never be distributed to stakers, permanently freezing up to `duration - 1` reward tokens per epoch with no recovery path.

### Finding Description

In `KernelDepositPool.notifyRewardAmount`, the reward rate is set as:

```solidity
// Line 580
rewardRate = receivedAmount / duration;
// Line 583 (mid-period top-up)
rewardRate = (receivedAmount + remaining) / duration;
``` [1](#0-0) 

Integer division truncates the result. The discarded remainder — `receivedAmount % duration` tokens — has already been transferred into the contract at line 574 but is never accounted for in `rewardRate`. Since `rewardPerToken()` and `earned()` derive all distributable yield exclusively from `rewardRate`:

```solidity
return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
    / totalKernelStaked;
``` [2](#0-1) 

…the truncated tokens are mathematically unreachable. There is no admin sweep, rescue, or excess-recovery function anywhere in the contract.

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

Every call to `notifyRewardAmount` silently discards up to `duration − 1` reward tokens. These tokens sit in the contract balance forever, indistinguishable from legitimately-held rewards, but never claimable by any staker. The loss is bounded per call but accumulates across epochs and is irreversible.

Concrete example with a low-decimal reward token (e.g., USDC, 6 decimals):
- `duration` = 30 days = 2,592,000 seconds
- `receivedAmount` = 1,000,000 × 10⁶ = 1,000,000,000,000 units
- `rewardRate` = 1,000,000,000,000 / 2,592,000 = **385,802** (truncated)
- Total distributed = 385,802 × 2,592,000 = 999,998,784,000 units
- **Permanently frozen = 1,216,000 units ≈ 1.22 USDC per epoch**
- Maximum possible loss per epoch = 2,591,999 units ≈ **2.59 USDC**

With a higher-decimal reward token the absolute loss is larger in raw units, though the relative fraction remains `< 1/duration`.

### Likelihood Explanation

**High.** This triggers on every single call to `notifyRewardAmount` under normal protocol operation. No special conditions, attacker action, or token properties are required — integer division always truncates. The only mitigating factor is that the per-epoch loss is small relative to total rewards, but it is guaranteed and cumulative.

### Recommendation

Track and redistribute the truncated dust. A standard pattern is:

```solidity
// After computing rewardRate, add the remainder back to the next epoch
uint256 dust = receivedAmount % duration;
// Store dust and add it to the next notifyRewardAmount call, or
// require the caller to send only amounts divisible by duration.
```

Alternatively, require `receivedAmount % duration == 0` and revert otherwise, forcing the admin to send an exact multiple of `duration`.

### Proof of Concept

1. Admin calls `setRewardsDuration(2_592_000)` (30 days).
2. Admin calls `notifyRewardAmount(1_000_000e6)` with USDC as `rewardsToken`.
3. Contract receives 1,000,000,000,000 units.
4. `rewardRate` = 1,000,000,000,000 / 2,592,000 = 385,802.
5. After 30 days, total distributed = 385,802 × 2,592,000 = 999,998,784,000 units.
6. Remaining in contract: 1,216,000 units (~1.22 USDC) — permanently frozen.
7. No function exists to recover these tokens; `getReward()` only transfers `rewards[msg.sender]` which is derived solely from `rewardRate`. [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L382-389)
```text
    function getReward() external nonReentrant updateReward(msg.sender) {
        uint256 rewardAmount = rewards[msg.sender];

        if (rewardAmount > 0) {
            rewards[msg.sender] = 0;
            rewardsToken.safeTransfer(msg.sender, rewardAmount);
            emit RewardsClaimed(msg.sender, rewardAmount);
        }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L412-413)
```text
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
