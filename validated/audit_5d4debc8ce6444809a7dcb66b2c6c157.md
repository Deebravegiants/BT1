### Title
`notifyRewardAmount()` truncates reward rate via integer division, permanently freezing dust reward tokens — (`contracts/KERNEL/KernelDepositPool.sol`)

---

### Summary

`KernelDepositPool.notifyRewardAmount()` computes `rewardRate` via integer division of `receivedAmount / duration`. The truncated remainder (`receivedAmount % duration`) is never distributed and cannot be recovered, as the contract has no sweep or rescue function for the rewards token. This is the direct structural analog of the PA1D `_payoutEth()` bug: a balance-offset calculation causes a systematic shortfall between tokens deposited and tokens ever distributed.

---

### Finding Description

In `KernelDepositPool.notifyRewardAmount()`:

```solidity
// line 580
rewardRate = receivedAmount / duration;
// or, when rolling over a live period (line 583):
rewardRate = (receivedAmount + remaining) / duration;
```

Integer division in Solidity truncates toward zero. The total rewards that will ever be emitted over the period is `rewardRate * duration`, which is strictly less than `receivedAmount` whenever `receivedAmount % duration != 0`. The difference — up to `duration - 1` wei of the rewards token — is deposited into the contract but never assigned to any staker and never emitted.

There is no `sweep`, `recover`, `rescue`, or admin-withdrawal function for the rewards token anywhere in `KernelDepositPool`. The contract comment at lines 17–22 acknowledges the "totalKernelStaked hits zero" dust scenario but does not address the integer-division dust.

Each successive call to `notifyRewardAmount` compounds the loss: the leftover from the previous period is already sitting in the contract balance, but the new `rewardRate` is computed only from `receivedAmount` (the freshly transferred tokens), not from the full contract balance. The pre-existing dust is silently ignored again.

---

### Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

Reward tokens deposited by the admin are permanently locked in the contract. Stakers collectively receive `rewardRate * duration` tokens instead of the full `receivedAmount`. The shortfall is up to `duration - 1` tokens per `notifyRewardAmount` call and accumulates across every reward epoch. Because there is no recovery path, these tokens are irrecoverable.

---

### Likelihood Explanation

**High.** `duration` is set in seconds (e.g., 7 days = 604 800 s). Any reward amount that is not an exact multiple of `duration` — which is virtually every real-world reward deposit — produces a non-zero remainder. The condition `receivedAmount % duration != 0` is satisfied on essentially every call.

---

### Recommendation

Capture and re-inject the truncated remainder so it is distributed in the next period, or track it explicitly and allow admin recovery:

```solidity
// Option A: carry the dust forward into the next period
uint256 leftover = receivedAmount - (rewardRate * duration);
// store leftover and add it to the next notifyRewardAmount call

// Option B: add a guarded rescue function
function recoverExcessRewards(address to) external onlyRole(DEFAULT_ADMIN_ROLE) {
    uint256 distributable = rewardRate * (finishAt - block.timestamp);
    uint256 excess = rewardsToken.balanceOf(address(this)) - distributable - totalPendingRewards();
    rewardsToken.safeTransfer(to, excess);
}
```

---

### Proof of Concept

**Setup:**
- `duration = 604_800` (7 days in seconds)
- Admin calls `notifyRewardAmount(1_000_000)` (1 000 000 reward tokens)

**Execution:**

```
receivedAmount = 1_000_000
rewardRate     = 1_000_000 / 604_800 = 1          (integer division)
distributed    = 1 * 604_800         = 604_800
dust_stuck     = 1_000_000 - 604_800 = 395_200     ← permanently frozen
```

395 200 reward tokens (≈ 39.5% of the deposit) are locked in the contract with no recovery path.

**Second epoch (admin calls `notifyRewardAmount(1_000_000)` again):**

```
remaining      = (finishAt - block.timestamp) * rewardRate  (≈ 0 at period end)
rewardRate     = (1_000_000 + 0) / 604_800 = 1
```

The 395 200 tokens already sitting in the contract from the first epoch are **not** included in the new `rewardRate` calculation. They remain frozen. The dust compounds with every epoch.

**Relevant lines:** [1](#0-0) [2](#0-1)

### Citations

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
