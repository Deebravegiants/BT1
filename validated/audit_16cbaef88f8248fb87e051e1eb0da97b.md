Audit Report

## Title
Low-Decimal Reward Token Precision Loss Permanently Freezes Unclaimed Yield - (File: contracts/KERNEL/KernelDepositPool.sol)

## Summary

`KernelDepositPool` stores `rewardRate` in raw token units with no decimal upscaling. When `rewardsToken` has fewer than 18 decimals (e.g., USDC at 6 decimals), the per-second increment to `rewardPerTokenStored` rounds to zero in integer arithmetic while `updatedAt` still advances, permanently destroying the rewards for each affected time window. Normal user activity is sufficient to trigger total reward loss.

## Finding Description

`notifyRewardAmount()` sets `rewardRate` as raw received token units divided by duration, with no upscaling:

```solidity
// L580
rewardRate = receivedAmount / duration;
```

`rewardPerToken()` then computes the accumulator increment as:

```solidity
// L412-413
return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
    / totalKernelStaked;
```

The `updateReward` modifier, applied to every state-changing function (`stake`, `initiateWithdrawal`, `getReward`, `notifyRewardAmount`), unconditionally snapshots both values:

```solidity
// L233-234
rewardPerTokenStored = rewardPerToken();   // may be unchanged (rounded to 0)
updatedAt = lastTimeRewardApplicable();    // always advances
```

**Concrete arithmetic with USDC (6 decimals) and realistic TVL:**

- `receivedAmount = 1_209_600_000` (1,209.6 USDC)
- `duration = 604_800` (1 week) → `rewardRate = 2_000`
- `totalKernelStaked = 1_000_000e18`
- Per 2-second block: `2_000 × 2 × 1e18 / 1_000_000e18 = 4e21 / 1e24 = 0`

`rewardPerTokenStored` does not increase, but `updatedAt` advances by 2 seconds. The rewards for that window are permanently unrecoverable. Any call interval shorter than `totalKernelStaked / (rewardRate × DECIMAL_PRECISION) = 1_000_000e18 / (2_000 × 1e18) = 500 seconds` causes the same loss.

There is no decimal restriction on `rewardsToken` in `initialize()`:

```solidity
// L269-270
kernelToken = IERC20(_kernelToken);
rewardsToken = IERC20(_rewardToken);
```

No existing guard prevents this. The `rewardRate == 0` check at L586 only catches the case where `receivedAmount < duration`, not the per-block rounding loss.

## Impact Explanation

**Medium — Permanent freezing of unclaimed yield.** KERNEL stakers receive zero rewards for any low-decimal reward token (USDC, USDT) distributed through this contract. The reward tokens remain locked in the contract with no recovery path for stakers, as there is no admin rescue function for stranded reward tokens.

## Likelihood Explanation

The `rewardsToken` is set at initialization with no decimal restriction. USDC and USDT are the most common staking reward tokens in DeFi. No deliberate attack is required: any organic user interaction (staking, withdrawing, claiming) at a frequency above the rounding threshold silently destroys yield. A griefer holding 1 wei of KERNEL can guarantee total loss by calling `stake(1)` each block, but even without griefing, the threshold of ~500 seconds between interactions is easily exceeded in a live protocol.

## Recommendation

Upscale `rewardRate` by a precision multiplier (e.g., `1e12`) when storing it in `notifyRewardAmount`, and divide by the same multiplier when transferring rewards in `getReward`. This is the standard fix for Synthetix-fork contracts supporting sub-18-decimal reward tokens. Alternatively, enforce that `rewardsToken` must have exactly 18 decimals in `initialize()`, or add a per-token decimal normalization factor computed at initialization time.

## Proof of Concept

1. Admin calls `setRewardsDuration(604800)` (1 week).
2. Admin calls `notifyRewardAmount(1_209_600_000)` with USDC as `rewardsToken`.
   - `rewardRate = 1_209_600_000 / 604_800 = 2_000`
3. `totalKernelStaked = 1_000_000e18` (realistic TVL).
4. Any user calls `stake(1)` (or `getReward()`, or `initiateWithdrawal()`) at any interval shorter than 500 seconds.
   - Each call triggers `updateReward`: `rewardPerToken()` returns `rewardPerTokenStored + 0`, but `updatedAt` advances.
5. After 1 week, `rewardPerTokenStored` is still 0. All stakers call `getReward()` and receive 0 USDC.
6. 1,209.6 USDC is permanently frozen in the contract.

**Foundry test plan:** Deploy `KernelDepositPool` with a mock 6-decimal ERC20 as `rewardsToken`. Call `notifyRewardAmount` with the above parameters. Warp forward 2 seconds and call `stake(1)` in a loop for 604,800 iterations (or use `vm.warp` in steps). Assert `rewardPerTokenStored == 0` and that `getReward()` transfers 0 tokens to a staker who held throughout the period.