### Title
Stale `assetsCommitted` in `LRTWithdrawalManager` Not Cleaned Up on `removeSupportedAsset` — (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary
`LRTConfig.removeSupportedAsset` does not clean up `assetsCommitted[asset]` in `LRTWithdrawalManager`. If the asset is later re-added, the stale committed amount causes `getAvailableAssetAmount` to underreport available assets, blocking all new withdrawal initiations for that asset.

---

### Finding Description

`LRTConfig.removeSupportedAsset` cleans up `isSupportedAsset[asset]`, `assetStrategy[asset]`, and `depositLimitByAsset[asset]`, but makes no call into `LRTWithdrawalManager` to clear `assetsCommitted[asset]`:

```solidity
delete isSupportedAsset[asset];
delete assetStrategy[asset];
depositLimitByAsset[asset] = 0;
``` [1](#0-0) 

The removal guard only checks `getTotalAssetDeposits`:

```solidity
if (ILRTDepositPool(depositPool).getTotalAssetDeposits(asset) > maxNegligibleAmount) {
    revert CannotRemoveAssetWithDeposits(asset);
}
``` [2](#0-1) 

`getTotalAssetDeposits` sums assets lying in the deposit pool, NDCs, staked in EigenLayer, and in the EigenLayer withdrawal queue (`getAssetUnstaking`). It does **not** count assets that have already been fully unstaked and moved into `LRTUnstakingVault` after `completeUnstaking` is called. Consequently, `getTotalAssetDeposits` can return zero (or negligible) while `assetsCommitted[asset]` is still non-zero — because users called `initiateWithdrawal` before `unlockQueue` was run.

`assetsCommitted[asset]` is increased in `initiateWithdrawal`:

```solidity
assetsCommitted[asset] += expectedAssetAmount;
``` [3](#0-2) 

and only reduced inside `_unlockWithdrawalRequests` (called by `unlockQueue`):

```solidity
assetsCommitted[asset] -= request.expectedAssetAmount;
``` [4](#0-3) 

If `removeSupportedAsset` is called before `unlockQueue` processes those locked requests, `assetsCommitted[asset]` remains non-zero. When the asset is re-added via `addNewSupportedAsset`, the stale value persists. `getAvailableAssetAmount` then computes:

```solidity
availableAssetAmount = totalAssets > assetsCommitted[asset]
    ? totalAssets - assetsCommitted[asset]
    : 0;
``` [5](#0-4) 

With stale `assetsCommitted[asset]` exceeding `totalAssets`, this returns `0`. Every subsequent `initiateWithdrawal` call reverts:

```solidity
if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();
``` [6](#0-5) 

---

### Impact Explanation
**Medium — Temporary freezing of funds.** After the asset is re-added, no new user can initiate a withdrawal for that asset. The freeze persists until `unlockQueue` is called to process the old locked requests, which reduces `assetsCommitted` back toward zero. During this window, withdrawers are blocked from accessing their funds.

---

### Likelihood Explanation
**Low.** The scenario requires the admin to (1) remove an asset while locked withdrawal requests exist and assets have been moved to `LRTUnstakingVault` (so `getTotalAssetDeposits` passes the negligible check), and (2) re-add the same asset. This is an unusual but plausible operational sequence — e.g., removing an asset to rotate its EigenLayer strategy and then re-listing it.

---

### Recommendation
In `LRTConfig.removeSupportedAsset`, also reset `assetsCommitted[asset]` in `LRTWithdrawalManager` to zero, or add a pre-condition check that `ILRTWithdrawalManager(withdrawalManager).assetsCommitted(asset) == 0` before allowing removal.

---

### Proof of Concept

1. User A calls `initiateWithdrawal(assetX, rsETHAmount)` → `assetsCommitted[assetX]` = 100e18.
2. Operator calls `NodeDelegator.completeUnstaking(...)` → assets move from EigenLayer withdrawal queue into `LRTUnstakingVault`; `getAssetUnstaking(assetX)` returns 0.
3. `getTotalAssetDeposits(assetX)` = 0 (assets are in `LRTUnstakingVault`, not counted by the function).
4. Admin calls `LRTConfig.removeSupportedAsset(assetX, index)` → the negligible-amount guard passes; `assetsCommitted[assetX]` = 100e18 is **not** cleared.
5. Admin calls `LRTConfig.addNewSupportedAsset(assetX, depositLimit)` → `assetsCommitted[assetX]` = 100e18 (stale).
6. User B calls `initiateWithdrawal(assetX, smallAmount)` → `getAvailableAssetAmount(assetX)` = 0 → reverts with `ExceedAmountToWithdraw`. All new withdrawals for `assetX` are frozen.

### Citations

**File:** contracts/LRTConfig.sol (L80-84)
```text
        address depositPool = getContract(LRTConstants.LRT_DEPOSIT_POOL);

        if (ILRTDepositPool(depositPool).getTotalAssetDeposits(asset) > maxNegligibleAmount) {
            revert CannotRemoveAssetWithDeposits(asset);
        }
```

**File:** contracts/LRTConfig.sol (L86-88)
```text
        delete isSupportedAsset[asset];
        delete assetStrategy[asset];
        depositLimitByAsset[asset] = 0;
```

**File:** contracts/LRTWithdrawalManager.sol (L170-170)
```text
        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();
```

**File:** contracts/LRTWithdrawalManager.sol (L173-173)
```text
        assetsCommitted[asset] += expectedAssetAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L599-602)
```text
    function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
```

**File:** contracts/LRTWithdrawalManager.sol (L802-802)
```text
            assetsCommitted[asset] -= request.expectedAssetAmount;
```
