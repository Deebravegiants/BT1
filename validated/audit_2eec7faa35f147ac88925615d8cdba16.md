### Title
Unlocked Withdrawals Can Be Abandoned After rsETH Is Burned, Temporarily Freezing Assets and Forcing Operator to Bear Unrecoverable Gas Costs — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

After `unlockQueue()` irrevocably burns rsETH and pulls assets from `LRTUnstakingVault` into `LRTWithdrawalManager`, users face no obligation to call `completeWithdrawal()`. If the underlying asset value crashes below the gas cost of claiming, users may rationally abandon their unlocked withdrawals. This leaves assets frozen in `LRTWithdrawalManager`, blocks `sweepRemainingAssets()`, and forces the operator to pay gas for `completeWithdrawalForUser()` calls — costs the operator cannot recoup — directly mirroring the external report's post-execution commitment / bad-debt pattern.

---

### Finding Description

The withdrawal lifecycle in `LRTWithdrawalManager` has three distinct phases:

1. **`initiateWithdrawal()`** — user's rsETH is transferred *to* the withdrawal manager (held, not yet burned).
2. **`unlockQueue()`** — operator burns the held rsETH from the contract and pulls the underlying asset from `LRTUnstakingVault` into `LRTWithdrawalManager`.
3. **`completeWithdrawal()`** — user claims their asset. [1](#0-0) 

After step 2, the rsETH is permanently burned and the underlying asset sits in `LRTWithdrawalManager`: [2](#0-1) 

The user has no obligation to call `completeWithdrawal()`. If the underlying asset (e.g., stETH) depegs or crashes, the gas cost of claiming may exceed the asset value, making abandonment economically rational — identical to the external report's LUNA-crash scenario.

When users abandon their unlocked withdrawals:

- Assets remain frozen in `LRTWithdrawalManager` with `unlockedWithdrawalsCount[asset] > 0`.
- `sweepRemainingAssets()` is permanently blocked: [3](#0-2) 

- The only recovery path is the operator calling `completeWithdrawalForUser()`, paying gas to push worthless assets to users: [4](#0-3) 

There is no mechanism to cancel an unlocked withdrawal, redirect assets back to the vault, or reset `unlockedWithdrawalsCount`. The operator cannot recoup the gas spent on `unlockQueue()` or `completeWithdrawalForUser()`.

The `_processWithdrawalCompletion()` path that decrements `unlockedWithdrawalsCount` is the *only* way to unblock the queue: [5](#0-4) 

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

Assets pulled from `LRTUnstakingVault` into `LRTWithdrawalManager` via `unlockQueue()` are frozen there until the operator force-completes each abandoned withdrawal via `completeWithdrawalForUser()`. During this period:

- The assets are not in the vault, not in EigenLayer, and not earning yield.
- `sweepRemainingAssets()` is blocked for the affected asset.
- The operator bears unrecoverable gas costs for force-completions.
- In the worst case (user address is a contract that rejects ETH), `completeWithdrawalForUser()` itself reverts, making the freeze permanent for ETH withdrawals. [6](#0-5) 

---

### Likelihood Explanation

**Low-Medium.** Requires the underlying LST to depeg or crash such that the gas cost of calling `completeWithdrawal()` exceeds the asset value. This is a realistic scenario during market stress events (LST depegs, slashing cascades). Users with small withdrawal amounts are most susceptible. The rsETH being burned at `unlockQueue()` time gives users *some* incentive to claim, but not if the asset value is near zero.

---

### Recommendation

1. Implement a **cancellation window**: allow users to cancel an unlocked withdrawal within a grace period, returning assets to `LRTUnstakingVault` and re-minting rsETH.
2. Alternatively, implement a **timeout mechanism**: after a configurable period, allow the operator to redirect unclaimed assets back to the vault and re-mint rsETH, restoring protocol solvency.
3. Consider collecting a small upfront fee at `initiateWithdrawal()` time to cover operator gas costs, refunded upon `completeWithdrawal()`.

---

### Proof of Concept

1. User calls `initiateWithdrawal(stETH, 1e18, "")` — 1 rsETH transferred to `LRTWithdrawalManager`.
2. Operator calls `unlockQueue(stETH, ...)` — rsETH burned from contract, stETH pulled from `LRTUnstakingVault` into `LRTWithdrawalManager`; `unlockedWithdrawalsCount[stETH]++`. [2](#0-1) 

3. stETH price crashes to near zero (e.g., depeg event).
4. User does not call `completeWithdrawal()` — gas cost exceeds stETH value.
5. stETH is frozen in `LRTWithdrawalManager`; `unlockedWithdrawalsCount[stETH] == 1`.
6. Manager calls `sweepRemainingAssets(stETH)` → reverts with `PendingWithdrawalsExist`. [3](#0-2) 

7. Operator must call `completeWithdrawalForUser(stETH, user, "")`, paying gas to push near-worthless stETH to the user — gas costs the operator cannot recoup. [4](#0-3)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L192-203)
```text
    function completeWithdrawalForUser(
        address asset,
        address user,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlyLRTOperator
    {
        _processWithdrawalCompletion(asset, user, referralId);
        emit AssetWithdrawalCompletedBy(msg.sender);
```

**File:** contracts/LRTWithdrawalManager.sol (L301-307)
```text
        (rsETHBurned, assetAmountUnlocked) = _unlockWithdrawalRequests(
            asset, params.totalAvailableAssets, params.rsETHPrice, params.assetPrice, firstExcludedIndex
        );

        if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
        //Take the amount to distribute from vault
        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L402-403)
```text
        // Check that all withdrawals are completed
        if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist();
```

**File:** contracts/LRTWithdrawalManager.sol (L717-717)
```text
        unlockedWithdrawalsCount[asset]--;
```

**File:** contracts/LRTWithdrawalManager.sol (L877-880)
```text
        if (asset == LRTConstants.ETH_TOKEN) {
            (bool sent,) = payable(to).call{ value: amount }("");
            if (!sent) revert EthTransferFailed();
        } else {
```
