### Title
Disconnected Accounting Between `assetsCommitted` and `queuedWithdrawalsBuffer` Allows Instant Withdrawals to Drain Assets Reserved for Queued Withdrawals — (`contracts/LRTWithdrawalManager.sol` / `contracts/LRTUnstakingVault.sol`)

---

### Summary

The `LRTWithdrawalManager` tracks assets committed to queued withdrawals via `assetsCommitted[asset]`, but the `LRTUnstakingVault` protects vault assets from instant withdrawals via a separate, manually-set `queuedWithdrawalsBuffer[asset]`. These two accounting systems are never synchronized. Because `queuedWithdrawalsBuffer` defaults to zero and is only updated by an operator as a separate manual step, any user can call `instantWithdrawal` and drain vault assets that were already committed to pending queued withdrawals, leaving those queued withdrawal users unable to complete their withdrawals until the vault is replenished.

---

### Finding Description

**Root cause — two disconnected accounting systems for the same shared vault assets:**

When a user calls `initiateWithdrawal`, the contract records the committed amount:

```solidity
// LRTWithdrawalManager.sol
assetsCommitted[asset] += expectedAssetAmount;
``` [1](#0-0) 

The check that prevents over-commitment uses `getAvailableAssetAmount`, which subtracts `assetsCommitted` from the **total protocol assets** (including vault balance):

```solidity
function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
    uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
    availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
}
``` [2](#0-1) 

However, `instantWithdrawal` uses a completely separate check — `getAssetsAvailableForInstantWithdrawal` — which knows nothing about `assetsCommitted`:

```solidity
if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
    revert CantInstantWithdrawMoreThanAvailable();
}
unstakingVault.redeem(asset, assetAmountUnlocked);
``` [3](#0-2) 

Inside `LRTUnstakingVault`, the protection for queued withdrawals is a manually-set `queuedWithdrawalsBuffer`:

```solidity
function getAssetsAvailableForInstantWithdrawal(address asset) external view returns (uint256 availableAmount) {
    uint256 vaultBalance = balanceOf(asset);
    uint256 reservedBuffer = queuedWithdrawalsBuffer[asset];
    availableAmount = reservedBuffer >= vaultBalance ? 0 : vaultBalance - reservedBuffer;
}
``` [4](#0-3) 

This buffer is set by an operator as a separate, manual step:

```solidity
function setQueuedWithdrawalsBuffer(address asset, uint256 buffer) external onlyLRTOperator onlySupportedAsset(asset) {
    queuedWithdrawalsBuffer[asset] = buffer;
``` [5](#0-4) 

Because `queuedWithdrawalsBuffer` is a storage mapping, its **default value is zero**. Unless the operator explicitly sets it after every queued withdrawal is initiated, the vault offers no protection: `getAssetsAvailableForInstantWithdrawal` returns the full vault balance, regardless of how much has been committed via `assetsCommitted`.

Furthermore, `unlockQueue` — the function that actually services queued withdrawals — uses only the live vault balance as its available amount:

```solidity
totalAvailableAssets: unstakingVault.balanceOf(asset)
``` [6](#0-5) 

So if instant withdrawals drain the vault, `unlockQueue` cannot service the queued requests.

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

A user who has initiated a queued withdrawal (burning rsETH and locking in `assetsCommitted`) may find that their withdrawal cannot be unlocked because another user's instant withdrawal drained the vault assets that were supposed to back it. The queued withdrawal user's rsETH has already been transferred to the contract; they cannot cancel. They must wait until the operator moves additional assets from NodeDelegators or EigenLayer into the vault — a process that can take days due to EigenLayer's withdrawal delay. This constitutes a temporary but potentially prolonged freezing of user funds.

---

### Likelihood Explanation

**Medium.**

- `isInstantWithdrawalEnabled` must be set to `true` by the manager — a normal operational action, not a malicious one.
- `queuedWithdrawalsBuffer` defaults to zero and requires a separate, explicit operator call to set. There is no protocol-level enforcement that the buffer be updated whenever `assetsCommitted` changes.
- Once instant withdrawal is enabled with a zero buffer, any unprivileged user can call `instantWithdrawal` and drain vault assets committed to queued withdrawals.
- The two accounting systems (`assetsCommitted` in `LRTWithdrawalManager` and `queuedWithdrawalsBuffer` in `LRTUnstakingVault`) are structurally independent and will diverge in any realistic deployment where queued and instant withdrawals coexist.

---

### Recommendation

Replace the manually-maintained `queuedWithdrawalsBuffer` with a dynamic check against `assetsCommitted` from `LRTWithdrawalManager`. Specifically, `getAssetsAvailableForInstantWithdrawal` should query `ILRTWithdrawalManager(withdrawalManager).assetsCommitted(asset)` and subtract it from the vault balance, rather than relying on a static operator-set buffer. This ensures the two accounting systems are always synchronized without requiring manual operator intervention.

---

### Proof of Concept

1. Manager calls `setInstantWithdrawalEnabled(asset, true)`. `queuedWithdrawalsBuffer[asset]` remains `0` (default).
2. User A calls `initiateWithdrawal(asset, rsETHAmount, ...)`. The contract transfers `rsETHAmount` of rsETH from User A and records `assetsCommitted[asset] += X` where `X = getExpectedAssetAmount(asset, rsETHAmount)`. The vault holds at least `X` of `asset`.
3. User B calls `instantWithdrawal(asset, rsETHAmount2, ...)` where `rsETHAmount2` corresponds to `X` assets. `getAssetsAvailableForInstantWithdrawal(asset)` returns `vaultBalance - 0 = X`. The check passes. `unstakingVault.redeem(asset, X)` drains the vault.
4. Operator calls `unlockQueue(asset, ...)`. `_createUnlockParams` reads `unstakingVault.balanceOf(asset) = 0`. `_unlockWithdrawalRequests` exits immediately because `availableAssetAmount = 0 < payoutAmount`. User A's request is not unlocked.
5. User A cannot call `completeWithdrawal` because `usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]` — the request was never unlocked. User A's funds are frozen until the vault is replenished from EigenLayer (subject to EigenLayer's multi-day withdrawal delay).

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L173-173)
```text
        assetsCommitted[asset] += expectedAssetAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L231-235)
```text
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }

        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L599-603)
```text
    function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L847-851)
```text
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
    }
```

**File:** contracts/LRTUnstakingVault.sol (L199-208)
```text
    function setQueuedWithdrawalsBuffer(
        address asset,
        uint256 buffer
    )
        external
        onlyLRTOperator
        onlySupportedAsset(asset)
    {
        queuedWithdrawalsBuffer[asset] = buffer;
        emit QueuedWithdrawalsBufferUpdated(asset, buffer);
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
