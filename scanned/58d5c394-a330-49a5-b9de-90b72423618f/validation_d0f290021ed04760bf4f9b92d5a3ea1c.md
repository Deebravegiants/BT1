### Title
Reward Tokens Permanently Locked in `KernelDepositPool` Due to Integer Division Truncation in `notifyRewardAmount` - (File: `contracts/KERNEL/KernelDepositPool.sol`)

---

### Summary

`KernelDepositPool.notifyRewardAmount` computes `rewardRate = receivedAmount / duration` using integer division. The remainder `receivedAmount % duration` is transferred into the contract but can never be distributed to stakers, permanently locking those reward tokens. This is the direct analog of the TroveManager emission-loss pattern: rewards are allocated in full but only a truncated subset is ever claimable.

---

### Finding Description

In `notifyRewardAmount`, the reward rate is set via integer division:

```solidity
// line 580
rewardRate = receivedAmount / duration;
// line 583 (mid-period top-up)
rewardRate = (receivedAmount + remaining) / duration;
```

The total rewards that will ever be emitted over the full period is `rewardRate * duration`. Because Solidity truncates integer division:

```
rewardRate * duration = (receivedAmount / duration) * duration ≤ receivedAmount
```

The difference — `receivedAmount % duration` — is transferred into the contract on line 574 (`rewardsToken.safeTransferFrom`) but is never accounted for in any subsequent distribution. There is no `withdrawTokens`, sweep, or recovery function in `KernelDepositPool` to reclaim these stranded tokens. They are permanently locked.

The same truncation recurs on every mid-period top-up call (line 583), compounding the loss across reward epochs.

---

### Impact Explanation

**Impact: Medium — Permanent freezing of unclaimed yield.**

Every call to `notifyRewardAmount` silently discards up to `duration − 1` reward tokens. For reward tokens with low decimal precision (e.g., a 6-decimal token) and long durations, the per-call loss is material:

| Scenario | `receivedAmount` | `duration` | Lost per call |
|---|---|---|---|
| 6-decimal token, 7-day period | 1,000,000 × 10⁶ | 604,800 s | 265,600 units ≈ 0.27 tokens |
| 6-decimal token, 30-day period | 1,000,000 × 10⁶ | 2,592,000 s | ~1.3 tokens |
| 18-decimal token, 7-day period | 1,000,000 × 10¹⁸ | 604,800 s | ~256,000 wei (negligible) |

For 18-decimal tokens the per-call loss is negligible in isolation, but it accumulates across every reward epoch and is irrecoverable. For lower-precision reward tokens the loss is immediately significant. In either case the tokens are permanently stranded with no admin recovery path.

---

### Likelihood Explanation

**Likelihood: High.** The truncation occurs unconditionally on every invocation of `notifyRewardAmount`. No special conditions, attacker coordination, or timing is required. Any reward claimant (staker) is affected automatically.

---

### Recommendation

After computing `rewardRate`, calculate the leftover dust and carry it forward into the next period or track it separately:

```solidity
uint256 leftover = receivedAmount - (rewardRate * duration);
// Option A: roll into next period by adding to contract balance tracking
// Option B: emit an event and allow admin to re-inject it next epoch
```

Alternatively, use a higher-precision intermediate (e.g., multiply `receivedAmount` by a scaling factor before dividing) and divide back when distributing, as done in many modern staking contracts.

---

### Proof of Concept

**Step-by-step:**

1. Admin calls `setRewardsDuration(604800)` (7 days).
2. A staker stakes 1,000 KERNEL tokens.
3. Admin calls `notifyRewardAmount(1_000_000e6)` (1M units of a 6-decimal reward token).
4. Inside `notifyRewardAmount`:
   - `receivedAmount = 1_000_000_000_000` (1M × 10⁶)
   - `rewardRate = 1_000_000_000_000 / 604_800 = 1_653_439`
   - Tokens that will be emitted: `1_653_439 × 604_800 = 999_999_667_200`
   - **Permanently locked: `1_000_000_000_000 − 999_999_667_200 = 332_800` units (0.33 tokens)**
5. After the full 7-day period, the staker calls `getReward()` and receives `999_999_667_200` units.
6. The remaining `332_800` units remain in the contract with no mechanism to recover or redistribute them.
7. On the next call to `notifyRewardAmount`, the same truncation recurs, compounding the locked balance.

**Relevant code locations:** [1](#0-0) 

The `rewardRate` integer division truncation at line 580 and 583 is the root cause. [2](#0-1) 

`rewardPerToken()` accumulates only `rewardRate * elapsed`, never recovering the truncated dust. [3](#0-2) 

`earned()` is bounded by the truncated `rewardPerToken`, so stakers can never claim the locked remainder.

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L408-413)
```text
    function rewardPerToken() public view returns (uint256) {
        if (totalKernelStaked == 0) {
            return rewardPerTokenStored;
        }
        return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
            / totalKernelStaked;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L421-423)
```text
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
