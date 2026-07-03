Audit Report

## Title
Instant Withdrawals Can Drain `LRTUnstakingVault`, Temporarily Freezing Queued Withdrawal Funds - (File: contracts/LRTWithdrawalManager.sol)

## Summary

When `isInstantWithdrawalEnabled[asset]` is `true` and `queuedWithdrawalsBuffer[asset]` is `0` (the default), any rsETH holder can call `instantWithdrawal()` to drain the `LRTUnstakingVault` to zero. Once drained, `unlockQueue()` reverts with `AmountMustBeGreaterThanZero`, and replenishing the vault requires going through EigenLayer's `minWithdrawalDelayBlocks` (~7 days). Users who have already called `initiateWithdrawal()` and had their rsETH locked in `LRTWithdrawalManager` cannot complete their withdrawal for at least 7 additional days beyond the normal 8-day protocol delay.

## Finding Description

**Root cause:** `getAssetsAvailableForInstantWithdrawal()` does not account for `assetsCommitted[asset]` — the amount already reserved for pending queued withdrawals. When `queuedWithdrawalsBuffer[asset] == 0`, the entire vault balance is available for instant withdrawals:

```solidity
// LRTUnstakingVault.sol:235-237
uint256 vaultBalance = balanceOf(asset);
uint256 reservedBuffer = queuedWithdrawalsBuffer[asset];
availableAmount = reservedBuffer >= vaultBalance ? 0 : vaultBalance - reservedBuffer;
```

`instantWithdrawal()` enforces only this check before draining the vault:

```solidity
// LRTWithdrawalManager.sol:231-235
if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
    revert CantInstantWithdrawMoreThanAvailable();
}
unstakingVault.redeem(asset, assetAmountUnlocked);
```

Once the vault is drained, `unlockQueue()` reads the raw vault balance via `_createUnlockParams` and immediately reverts:

```solidity
// LRTWithdrawalManager.sol:849
totalAvailableAssets: unstakingVault.balanceOf(asset)
// LRTWithdrawalManager.sol:297
if (params.totalAvailableAssets == 0) revert AmountMustBeGreaterThanZero();
```

Since `completeWithdrawal()` requires the request's nonce to be below `nextLockedNonce[asset]` (line 707: `if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked()`), and `nextLockedNonce` only advances via `unlockQueue()`, users with pending queued withdrawals are fully blocked.

Replenishment requires the operator to call `NodeDelegator.initiateUnstaking()`, which queues a withdrawal from EigenLayer subject to `minWithdrawalDelayBlocks` (~7 days). Only after `completeUnstaking()` transfers assets back to the vault can `unlockQueue()` succeed. The user's rsETH remains locked in `LRTWithdrawalManager` for the entire duration.

**Exploit path:**
1. Manager enables instant withdrawals: `isInstantWithdrawalEnabled[asset] = true`; `queuedWithdrawalsBuffer[asset]` remains `0` (default)
2. User A calls `initiateWithdrawal()` — rsETH transferred to `LRTWithdrawalManager`, `assetsCommitted[asset]` incremented
3. Users B, C, D... call `instantWithdrawal()` — vault drained to 0 (no protection since buffer is 0)
4. Operator calls `unlockQueue()` — reverts: `AmountMustBeGreaterThanZero`
5. Operator calls `NodeDelegator.initiateUnstaking()` — EigenLayer queues withdrawal, ~7-day delay begins
6. During the 7-day wait, `unlockQueue()` continues to revert; User A's rsETH remains locked
7. After EigenLayer delay + `completeUnstaking()`, vault is replenished; `unlockQueue()` can proceed
8. User A must then wait an additional `withdrawalDelayBlocks` (8 days / 12 seconds, initialized at line 94) from their original request block before `completeWithdrawal()` succeeds

## Impact Explanation

Users who called `initiateWithdrawal()` before the vault was drained have their rsETH locked in `LRTWithdrawalManager` for a period exceeding the normal 8-day delay by at least 7 days (EigenLayer's `minWithdrawalDelayBlocks`). This constitutes **temporary freezing of funds** for more than one week, matching the medium-severity impact class.

## Likelihood Explanation

- `isInstantWithdrawalEnabled[asset]` must be `true` — a realistic operational state once the feature is live; it is set by the manager role, not an admin
- `queuedWithdrawalsBuffer[asset]` defaults to `0` with no enforcement requiring it to be set before enabling instant withdrawals
- Any rsETH holder can call `instantWithdrawal()` without special privileges; no coordination between attackers is required — a single large holder can drain the vault in one transaction
- The condition is repeatable: after replenishment, the vault can be drained again

## Recommendation

1. **Enforce a non-zero buffer before enabling instant withdrawals.** In `setInstantWithdrawalEnabled()`, require `queuedWithdrawalsBuffer[asset] >= assetsCommitted[asset]` when enabling.
2. **Account for `assetsCommitted` in `getAssetsAvailableForInstantWithdrawal()`.** The available amount for instant withdrawals should be `max(0, vaultBalance - max(queuedWithdrawalsBuffer[asset], assetsCommitted[asset]))`.
3. **Add a check in `instantWithdrawal()`** that ensures the vault balance after the withdrawal remains at least `assetsCommitted[asset]`, protecting funds already reserved for queued withdrawals.

## Proof of Concept

```
// Foundry fork test outline
// 1. Deploy/fork with LRTUnstakingVault funded with 100 ETH
// 2. Manager calls setInstantWithdrawalEnabled(ETH, true)
//    queuedWithdrawalsBuffer[ETH] == 0 (default)
// 3. User A calls initiateWithdrawal(ETH, rsETH_A)
//    → assetsCommitted[ETH] += expectedAmount_A
//    → rsETH_A locked in LRTWithdrawalManager
// 4. Attacker calls instantWithdrawal(ETH, rsETH_large) in a loop
//    → getAssetsAvailableForInstantWithdrawal returns 100 ETH (buffer=0)
//    → vault drained to 0
// 5. Operator calls unlockQueue(ETH, ...)
//    → _createUnlockParams: totalAvailableAssets = unstakingVault.balanceOf(ETH) = 0
//    → REVERT: AmountMustBeGreaterThanZero ✓
// 6. vm.roll(block.number + 7 days / 12) // simulate EigenLayer delay
//    → unlockQueue() still reverts (vault still empty)
// 7. Assert: User A cannot call completeWithdrawal() (WithdrawalLocked revert)
// 8. After completeUnstaking() replenishes vault, unlockQueue() succeeds
//    → User A's total lock-up = EigenLayer delay + withdrawalDelayBlocks > 15 days
```