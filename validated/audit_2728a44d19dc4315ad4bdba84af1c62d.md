Audit Report

## Title
Withdrawal Queue Liveness Failure: `getAvailableAssetAmount` Counts Illiquid EigenLayer Assets, Causing Temporary Fund Freeze and Stale-Price Execution - (File: `contracts/LRTWithdrawalManager.sol`)

## Summary

`initiateWithdrawal` gates new requests against `getAvailableAssetAmount`, which counts EigenLayer-locked assets as available. However, `unlockQueue` can only draw from the liquid `LRTUnstakingVault` balance. When the vault is empty, the queue cannot be unlocked regardless of total protocol TVL, leaving the user's rsETH frozen in the contract with no cancellation path. Additionally, `_calculatePayoutAmount` applies a `min(originalQuote, currentReturn)` formula, so a price decline during the mandatory EigenLayer unwind period causes the user to receive less than the amount quoted at request time.

## Finding Description

**Root cause — mismatched liquidity accounting between admission and execution.**

`getAvailableAssetAmount` (L599–603) calls `lrtDepositPool.getTotalAssetDeposits(asset)` (L385–397 of `LRTDepositPool.sol`), which sums every location including `assetStakedInEigenLayer` and `assetUnstakingFromEigenLayer` — assets subject to a ≥7-day EigenLayer withdrawal delay. The admission check at L170 of `LRTWithdrawalManager.sol` passes as long as `expectedAssetAmount ≤ totalAssets − assetsCommitted`, even when the vault is empty.

`_createUnlockParams` (L837–851) sets `totalAvailableAssets` to `unstakingVault.balanceOf(asset)` — only the liquid vault balance. `unlockQueue` (L297) immediately reverts with `AmountMustBeGreaterThanZero` if that balance is zero. The loop at L800 also breaks early if `availableAssetAmount < payoutAmount`.

There is no `cancelWithdrawal` function anywhere in the contract (confirmed by search). Once `initiateWithdrawal` transfers the user's rsETH to the contract (L166), the user has no recourse until an operator completes the full EigenLayer unwind cycle: queue withdrawal → wait ≥7 days → `completeUnstaking` → route funds to vault → call `unlockQueue`.

**Stale-price execution:** `_calculatePayoutAmount` (L833–834) returns `min(expectedAssetAmount, currentReturn)`. If the rsETH/asset rate declines during the unwind period, `currentReturn < expectedAssetAmount` and the user receives less than the amount they were quoted at request time, with no slippage protection or cancellation right.

## Impact Explanation

**Medium — Temporary freezing of funds:** A user who calls `initiateWithdrawal` when the vault is empty but EigenLayer TVL is large will have their rsETH locked in `LRTWithdrawalManager` for the full EigenLayer unwind period (≥7 days on top of `withdrawalDelayBlocks`), with no ability to cancel. This is a concrete, user-triggered, time-bounded freeze caused by a code-level accounting mismatch, not a generic liquidity issue.

**Low — Contract fails to deliver promised returns:** The `expectedAssetAmount` stored at request time is the amount the user was quoted. The `min()` formula in `_calculatePayoutAmount` means adverse price movement during the extended wait reduces the payout below the quoted figure, with no recourse.

## Likelihood Explanation

This is a normal operating condition. The protocol actively moves assets from `LRTDepositPool` into EigenLayer strategies, making the `LRTUnstakingVault` balance routinely near zero between unwind cycles. Any user who calls `initiateWithdrawal` during such a period — which is the typical state — will experience the freeze. No attacker capability is required; the victim is any ordinary withdrawer. The EigenLayer delay is a protocol-level constant, making the price-movement window substantial and repeatable.

## Recommendation

1. **Fix the availability check:** `getAvailableAssetAmount` should count only liquid assets (vault balance + deposit pool balance), not EigenLayer-locked assets, so users cannot queue withdrawals that cannot be serviced without an EigenLayer unwind.
2. **Add a cancellation path:** Allow users to cancel a pending (not yet unlocked) withdrawal request and reclaim their rsETH.
3. **Positive-slippage protection:** In `_calculatePayoutAmount`, if `currentReturn > expectedAssetAmount`, pay `currentReturn` rather than capping at the original quote.

## Proof of Concept

**Setup:** Protocol has 1000 stETH: 990 stETH in EigenLayer, 10 stETH in `LRTUnstakingVault`, `assetsCommitted[stETH] = 0`.

1. User calls `initiateWithdrawal(stETH, rsETHAmount)` where `expectedAssetAmount = 40 stETH`.
2. `getAvailableAssetAmount` returns `1000 − 0 = 1000 stETH` → check at L170 passes. rsETH transferred to contract. `assetsCommitted[stETH] = 40`.
3. Operator calls `unlockQueue(stETH, ...)`. `unstakingVault.balanceOf(stETH) = 10`. `_createUnlockParams` sets `totalAvailableAssets = 10`. Loop at L800: `10 < 40` → breaks immediately. `rsETHBurned = 0`, `assetAmountUnlocked = 0`. Nothing is unlocked.
4. Operator must queue EigenLayer withdrawal → wait ≥7 days → `completeUnstaking` → route to vault → call `unlockQueue` again.
5. User cannot cancel (no `cancelWithdrawal` exists). rsETH is frozen for the entire duration.
6. During the 7-day wait, stETH/ETH rate drops 2%. At unlock time, `currentReturn = 39.2 stETH < 40 stETH = expectedAssetAmount`. User receives 39.2 stETH instead of the quoted 40 stETH, with no recourse.

**Foundry test plan:** Deploy `LRTWithdrawalManager`, `LRTDepositPool`, and a mock `LRTUnstakingVault` with `balanceOf` returning 10e18. Stake 990e18 in a mock EigenLayer strategy so `getTotalAssetDeposits` returns 1000e18. Call `initiateWithdrawal` for 40e18 expected — assert it succeeds. Call `unlockQueue` — assert it reverts or returns `(0, 0)`. Assert user cannot recover rsETH. Advance block time by 7 days, drop mock oracle price by 2%, complete the unwind, call `unlockQueue` again, assert payout is 39.2e18 not 40e18.