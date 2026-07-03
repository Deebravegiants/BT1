Audit Report

## Title
Counter Desync via `initialize2` Seeding Skips Zero-`expectedAssetAmount` Requests, Causing Underflow Revert in `_processWithdrawalCompletion` - (File: contracts/LRTWithdrawalManager.sol)

## Summary
`UnlockedWithdrawalsInitializer.processChunk()` seeds `unlockedWithdrawalsCount` by counting only requests where `expectedAssetAmount > 0`, but `_unlockWithdrawalRequests` increments the counter for every unlocked request regardless of payout amount. If any request was unlocked with a zero payout (possible when `_calculatePayoutAmount` truncates to 0), the seeded counter is lower than the true number of completable requests. Once the counter reaches zero, every subsequent `completeWithdrawal` call for a still-valid unlocked request reverts with an arithmetic underflow panic (0x11), temporarily freezing those users' funds.

## Finding Description
`_unlockWithdrawalRequests` (line 798–809) computes `payoutAmount = _calculatePayoutAmount(request, rsETHPrice, assetPrice)`. The guard at line 800 is `if (availableAssetAmount < payoutAmount) break` — when `payoutAmount == 0`, this condition is `uint256 < 0`, which is always false, so execution continues. The request is stored with `request.expectedAssetAmount = 0` and `unlockedWithdrawalsCount[asset]++` is unconditionally executed at line 809.

`_calculatePayoutAmount` (line 833) computes `currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice`. Integer division truncates to 0 when `rsETHUnstaked * rsETHPrice < assetPrice`, a realistic condition under extreme price ratios.

During the upgrade path, `UnlockedWithdrawalsInitializer.processChunk()` (lines 97–103) iterates over all nonces up to `nextLockedNonce` and increments `added` only when `expectedAssetAmount > 0`. Zero-payout unlocked requests are silently skipped. The resulting seeded value passed to `initialize2` is therefore lower than the actual number of completable requests by the count of zero-payout requests.

In `_processWithdrawalCompletion` (line 717), `unlockedWithdrawalsCount[asset]--` is executed with no guard. After the seeded count of completions, the counter is 0. The next valid user's call reverts with an opaque arithmetic panic.

## Impact Explanation
Users who transferred rsETH to the contract at `initiateWithdrawal` (line 166) and whose requests were subsequently unlocked cannot call `completeWithdrawal` successfully once the counter underflows. Their rsETH remains locked in `LRTWithdrawalManager` with no user-accessible recovery path until an admin upgrade corrects the counter. This is **temporary freezing of funds** (Medium).

## Likelihood Explanation
The precondition requires the upgrade path (`initialize2` seeding) to have been used AND at least one unlocked request to have had `expectedAssetAmount == 0` at seeding time. The zero-payout condition arises from integer division truncation in `_calculatePayoutAmount` under extreme rsETH/asset price ratios — an edge case but not an impossible one for any deployment that went through the reinitializer upgrade. No privileged action by an attacker is needed; the underflow is triggered by ordinary users calling `completeWithdrawal` in sequence.

## Recommendation
Add an explicit guard before the decrement at line 717:

```solidity
if (unlockedWithdrawalsCount[asset] == 0) revert UnlockedWithdrawalsCountUnderflow();
unlockedWithdrawalsCount[asset]--;
```

Additionally, `_unlockWithdrawalRequests` should skip (or not increment the counter for) requests where `payoutAmount == 0`, and `UnlockedWithdrawalsInitializer.processChunk()` should use the same counting logic as `_unlockWithdrawalRequests` to ensure consistency.

## Proof of Concept

1. Before upgrade, operator calls `unlockWithdrawals` when `rsETHPrice` is extremely low relative to `assetPrice`, causing `_calculatePayoutAmount` to return 0 for request at nonce `k`. The request is stored with `expectedAssetAmount = 0`; `unlockedWithdrawalsCount[asset]` is incremented to 1 (via `_unlockWithdrawalRequests` line 809). Then N additional normal requests are unlocked, bringing the counter to N+1.
2. Upgrade is executed. `UnlockedWithdrawalsInitializer.processChunk()` iterates nonces 0..nextLockedNonce. Nonce `k` has `expectedAssetAmount == 0` → skipped. Only N requests are counted. `initialize2` seeds `unlockedWithdrawalsCount[asset] = N`.
3. N users call `completeWithdrawal`. Each call decrements the counter; after the Nth call, `unlockedWithdrawalsCount[asset] == 0`.
4. The user at nonce `k` (or any remaining valid user) calls `completeWithdrawal`. Execution reaches line 717: `unlockedWithdrawalsCount[asset]--` → arithmetic underflow panic (0x11). Transaction reverts with no meaningful message.
5. The user's rsETH (transferred at line 166) remains locked in `LRTWithdrawalManager` until an admin upgrade corrects the counter.