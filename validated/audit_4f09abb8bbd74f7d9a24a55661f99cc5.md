Audit Report

## Title
Uninitialized `withdrawalDelay` Allows Same-Block Principal Recovery After Reward Capture - (File: `contracts/KERNEL/KernelDepositPool.sol`)

## Summary
`withdrawalDelay` is declared as a plain `uint256` state variable and is never assigned in `initialize()`, leaving it at `0`. With a zero delay, `initiateWithdrawal()` sets `unlockTime = block.timestamp`, and the `claimWithdrawal()` guard (`block.timestamp < unlockTime`) is immediately satisfied in the same block. An unprivileged attacker can stake a dominant share, wait one block for rewards to accrue, claim rewards via `getReward()`, then recover their full principal via `initiateWithdrawal()` + `claimWithdrawal()` with no lock-up cost — stealing yield from legitimate long-term stakers.

## Finding Description
`withdrawalDelay` is declared at L96 with no default:
```solidity
uint256 public withdrawalDelay;
```
`initialize()` (L259–271) sets only `kernelToken`, `rewardsToken`, and access control roles — `withdrawalDelay` is never touched. `notifyRewardAmount()` (L566–592) guards only against `totalKernelStaked == 0`; there is no check that `withdrawalDelay > 0` before a reward period begins. `setWithdrawalDelay()` (L598–604) explicitly rejects `0`, meaning the initial zero state can never be restored once set, but there is no enforcement that it must be set before rewards start.

With `withdrawalDelay == 0`, `initiateWithdrawal()` at L330 computes:
```solidity
uint256 unlockTime = block.timestamp + withdrawalDelay; // == block.timestamp
```
The guard in `claimWithdrawal()` at L355:
```solidity
if (block.timestamp < withdrawal.unlockTime) revert WithdrawalNotReady();
```
evaluates as `block.timestamp < block.timestamp` → `false`, so the revert is never triggered and the withdrawal is claimable immediately.

**Note:** `maxNumberOfWithdrawalsPerUser` is also uninitialized (defaults to `0`), which means `initiateWithdrawal()` reverts at L323 (`0 >= 0`) until the admin calls `setMaxNumberOfWithdrawalsPerUser`. However, this is a required setup step for the contract to be usable at all — once the admin enables withdrawals by setting this value, the `withdrawalDelay == 0` window is exploitable if `setWithdrawalDelay` was not also called.

## Impact Explanation
**High — Theft of unclaimed yield.** The attacker captures a disproportionate share of the active reward period's yield by holding a dominant stake for a minimal time window (one or more blocks), then exits with full principal and no lock-up penalty. Legitimate long-term stakers receive a reduced share of rewards for the same period. This matches the allowed impact "Theft of unclaimed yield."

## Likelihood Explanation
**Medium.** The preconditions are: (1) admin has called `setMaxNumberOfWithdrawalsPerUser` (required for any withdrawal to function), (2) admin has called `notifyRewardAmount` to start a reward period, and (3) admin has not yet called `setWithdrawalDelay`. This ordering is realistic — the contract comment at L19–22 explicitly instructs the admin to ensure tokens are staked before calling `notifyRewardAmount`, but places no analogous requirement on `withdrawalDelay`. Any on-chain observer can detect `withdrawalDelay == 0` and an active `rewardRate > 0` and execute the attack permissionlessly.

## Recommendation
1. **Initialize `withdrawalDelay` to a safe non-zero value** (e.g., `7 days`) inside `initialize()`.
2. **Add a guard in `notifyRewardAmount()`** that reverts if `withdrawalDelay == 0`:
   ```solidity
   if (withdrawalDelay == 0) revert InvalidWithdrawalDelay();
   ```
3. Optionally, initialize `maxNumberOfWithdrawalsPerUser` to a safe default (e.g., `MAX_WITHDRAWALS_PER_USER`) in `initialize()` to avoid a separate uninitialized-variable footgun.

## Proof of Concept
```solidity
// Preconditions:
//   - withdrawalDelay == 0 (never initialized)
//   - maxNumberOfWithdrawalsPerUser > 0 (admin called setMaxNumberOfWithdrawalsPerUser)
//   - Active reward period (admin called notifyRewardAmount)

// 1. Attacker stakes large amount
kernelDepositPool.stake(1_000_000e18);

// 2. Advance 1 block so rewards accrue (rewardPerToken increases)
vm.roll(block.number + 1);
vm.warp(block.timestamp + 12);

// 3. Claim rewards — attacker captures majority share proportional to stake
kernelDepositPool.getReward();

// 4. Initiate withdrawal — unlockTime = block.timestamp + 0 = block.timestamp
kernelDepositPool.initiateWithdrawal(1_000_000e18);

// 5. Claim withdrawal in same block — block.timestamp < block.timestamp is false, no revert
kernelDepositPool.claimWithdrawal(1);

// Result: attacker recovers full 1_000_000e18 principal + disproportionate rewards
// Legitimate stakers earned near-zero rewards for the same 12-second window
```