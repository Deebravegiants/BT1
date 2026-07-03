Audit Report

## Title
Unscaled `rewardRate` Causes Permanent Freezing of Unclaimed Yield - (File: contracts/KERNEL/KernelDepositPool.sol)

## Summary

`KernelDepositPool.notifyRewardAmount()` stores `rewardRate` as a plain integer division result with no `1e18` scaling. This causes two irreversible losses: a guaranteed dust remainder locked on every reward notification, and per-checkpoint accumulator increments that round to zero whenever `rewardRate * timeDelta * 1e18 < totalKernelStaked`. Because `updatedAt` advances regardless, the rewards for those intervals are permanently unrecoverable.

## Finding Description

`rewardRate` is set without precision scaling:

```solidity
rewardRate = receivedAmount / duration;           // L580
rewardRate = (receivedAmount + remaining) / duration; // L583
``` [1](#0-0) 

`rewardPerToken()` then multiplies by `DECIMAL_PRECISION` downstream:

```solidity
return rewardPerTokenStored
    + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
    / totalKernelStaked;
``` [2](#0-1) 

The `updateReward` modifier unconditionally advances `updatedAt` to `lastTimeRewardApplicable()` before any check:

```solidity
rewardPerTokenStored = rewardPerToken();
updatedAt = lastTimeRewardApplicable();
``` [3](#0-2) 

Two distinct loss paths follow:

1. **Dust lock**: `receivedAmount % duration` wei are silently discarded on every `notifyRewardAmount` call and remain permanently locked — there is no sweep or rescue function.

2. **Zero-increment checkpoints**: Whenever `rewardRate * timeDelta * 1e18 < totalKernelStaked`, the accumulator increment rounds to zero. `updatedAt` is still advanced, so the rewards that should have accrued during that interval are permanently lost. The `rewardRate == 0` guard at L586 only blocks the trivially zero case; it does not prevent `rewardRate = 1` with a large staked supply. [4](#0-3) 

## Impact Explanation

**Medium — Permanent freezing of unclaimed yield.**

Reward tokens deposited via `notifyRewardAmount` are transferred into the contract but a portion can never be claimed by stakers: `rewardPerTokenStored` never advances for the affected intervals, so `earned()` returns zero for those periods and `getReward()` transfers nothing. The tokens remain in the contract with no recovery path.

## Likelihood Explanation

No attacker action is required. Every call to `stake`, `initiateWithdrawal`, or `getReward` triggers `updateReward`, which advances `updatedAt` and potentially drops a zero-increment checkpoint. The condition is reachable under normal protocol usage whenever the reward token has fewer than 18 decimals (USDC, USDT) or when the reward amount is small relative to `duration`. The scenario is realistic and repeatable across every reward period.

## Recommendation

Scale `rewardRate` by `DECIMAL_PRECISION` at storage time:

```solidity
// notifyRewardAmount():
rewardRate = receivedAmount * DECIMAL_PRECISION / duration;
// renewal:
uint256 remaining = (finishAt - block.timestamp) * rewardRate; // already scaled
rewardRate = (receivedAmount * DECIMAL_PRECISION + remaining) / duration;
```

Then remove the `* DECIMAL_PRECISION` factor from `rewardPerToken()`:

```solidity
return rewardPerTokenStored
    + (rewardRate * (lastTimeRewardApplicable() - updatedAt))
    / totalKernelStaked;
```

This is the standard Synthetix pattern: precision is enforced at the rate-storage site, not downstream.

## Proof of Concept

**Parameters**: `duration = 2_592_000` (30 days), reward token = USDC (6 decimals), `receivedAmount = 3_000_000` (3 USDC), `totalKernelStaked = 1e19` (10 KERNEL).

**Step 1 — dust lock**:
```
rewardRate = 3_000_000 / 2_592_000 = 1
locked forever = 3_000_000 - 1 * 2_592_000 = 408_000 wei ≈ 0.408 USDC
```

**Step 2 — per-checkpoint nullification**:
Any user calls `stake` (or any `updateReward`-gated function) once per second. Each call:
```
increment = rewardRate * timeDelta * 1e18 / totalKernelStaked
           = 1 * 1 * 1e18 / 1e19 = 0
```
`rewardPerTokenStored` never increases. After 30 days, `earned()` returns 0 for all stakers despite 2.592 USDC having been deposited.

**Step 3 — funds locked**:
`getReward()` transfers 0. The 2.592 USDC (minus the 0.408 USDC dust) is permanently locked in the contract.

**Foundry test sketch**:
```solidity
function test_rewardRatePrecisionLoss() public {
    // Setup: mint USDC, notifyRewardAmount(3_000_000, 2_592_000)
    // Assert rewardRate == 1
    // Warp 1 second, call stake(0) to trigger updateReward
    // Assert rewardPerTokenStored == 0
    // Warp full duration, call getReward()
    // Assert USDC balance of staker == 0
    // Assert USDC balance of contract == 3_000_000
}
```

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L232-241)
```text
    modifier updateReward(address _account) {
        rewardPerTokenStored = rewardPerToken();
        updatedAt = lastTimeRewardApplicable();

        if (_account != address(0)) {
            rewards[_account] = earned(_account);
            userRewardPerTokenPaid[_account] = rewardPerTokenStored;
        }

        _;
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L408-414)
```text
    function rewardPerToken() public view returns (uint256) {
        if (totalKernelStaked == 0) {
            return rewardPerTokenStored;
        }
        return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
            / totalKernelStaked;
    }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L579-584)
```text
        if (block.timestamp >= finishAt) {
            rewardRate = receivedAmount / duration;
        } else {
            uint256 remaining = (finishAt - block.timestamp) * rewardRate;
            rewardRate = (receivedAmount + remaining) / duration;
        }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L586-586)
```text
        if (rewardRate == 0) revert RewardRateZero();
```
