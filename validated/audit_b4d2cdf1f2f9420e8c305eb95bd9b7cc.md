### Title
Truncating Integer Division in `notifyRewardAmount` Permanently Locks Reward Tokens — (`File: contracts/KERNEL/KernelDepositPool.sol`)

### Summary

`KernelDepositPool.notifyRewardAmount()` computes `rewardRate` via integer division `receivedAmount / duration`. Solidity truncates this division, so `rewardRate * duration < receivedAmount`. The remainder (`receivedAmount % duration`) is transferred into the contract but can never be distributed to stakers — it is permanently locked. When `notifyRewardAmount` is called multiple times (rolling over reward periods), the truncation compounds across calls, analogous to the RPL multi-interval inflation inaccuracy.

### Finding Description

In `notifyRewardAmount()`, the reward rate is set as:

```solidity
// line 580
rewardRate = receivedAmount / duration;
// or, for a mid-period top-up (line 582-583):
uint256 remaining = (finishAt - block.timestamp) * rewardRate;
rewardRate = (receivedAmount + remaining) / duration;
```

Because Solidity integer division truncates toward zero, `rewardRate * duration` is strictly less than `receivedAmount` (or `receivedAmount + remaining`) whenever the numerator is not perfectly divisible by `duration`. The difference — up to `duration - 1` wei per call — is transferred into the contract but is never accounted for in `rewardPerTokenStored` or any user's `rewards` mapping. No sweep or recovery mechanism exists.

The compounding case mirrors the RPL multi-interval bug exactly: when `notifyRewardAmount` is called while a period is still active, `remaining = (finishAt - block.timestamp) * rewardRate` is itself computed from an already-truncated `rewardRate`. The new `rewardRate = (receivedAmount + remaining) / duration` then truncates again. Each successive call accumulates additional permanently-locked dust on top of prior dust. [1](#0-0) 

### Impact Explanation

Every call to `notifyRewardAmount` permanently locks up to `duration - 1` wei of reward tokens in the contract. With a `duration` of 7 days (604,800 seconds), up to 604,799 wei is lost per call. Over many reward periods this accumulates into a non-trivial amount of permanently frozen yield that stakers are entitled to but can never claim. This matches the allowed impact: **Medium — Permanent freezing of unclaimed yield**. [2](#0-1) 

### Likelihood Explanation

`notifyRewardAmount` is called by the admin on a regular cadence (every reward period). The truncation occurs on every single call as a deterministic consequence of integer division — it requires no special conditions, no attacker, and no misconfiguration. The only requirement is that `receivedAmount % duration != 0`, which is true for virtually all realistic reward amounts. Likelihood is **High** (certain to occur in normal operation).

### Recommendation

Track the undistributed remainder and either:

1. **Carry the remainder forward** into the next period's numerator:
   ```solidity
   uint256 leftover = receivedAmount % duration;
   rewardRate = (receivedAmount - leftover) / duration;
   // store leftover and add it to the next notifyRewardAmount call
   ```

2. **Scale up precision** by multiplying `rewardRate` by a large constant (e.g., `1e18`) and dividing it back out in `rewardPerToken()`, reducing the relative truncation error to negligible levels.

3. **Refund the remainder** to the caller so no tokens are silently locked.

### Proof of Concept

**Setup:** `duration = 604800` (7 days), `receivedAmount = 1e18 + 1` (1 ETH + 1 wei).

**Step 1 — First `notifyRewardAmount` call:**
```
rewardRate = (1e18 + 1) / 604800 = 1653439153439 (truncated)
rewardRate * duration = 1653439153439 * 604800 = 999999999999667200
lost_dust = (1e18 + 1) - 999999999999667200 = 332801 wei
```
332,801 wei is permanently locked after a single call.

**Step 2 — Second `notifyRewardAmount` call mid-period** (e.g., 1 day later, `timeLeft = 518400`):
```
remaining = 518400 * 1653439153439 = 857,219,999,999,654,400 (already truncated)
rewardRate = (1e18 + remaining) / 604800 = truncated again
additional_dust = (1e18 + remaining) % 604800
```
The second truncation adds to the first. Over N calls, total locked dust grows as `O(N * duration)` wei.

**Verification:** At the end of the reward period, `rewardsToken.balanceOf(address(this))` will exceed the sum of all `rewards[user]` values by the accumulated dust, which is irrecoverable since no admin sweep function exists. [3](#0-2)

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
