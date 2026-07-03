### Title
Rewards Spread Across Wrong Period When New Reward Added During Active Distribution - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary
`KernelDepositPool.notifyRewardAmount` uses the same leftover-rollover math as the referenced report. When a second reward is added while the first distribution window is still active, the remaining first-period rewards are diluted across a brand-new full `duration`. Early stakers receive fewer rewards than they are entitled to during the original window, and stakers who join after the original `finishAt` can permanently capture a share of those first-period rewards.

### Finding Description
In `notifyRewardAmount`, when `block.timestamp < finishAt` (an active reward period exists), the contract computes:

```solidity
uint256 remaining = (finishAt - block.timestamp) * rewardRate;
rewardRate = (receivedAmount + remaining) / duration;
// ...
finishAt = block.timestamp + duration;
``` [1](#0-0) 

The leftover rewards from the first period (`remaining`) are merged with the new reward amount and then spread uniformly over a fresh full `duration`. The original `finishAt` is discarded and replaced with `block.timestamp + duration`. This means:

1. Rewards that should have been fully distributed by the original `finishAt` are now stretched to the new `finishAt` (original `finishAt + duration`).
2. Any staker who enters between the original `finishAt` and the new `finishAt` accrues a share of the first-period's leftover rewards, even though those rewards were earned before they staked.

### Impact Explanation
Early stakers permanently lose a portion of their entitled first-period rewards to late stakers who join after the original distribution window should have closed. This constitutes **theft of unclaimed yield** (High) or at minimum **permanent freezing of unclaimed yield** (Medium), depending on whether late stakers actually enter and claim the diluted rewards.

Concretely, using the same timeline as the report (30-day `duration`, second reward added at day 15):
- At day 30, an early staker receives only `A + B/2 + C/2` instead of the correct `A + B + C/2`.
- The missing `B/2` is spread across days 30–45 and can be partially captured by any staker who joins on day 30 or later.

### Likelihood Explanation
The admin calling `notifyRewardAmount` a second time while the first window is still active is a routine, expected protocol operation (e.g., topping up rewards mid-period). No malicious intent or compromise is required. The math error fires on every such legitimate call. [2](#0-1) 

### Recommendation
Before merging leftover rewards, do not extend `finishAt` beyond the original deadline for the leftover portion. One approach is to track the leftover separately and only begin distributing the new reward after the current period ends (queue-based approach as suggested in the original report). Alternatively, cap the new `rewardRate` so that the leftover is fully paid out by the original `finishAt` and only the new reward is spread over the new `duration`.

### Proof of Concept
Scenario with `duration = 30 days`:

```
          [----A----|----B----]           (1st reward period)
                    [---------C---------] (2nd reward period)
    Day:  0        15         30       45
```

1. Admin calls `notifyRewardAmount(10_000e18)` at day 0. `rewardRate = 10_000e18 / 30 days`. `finishAt = day 30`.
2. Alice stakes at day 0.
3. At day 15, Alice claims rewards → receives `A ≈ 5_000e18` (correct).
4. Admin calls `notifyRewardAmount(10_000e18)` at day 15 (legitimate top-up).
   - `remaining = (day30 - day15) * rewardRate = 5_000e18`
   - `rewardRate = (10_000e18 + 5_000e18) / 30 days`
   - `finishAt = day 45`
5. At day 30, Alice claims → receives `≈ 7_500e18` (only `B/2 + C/2`), not the correct `B + C/2 = 10_000e18`.
6. Malicious staker stakes at day 30, claims at day 45 → receives `≈ 7_500e18`, which includes `B/2` that belongs to Alice.

Alice permanently loses `≈ 2_500e18` of first-period rewards to the late staker. [3](#0-2)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L566-566)
```text
    function notifyRewardAmount(uint256 _amount) external onlyRole(DEFAULT_ADMIN_ROLE) updateReward(address(0)) {
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L579-588)
```text
        if (block.timestamp >= finishAt) {
            rewardRate = receivedAmount / duration;
        } else {
            uint256 remaining = (finishAt - block.timestamp) * rewardRate;
            rewardRate = (receivedAmount + remaining) / duration;
        }

        if (rewardRate == 0) revert RewardRateZero();

        finishAt = block.timestamp + duration;
```
