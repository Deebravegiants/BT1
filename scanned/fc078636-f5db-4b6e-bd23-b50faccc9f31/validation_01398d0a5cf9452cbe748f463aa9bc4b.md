### Title
Reward Rate Truncation in `notifyRewardAmount` Permanently Locks Yield for Stakers - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool.notifyRewardAmount` computes `rewardRate` via integer division (`receivedAmount / duration`), permanently discarding the remainder (`receivedAmount % duration`) into the contract with no recovery path. Every reward notification silently locks up to `duration - 1` wei of reward tokens that stakers can never claim.

### Finding Description
In `notifyRewardAmount`, the reward rate is set as:

```solidity
// Line 580
rewardRate = receivedAmount / duration;
// Line 583
rewardRate = (receivedAmount + remaining) / duration;
``` [1](#0-0) 

Because `rewardRate` is an integer, the division truncates. The total rewards that will ever be distributed over the period is `rewardRate * duration`, which equals `(receivedAmount / duration) * duration` — always strictly less than `receivedAmount` unless `receivedAmount` is exactly divisible by `duration`. The difference, `receivedAmount % duration`, is transferred into the contract but never emitted to any staker. There is no sweep or recovery function in the contract. [2](#0-1) 

The `earned` and `rewardPerToken` functions both correctly multiply before dividing, so the rounding loss is entirely concentrated at the `rewardRate` assignment step. [3](#0-2) 

### Impact Explanation
**Permanent freezing of unclaimed yield (Medium).** On every call to `notifyRewardAmount`, up to `duration - 1` wei of reward tokens are permanently locked in the contract. With a 7-day duration (`604800` seconds), each call can silently discard up to 604799 wei. Over repeated reward cycles these amounts accumulate irreversibly. Stakers receive less yield than was deposited on their behalf, with no mechanism to recover the stranded tokens.

### Likelihood Explanation
Certain on every invocation of `notifyRewardAmount`. The truncation is deterministic and unavoidable given integer arithmetic; it occurs regardless of the reward amount or who calls the function. The only case where no tokens are lost is when `receivedAmount` is an exact multiple of `duration`, which is unlikely in practice.

### Recommendation
Scale `rewardRate` by a precision factor (e.g., `1e18`) to preserve sub-second granularity, or track the undistributed remainder and roll it into the next reward period:

```solidity
// Option A: track remainder and add it to the next period
uint256 leftover = receivedAmount % duration;
rewardRate = (receivedAmount - leftover) / duration;
// store leftover and add it to receivedAmount on the next notifyRewardAmount call

// Option B: use a scaled rate (requires adjusting rewardPerToken accordingly)
rewardRate = (receivedAmount * DECIMAL_PRECISION) / duration;
```

### Proof of Concept
1. Admin calls `notifyRewardAmount` with `receivedAmount = 1_000_000` and `duration = 604800` (7 days).
2. `rewardRate = 1_000_000 / 604800 = 1` (truncated).
3. Total distributed over the period: `1 * 604800 = 604800` tokens.
4. Permanently locked: `1_000_000 - 604800 = 395200` tokens — **39.5% of the reward** is silently frozen.
5. Repeat calls compound the loss; no function exists to recover stranded tokens. [1](#0-0)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L408-423)
```text
    function rewardPerToken() public view returns (uint256) {
        if (totalKernelStaked == 0) {
            return rewardPerTokenStored;
        }
        return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
            / totalKernelStaked;
    }

    /**
     * @notice Calculates the amount of rewards earned by an account
     * @param _account The account to for which rewards are calculated
     * @return The earned reward amount
     */
    function earned(address _account) public view returns (uint256) {
        return (balanceOf[_account] * (rewardPerToken() - userRewardPerTokenPaid[_account]) / DECIMAL_PRECISION)
            + rewards[_account];
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
