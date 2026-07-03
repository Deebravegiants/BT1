### Title
Reducing `withdrawalDelay` Does Not Apply to Pending Withdrawals, Temporarily Freezing User KERNEL Tokens - (File: contracts/KERNEL/KernelDepositPool.sol)

### Summary

`KernelDepositPool.initiateWithdrawal()` snapshots `unlockTime = block.timestamp + withdrawalDelay` into each `Withdrawal` struct at the moment of initiation. `claimWithdrawal()` enforces only the stored per-withdrawal `unlockTime`, never consulting the current global `withdrawalDelay`. When the admin reduces `withdrawalDelay` via `setWithdrawalDelay()`, all previously queued withdrawals remain locked until their original, longer `unlockTime` elapses, even though the protocol now permits a shorter delay.

### Finding Description

`initiateWithdrawal()` computes and stores the absolute unlock timestamp at call time:

```solidity
// KernelDepositPool.sol line 330
uint256 unlockTime = block.timestamp + withdrawalDelay;

withdrawals[withdrawalId] = Withdrawal({
    user: msg.sender, amount: _amount, unlockTime: unlockTime, ...
});
```

`claimWithdrawal()` enforces only this stored value:

```solidity
// KernelDepositPool.sol line 355-357
if (block.timestamp < withdrawal.unlockTime) {
    revert WithdrawalNotReady();
}
```

The admin can reduce `withdrawalDelay` at any time (down to 1 second):

```solidity
// KernelDepositPool.sol line 598-603
function setWithdrawalDelay(uint256 _withdrawalDelay) external onlyRole(DEFAULT_ADMIN_ROLE) {
    if (_withdrawalDelay == 0) revert InvalidWithdrawalDelay();
    if (_withdrawalDelay > MAX_WITHDRAWAL_DELAY) revert MaximumWithdrawalDelayExceeded();
    withdrawalDelay = _withdrawalDelay;
    ...
}
```

After the reduction, `claimWithdrawal()` still enforces the old, longer `unlockTime` baked into each pending `Withdrawal` struct. There is no code path that re-evaluates pending withdrawals against the new global delay.

### Impact Explanation

Users who initiated withdrawals under a longer delay (up to 30 days) are temporarily frozen out of their KERNEL tokens even after the protocol's required delay has been shortened. Their staked KERNEL was already deducted from `balanceOf` and `totalKernelStaked` at initiation time, so they hold neither staked position nor liquid tokens for the excess duration. This constitutes a **temporary freezing of funds** (Medium).

### Likelihood Explanation

The admin reducing `withdrawalDelay` is a realistic operational action (e.g., improving UX, responding to competitive pressure, or emergency liquidity needs). Any user who initiated a withdrawal before the reduction is automatically affected with no action required on their part. The maximum excess lock duration equals the difference between the old and new delay, up to 30 days.

### Recommendation

In `claimWithdrawal()`, allow the claim if either the stored `unlockTime` has passed **or** the current global `withdrawalDelay` has elapsed since `initiateWithdrawal` was called. Since the `Withdrawal` struct does not store the initiation timestamp separately, the simplest fix is to store `withdrawalStartTime` in the struct and check `min(withdrawal.unlockTime, withdrawal.withdrawalStartTime + withdrawalDelay)`:

```solidity
// Modified check in claimWithdrawal():
uint256 effectiveUnlockTime = withdrawal.withdrawalStartTime + withdrawalDelay;
if (effectiveUnlockTime > withdrawal.unlockTime) effectiveUnlockTime = withdrawal.unlockTime;
if (block.timestamp < effectiveUnlockTime) revert WithdrawalNotReady();
```

Alternatively, store only `withdrawalStartTime` and always compute the unlock dynamically from the current `withdrawalDelay`, mirroring how `LRTWithdrawalManager` handles its block-based delay.

### Proof of Concept

1. Admin deploys `KernelDepositPool` with `withdrawalDelay = 30 days`.
2. Alice calls `initiateWithdrawal(100e18)`. Her `Withdrawal.unlockTime` is set to `block.timestamp + 30 days`. Her `balanceOf` is reduced immediately.
3. Admin calls `setWithdrawalDelay(1 days)` — the protocol now only requires a 1-day delay.
4. Bob calls `initiateWithdrawal(100e18)` after the change. His `unlockTime = block.timestamp + 1 day`.
5. After 1 day, Bob successfully calls `claimWithdrawal` and receives his KERNEL.
6. Alice calls `claimWithdrawal` and receives `WithdrawalNotReady` — she must wait the remaining ~29 days despite the protocol no longer requiring it. Alice holds neither staked KERNEL nor liquid KERNEL for this period.

**Relevant lines:** [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/KERNEL/KernelDepositPool.sol (L329-334)
```text
        uint256 withdrawalId = ++withdrawalCounter;
        uint256 unlockTime = block.timestamp + withdrawalDelay;

        withdrawals[withdrawalId] = Withdrawal({
            user: msg.sender, amount: _amount, unlockTime: unlockTime, claimed: false, withdrawalId: withdrawalId
        });
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L355-357)
```text
        if (block.timestamp < withdrawal.unlockTime) {
            revert WithdrawalNotReady();
        }
```

**File:** contracts/KERNEL/KernelDepositPool.sol (L598-603)
```text
    function setWithdrawalDelay(uint256 _withdrawalDelay) external onlyRole(DEFAULT_ADMIN_ROLE) {
        if (_withdrawalDelay == 0) revert InvalidWithdrawalDelay();
        if (_withdrawalDelay > MAX_WITHDRAWAL_DELAY) revert MaximumWithdrawalDelayExceeded();

        withdrawalDelay = _withdrawalDelay;
        emit WithdrawalDelayUpdated(_withdrawalDelay);
```
