Audit Report

## Title
Rewards Permanently Frozen When `totalKernelStaked` Drops to Zero During Active Reward Period - (File: contracts/KERNEL/KernelDepositPool.sol)

## Summary
In `KernelDepositPool`, the `updateReward` modifier unconditionally advances `updatedAt` to `lastTimeRewardApplicable()` even when `totalKernelStaked == 0`. Any reward tokens that accrue during a zero-staker window are permanently unclaimable and unrecoverable, because no user earns them and no admin sweep function exists. Any unprivileged staker can trigger this by being the last to call `initiateWithdrawal`.

## Finding Description
The root cause is the interaction between two components:

**`rewardPerToken()`** (L408–414): When `totalKernelStaked == 0`, it returns `rewardPerTokenStored` unchanged — no new reward-per-token is accumulated.

**`updateReward` modifier** (L232–242): Regardless of `totalKernelStaked`, it always executes `updatedAt = lastTimeRewardApplicable()`. This advances the time cursor even during periods where no rewards were distributed.

Exploit path:
1. Alice is the last staker. She calls `initiateWithdrawal(amount)` (L320), which decrements `totalKernelStaked` to 0 and triggers `updateReward`, setting `updatedAt = T1`.
2. During `[T1, T2]`, `rewardRate` continues emitting tokens (the `finishAt` timestamp is unchanged), but `rewardPerToken()` always returns the same stored value because `totalKernelStaked == 0`.
3. At `T2`, Bob calls `stake()`. The `updateReward` modifier fires: `rewardPerTokenStored` is unchanged (still zero-staker state at modifier entry, before `totalKernelStaked` is incremented), and `updatedAt` is set to `T2`.
4. The rewards for `[T1, T2]` — equal to `rewardRate × (T2 − T1)` — are permanently unaccounted for. No user can claim them.

The `notifyRewardAmount` guard (L570) only prevents starting a reward period with zero stakers; it does not prevent all stakers from exiting after the period begins. The entire admin section (L544–621) contains no token recovery or sweep function.

The contract's own NatSpec (L17–23) explicitly acknowledges this risk and relies solely on the operational assumption that tokens are always staked — an assumption any unprivileged user can break.

## Impact Explanation
**Medium — Permanent freezing of unclaimed yield.** Reward tokens that accrue during the zero-staker window are locked in the contract forever. They cannot be claimed by any user (no staker was present) and cannot be recovered by the admin (no sweep function exists). The magnitude equals `rewardRate × duration_of_empty_period`. This matches the allowed impact: *"Medium. Permanent freezing of unclaimed yield."*

## Likelihood Explanation
Any unprivileged staker can trigger this by being the last to call `initiateWithdrawal`. No special role, coordination, or external dependency is required. The scenario is realistic in low-activity periods or when a single dominant staker exits. The contract's own comment confirms this is a known operational risk with no on-chain enforcement.

## Recommendation
1. **Add an admin recovery function** to sweep undistributed reward tokens back to the treasury after the reward period ends and `totalKernelStaked` is zero, analogous to `withdrawTokens` in `KernelTop100MerkleDistributor`.
2. **Alternatively**, in the `updateReward` modifier, only advance `updatedAt` when `totalKernelStaked > 0`, so rewards for the empty period are preserved and redistributed once staking resumes:
```solidity
modifier updateReward(address _account) {
    rewardPerTokenStored = rewardPerToken();
    if (totalKernelStaked > 0) {
        updatedAt = lastTimeRewardApplicable();
    }
    ...
}
```

## Proof of Concept
```
Setup:
  - rewardRate = 100 tokens/second
  - duration = 1000 seconds (finishAt = T0 + 1000)
  - Alice stakes 1000 KERNEL at T0

At T0 + 100:
  - Alice calls initiateWithdrawal(1000)
  - totalKernelStaked = 0, updatedAt = T0 + 100

At T0 + 600 (500 seconds later):
  - Bob calls stake(1 wei)
  - updateReward fires:
      rewardPerToken() → returns rewardPerTokenStored (totalKernelStaked was 0)
      updatedAt = T0 + 600

Rewards for [T0+100, T0+600] = 100 * 500 = 50,000 tokens
→ Permanently stuck in KernelDepositPool with no recovery path.
```

Foundry test plan: deploy `KernelDepositPool`, call `notifyRewardAmount`, have Alice stake and then `initiateWithdrawal` to drain `totalKernelStaked` to 0, `warp` forward, have Bob `stake`, then assert that `rewardsToken.balanceOf(address(pool))` exceeds all claimable rewards by `rewardRate * elapsed_empty_period`.