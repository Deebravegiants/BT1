Audit Report

## Title
Reward Accumulation Permanently Frozen via Integer Truncation in `rewardPerToken()` When `dt` Is Kept Small - (File: `contracts/KERNEL/KernelDepositPool.sol`)

## Summary

`KernelDepositPool.rewardPerToken()` computes the per-token reward increment as `rewardRate * dt * DECIMAL_PRECISION / totalKernelStaked`. The `updateReward` modifier resets `updatedAt` to `lastTimeRewardApplicable()` on every invocation. An attacker who calls `stake(1)` every block keeps `dt` pinned to ~12 seconds; when `rewardRate * 12 * 1e18 < totalKernelStaked`, Solidity integer division truncates the increment to zero, `rewardPerTokenStored` never advances, and all stakers earn zero rewards for the entire distribution window. The deposited reward tokens have no recovery path and are permanently frozen.

## Finding Description

`rewardPerToken()` accumulates the global reward index:

```solidity
// contracts/KERNEL/KernelDepositPool.sol L408-413
return rewardPerTokenStored + (rewardRate * (lastTimeRewardApplicable() - updatedAt) * DECIMAL_PRECISION)
    / totalKernelStaked;
```

The `updateReward` modifier, applied to every state-changing function (`stake`, `stakeFor`, `initiateWithdrawal`, `getReward`), resets the clock before executing the function body:

```solidity
// contracts/KERNEL/KernelDepositPool.sol L232-234
modifier updateReward(address _account) {
    rewardPerTokenStored = rewardPerToken();
    updatedAt = lastTimeRewardApplicable();   // resets dt to 0
```

`rewardRate` is set by integer division in `notifyRewardAmount`:

```solidity
// contracts/KERNEL/KernelDepositPool.sol L579-580
if (block.timestamp >= finishAt) {
    rewardRate = receivedAmount / duration;
```

`stake()` enforces only `_amount != 0`, so `stake(1)` is valid:

```solidity
// contracts/KERNEL/KernelDepositPool.sol L281-282
function stake(uint256 _amount) external nonReentrant updateReward(msg.sender) {
    if (_amount == 0) revert AmountZero();
```

**Exploit path:**
1. Admin calls `notifyRewardAmount(40_000e6)` with USDC (6 decimals), `duration = 604800`. `rewardRate = 40_000e6 / 604800 = 66137`.
2. `totalKernelStaked = 1_000_000e18` (1e24 wei).
3. Attacker calls `stake(1)` every Ethereum block (~12 s).
4. Each call: `dt = 12`, increment = `66137 * 12 * 1e18 / 1e24 = 793644e18 / 1e24 = 0` (truncated). `updatedAt` is reset to `block.timestamp`.
5. After 604,800 seconds, `rewardPerTokenStored = 0`. `earned()` returns 0 for every staker. `getReward()` transfers nothing.
6. The 40,000 USDC is permanently locked — no sweep or token-recovery function exists, and `notifyRewardAmount` uses `rewardRate` (not actual balance) so the stranded tokens are never redistributed.

No existing guard prevents this: `nonReentrant` only blocks same-transaction reentrancy; there is no minimum `dt`, no minimum stake size beyond zero, and no dust accumulation mechanism.

## Impact Explanation

**Medium — Permanent freezing of unclaimed yield.** `rewardPerTokenStored` remains zero for the full reward window. Every staker's `earned()` returns zero and `getReward()` transfers nothing. The reward tokens deposited via `notifyRewardAmount` are permanently locked in the contract with no recovery path. This matches the allowed impact "Medium. Permanent freezing of unclaimed yield."

## Likelihood Explanation

The attack requires only a public `stake(uint256)` call with `_amount = 1` — no privileged role. The truncation condition (`rewardRate * 12 * 1e18 < totalKernelStaked`) is realistic for any low-decimal reward token (USDC, USDT) paired with a large staked supply, a common operational configuration. Gas cost is the primary deterrent for regular users, but a block proposer/validator incurs zero gas cost and can sustain the attack for the full 7-day window (50,400 blocks) at no expense. The condition can also be triggered inadvertently by normal high-frequency user activity without any malicious intent.

## Recommendation

1. **Accumulate remainder dust**: Track the fractional reward that is truncated each call and add it back to the next period's `rewardRate` calculation, as Synthetix does in `notifyRewardAmount`.
2. **Higher precision at storage time**: Store `rewardRate * DECIMAL_PRECISION` and divide only at read time, eliminating per-second truncation.
3. **Minimum `dt` guard**: Skip the `rewardPerTokenStored` update if `dt` is below a threshold (e.g., 1 hour), preventing sub-threshold calls from resetting `updatedAt` without contributing meaningful reward.
4. **Token recovery function**: Add an admin-callable sweep for stranded reward tokens so any frozen balance can be redistributed.

## Proof of Concept

**Setup (Foundry fork test):**
```solidity
// duration = 604800 (7 days)
// rewardToken = MockUSDC (6 decimals)
// admin calls notifyRewardAmount(40_000e6)
// → rewardRate = 66137
// totalKernelStaked = 1_000_000e18
```

**Attack loop (vm.roll + vm.warp every 12 s for 604800 s):**
```solidity
for (uint i = 0; i < 50400; i++) {
    vm.warp(block.timestamp + 12);
    vm.roll(block.number + 1);
    vm.prank(attacker);
    pool.stake(1);
    assertEq(pool.rewardPerTokenStored(), 0); // never advances
}
// After full reward window:
assertEq(pool.earned(victim), 0);
vm.prank(victim);
pool.getReward(); // transfers 0
assertEq(usdc.balanceOf(victim), 0);
assertEq(usdc.balanceOf(address(pool)), 40_000e6); // permanently locked
```