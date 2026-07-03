### Title
`whenNotPaused` on `completeWithdrawal` Freezes Already-Unlocked User Funds During Auto-Pause - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`LRTWithdrawalManager.completeWithdrawal()` carries a `whenNotPaused` guard. After `unlockQueue()` has already burned the user's rsETH and pulled the corresponding assets from the vault into the manager contract, a subsequent pause (which can be triggered automatically by `LRTOracle` on a price drop) makes those assets permanently inaccessible to users until an admin manually unpauses.

---

### Finding Description

The withdrawal lifecycle in `LRTWithdrawalManager` has three distinct phases:

1. **`initiateWithdrawal()`** — user's rsETH is transferred into the contract and a request is queued.
2. **`unlockQueue()`** — an operator call that (a) burns the queued rsETH from the contract and (b) redeems the corresponding asset amount from `LRTUnstakingVault` into `LRTWithdrawalManager`. After this step the user's rsETH is gone and the owed assets sit inside the manager.
3. **`completeWithdrawal()`** — user calls this to receive the assets already sitting in the contract.

`completeWithdrawal` is guarded by `whenNotPaused`:

```solidity
// LRTWithdrawalManager.sol:183
function completeWithdrawal(address asset, string calldata referralId)
    external nonReentrant whenNotPaused { ... }
```

`LRTOracle._updateRsETHPrice()` contains an automatic downside-protection mechanism that pauses `LRTWithdrawalManager` without any admin action whenever the rsETH price drops beyond `pricePercentageLimit`:

```solidity
// LRTOracle.sol:277-281
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
```

If this auto-pause fires after `unlockQueue()` has already settled a batch of requests (rsETH burned, assets in the manager), every affected user's `completeWithdrawal()` call reverts. The assets are stranded in the contract: the rsETH that represented them has been destroyed and cannot be recovered, yet the assets cannot be transferred out.

`completeWithdrawalForUser` (the operator-assisted path) carries the same `whenNotPaused` guard and is equally blocked:

```solidity
// LRTWithdrawalManager.sol:197-200
external nonReentrant whenNotPaused onlyLRTOperator { ... }
```

---

### Impact Explanation

**Medium — Temporary (potentially indefinite) freezing of funds.**

After `unlockQueue()` executes, the user's rsETH is irreversibly burned and the owed assets are held inside `LRTWithdrawalManager`. While the contract is paused, `completeWithdrawal` reverts unconditionally, so those assets cannot reach their owners. The freeze lasts until an admin with `DEFAULT_ADMIN_ROLE` calls `unpause()`. If the pause is triggered by a severe slashing or depeg event, the admin may delay unpausing indefinitely, extending the freeze. Users have no self-service escape path.

---

### Likelihood Explanation

**Medium.**

Two realistic conditions must coincide:
- One or more withdrawal requests have been processed through `unlockQueue()` (assets in manager, rsETH burned) but not yet claimed via `completeWithdrawal()`.
- `LRTOracle.updateRSETHPrice()` is called (routine oracle update) while the rsETH price has dropped beyond `pricePercentageLimit` relative to `highestRsethPrice`.

The oracle update is a normal operational call. A significant EigenLayer slashing event or LST depeg is a realistic trigger for the price-drop condition. Both conditions can occur simultaneously without any attacker involvement.

---

### Recommendation

Remove `whenNotPaused` from `completeWithdrawal` (and `completeWithdrawalForUser`). By the time these functions are called, the user's rsETH has already been burned and the assets are already inside the manager — there is no economic reason to block the final transfer. Alternatively, introduce a separate `claimPaused` flag that blocks only new `initiateWithdrawal` requests while still allowing already-unlocked claims to proceed, mirroring the fix recommended in the reference report.

---

### Proof of Concept

**Step-by-step:**

1. Alice calls `initiateWithdrawal(ETH, 1e18 rsETH, "")`. Her rsETH is transferred to `LRTWithdrawalManager`.
2. An operator calls `unlockQueue(ETH, ...)`. Inside `unlockQueue`:
   - Line 305: `IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned)` — Alice's rsETH is burned.
   - Line 307: `unstakingVault.redeem(asset, assetAmountUnlocked)` — ETH is pulled from `LRTUnstakingVault` into `LRTWithdrawalManager`. Alice's request is now marked unlocked.
3. A routine oracle update calls `LRTOracle.updateRSETHPrice()`. The new rsETH price is below `highestRsethPrice` by more than `pricePercentageLimit`. Line 279 executes: `withdrawalManager.pause()`.
4. Alice calls `completeWithdrawal(ETH, "")`. The `whenNotPaused` modifier at line 183 reverts the call.
5. Alice's ETH sits in `LRTWithdrawalManager`. Her rsETH is gone. She has no recourse until an admin calls `unpause()`.

**Relevant code references:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L183-185)
```text
    function completeWithdrawal(address asset, string calldata referralId) external nonReentrant whenNotPaused {
        _processWithdrawalCompletion(asset, msg.sender, referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L197-203)
```text
        external
        nonReentrant
        whenNotPaused
        onlyLRTOperator
    {
        _processWithdrawalCompletion(asset, user, referralId);
        emit AssetWithdrawalCompletedBy(msg.sender);
```

**File:** contracts/LRTWithdrawalManager.sol (L305-307)
```text
        if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
        //Take the amount to distribute from vault
        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTOracle.sol (L277-281)
```text
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
```
