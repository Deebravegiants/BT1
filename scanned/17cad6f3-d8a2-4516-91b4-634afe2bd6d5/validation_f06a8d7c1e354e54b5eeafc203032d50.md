### Title
`instantWithdrawal` Missing `assetsCommitted` State Check Allows Draining of Assets Reserved for Queued Withdrawals - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

The `instantWithdrawal` function in `LRTWithdrawalManager` gates vault access using `queuedWithdrawalsBuffer` — a manually set operator value that defaults to zero — rather than `assetsCommitted`, the on-chain accounting variable that tracks assets already promised to queued withdrawal users. An unprivileged instant-withdrawal caller can drain the `LRTUnstakingVault` of assets that are committed to pending queued withdrawals, causing `unlockQueue` to revert and permanently blocking queued withdrawal users from completing their withdrawals while their rsETH remains locked in the contract with no recourse.

---

### Finding Description

When a user calls `initiateWithdrawal`, their rsETH is transferred to `LRTWithdrawalManager` and `assetsCommitted[asset]` is incremented by the expected asset amount. This committed amount is used in `getAvailableAssetAmount` to prevent over-commitment of new queued withdrawals. [1](#0-0) 

However, `instantWithdrawal` does not consult `assetsCommitted` at all. Instead, it checks `unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)`, which computes `vaultBalance - queuedWithdrawalsBuffer[asset]`. [2](#0-1) 

Since `queuedWithdrawalsBuffer` is a Solidity mapping that defaults to zero, the entire vault balance is available for instant withdrawal regardless of how much has been committed to queued withdrawals. [3](#0-2) 

When `unlockQueue` is subsequently called by an operator, it reads `unstakingVault.balanceOf(asset)` as `totalAvailableAssets` via `_createUnlockParams`. [4](#0-3) 

If the vault has been drained by instant withdrawals, this value is zero, causing `unlockQueue` to revert immediately: [5](#0-4) 

The queued withdrawal users' rsETH remains locked in `LRTWithdrawalManager` with no cancel mechanism available to them. The `_processWithdrawalCompletion` path also cannot help because it requires the request to have been unlocked first (`nextLockedNonce` check), which requires `unlockQueue` to succeed. [6](#0-5) 

---

### Impact Explanation

**Medium. Temporary freezing of funds.** Queued withdrawal users' rsETH is locked in `LRTWithdrawalManager` until the vault is replenished (e.g., via `completeUnstaking` from EigenLayer). There is no cancel mechanism for queued withdrawals, so users cannot recover their rsETH during the freeze period. The freeze persists for as long as the vault remains underfunded relative to committed queued withdrawals.

---

### Likelihood Explanation

`queuedWithdrawalsBuffer` is zero by default and requires explicit operator action to set. In the window between a user calling `initiateWithdrawal` and the operator setting the buffer — or if the operator fails to update the buffer when new queued withdrawals are initiated — any user holding rsETH can call `instantWithdrawal` to drain the vault. The `instantWithdrawal` path is permissionless and available to any rsETH holder, making this a realistic, low-barrier attack. The two accounting systems (`assetsCommitted` and `queuedWithdrawalsBuffer`) are never automatically synchronized, so the gap can persist indefinitely.

---

### Recommendation

The `instantWithdrawal` function should enforce that the vault retains enough assets to cover committed queued withdrawals. Concretely, `getAssetsAvailableForInstantWithdrawal` in `LRTUnstakingVault

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L166-173)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L228-235)
```text
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }

        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L297-297)
```text
        if (params.totalAvailableAssets == 0) revert AmountMustBeGreaterThanZero();
```

**File:** contracts/LRTWithdrawalManager.sol (L705-707)
```text
        uint256 usersFirstWithdrawalRequestNonce = userAssociatedNonces[asset][user].popFront();
        // Ensure the request is already unlocked.
        if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();
```

**File:** contracts/LRTWithdrawalManager.sol (L846-850)
```text
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
```

**File:** contracts/LRTUnstakingVault.sol (L229-238)
```text
    function getAssetsAvailableForInstantWithdrawal(address asset)
        external
        view
        onlySupportedAsset(asset)
        returns (uint256 availableAmount)
    {
        uint256 vaultBalance = balanceOf(asset);
        uint256 reservedBuffer = queuedWithdrawalsBuffer[asset];
        availableAmount = reservedBuffer >= vaultBalance ? 0 : vaultBalance - reservedBuffer;
    }
```
