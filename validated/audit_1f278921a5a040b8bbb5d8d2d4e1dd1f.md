### Title
Precision Loss in `notifyRewardAmount` Permanently Locks Reward Tokens - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
The `KernelDepositPool` contract contains the same integer division truncation bug as the referenced M-13 finding. In `notifyRewardAmount`, the `rewardRate` is computed by dividing `receivedAmount` by `duration`, which truncates the remainder. The truncated dust (`receivedAmount % duration`) is transferred into the contract but can never be distributed or recovered, permanently locking reward tokens.

### Finding Description
In `KernelDepositPool.notifyRewardAmount`, the reward rate is set as:

```solidity
// Line 580
rewardRate = receivedAmount / duration;
// or, for mid-period top-ups (line 583):
rewardRate = (receivedAmount + remaining) / duration;
```

Because Solidity integer division truncates, `rewardRate * duration < receivedAmount` whenever `receivedAmount % duration != 0`. The difference is silently discarded from the distributable pool. The contract has no sweep, rescue, or recovery function for the rewards token — the only admin functions are `setRewardsDuration`, `notifyRewardAmount`, `setWithdrawalDelay`, and `setMaxNumberOfWithdrawalsPerUser`, none of which can extract stranded reward tokens. [1](#0-0) 

### Impact Explanation
Every call to `notifyRewardAmount` permanently locks `receivedAmount % duration` reward tokens in the contract. With a typical `duration` of 1 week (604,800 seconds) and a reward token with low decimals (e.g., 8-decimal WBTC), the locked amount per epoch can be material. Over multiple reward epochs the locked dust accumulates with no recovery path. This constitutes **permanent freezing of unclaimed yield** (Medium severity per the allowed impact scope).

### Likelihood Explanation
This is triggered by the normal, intended admin operation of calling `notifyRewardAmount`. It fires on every single reward epoch unless `receivedAmount` happens to be exactly divisible by `duration` — a condition that is essentially never true in practice. No attacker action is required; the loss is automatic and cumulative.

### Recommendation
Compute the distributable amount from the truncated rate and refund or track the remainder:

```solidity
rewardRate = receivedAmount / duration;
uint256 leftover = receivedAmount - (rewardRate * duration);
// either: transfer leftover back to the caller
// or: add an admin rescue function for the rewards token
```

Alternatively, add an admin `recoverRewardToken(uint256 amount)` function that can sweep tokens in excess of `rewardRate * (finishAt - block.timestamp)`.

### Proof of Concept
Using the same parameters as M-13 (adapted to `KernelDepositPool`):

1. Admin sets `duration = 1 weeks` (604,800 seconds).
2. Admin calls `notifyRewardAmount(10e8)` (10 WBTC, 8 decimals).
3. `rewardRate = 1_000_000_000 / 604_800 = 1653` (truncated).
4. Distributable total = `1653 * 604_800 = 999_734_400`.
5. Locked dust = `1_000_000_000 - 999_734_400 = 265_600` (0.00265600 WBTC ≈ $100+ at current prices).
6. After the full `duration` elapses, all stakers claim their rewards. The contract retains 265,600 units of the reward token with no mechanism to distribute or recover them. [2](#0-1)

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
