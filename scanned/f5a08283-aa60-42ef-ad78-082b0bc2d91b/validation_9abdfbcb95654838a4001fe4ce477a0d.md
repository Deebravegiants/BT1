### Title
User Can DoS `unlockQueue()` by Draining `LRTUnstakingVault` via `instantWithdrawal()` — (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

When instant withdrawal is enabled for an asset and `queuedWithdrawalsBuffer` is zero (the default), any rsETH holder can drain the `LRTUnstakingVault` through `instantWithdrawal()`, causing the operator's subsequent `unlockQueue()` call to revert with `AmountMustBeGreaterThanZero`. This temporarily freezes the withdrawal queue, blocking queued users from receiving their assets.

---

### Finding Description

`unlockQueue()` is a privileged function (restricted to `onlyAssetTransferOrOperatorRole`) that processes the withdrawal queue. Its first substantive check reads the vault's current balance and reverts if it is zero:

```solidity
// LRTWithdrawalManager.sol
UnlockParams memory params = _createUnlockParams(lrtOracle, unstakingVault, asset);
...
if (params.totalAvailableAssets == 0) revert AmountMustBeGreaterThanZero();
``` [1](#0-0) 

`totalAvailableAssets` is sourced directly from the vault's live balance:

```solidity
return UnlockParams({
    ...
    totalAvailableAssets: unstakingVault.balanceOf(asset)
});
``` [2](#0-1) 

The `instantWithdrawal()` function, callable by any rsETH holder when enabled, pulls assets directly out of the vault:

```solidity
unstakingVault.redeem(asset, assetAmountUnlocked);
``` [3](#0-2) 

The amount a user may withdraw via `instantWithdrawal` is bounded only by `getAssetsAvailableForInstantWithdrawal`:

```solidity
uint256 vaultBalance = balanceOf(asset);
uint256 reservedBuffer = queuedWithdrawalsBuffer[asset];
availableAmount = reservedBuffer >= vaultBalance ? 0 : vaultBalance - reservedBuffer;
``` [4](#0-3) 

`queuedWithdrawalsBuffer` is a mapping whose default value is `0`: [5](#0-4) 

When the buffer is zero, `availableAmount == vaultBalance`, meaning a user can drain the **entire** vault in one or more `instantWithdrawal` calls. Once the vault is empty, any subsequent `unlockQueue()` call by the operator reverts unconditionally at the `AmountMustBeGreaterThanZero` guard, regardless of how many pending withdrawal requests exist.

The attacker does not need to frontrun any specific transaction. They can drain the vault at any time; the DoS persists until the vault is replenished by the protocol (e.g., via `completeUnstaking` → `NodeDelegator` → vault). During that window, all queued withdrawal requests are frozen.

---

### Impact Explanation

**Temporary freezing of funds.** Users who have already submitted withdrawal requests via `initiateWithdrawal()` (burning their rsETH and committing assets) cannot complete their withdrawals because `unlockQueue()` — the only mechanism to advance the queue — reverts. The attacker can repeat the drain each time the vault is refilled, extending the freeze. The protocol can mitigate by disabling instant withdrawal, but this requires a privileged action and leaves queued users in limbo in the interim.

---

### Likelihood Explanation

**Medium.** Two conditions must hold simultaneously:

1. `isInstantWithdrawalEnabled[asset] == true` — a deliberate manager action.
2. `queuedWithdrawalsBuffer[asset] == 0` — the **default** state; the operator must explicitly call `setQueuedWithdrawalsBuffer` to protect the vault.

The protocol provides the buffer mechanism precisely to prevent this, but it is opt-in and not enforced at the time instant withdrawal is enabled. Any rsETH holder with sufficient balance can execute the attack without any privileged access or frontrunning.

---

### Recommendation

1. **Enforce a non-zero buffer when enabling instant withdrawal.** In `setInstantWithdrawalEnabled`, require that `queuedWithdrawalsBuffer[asset] > 0` before allowing `enabled = true`.
2. **Alternatively**, make `unlockQueue()` degrade gracefully when `totalAvailableAssets == 0` (e.g., return `(0, 0)`) rather than reverting, so the operator's call does not fail outright.

---

### Proof of Concept

1. Manager calls `setInstantWithdrawalEnabled(ETH, true)`.
2. `queuedWithdrawalsBuffer[ETH]` remains `0` (default — operator never called `setQueuedWithdrawalsBuffer`).
3. Multiple users call `initiateWithdrawal(ETH, ...)`, locking their rsETH and committing expected ETH amounts.
4. Protocol refills the vault (e.g., via `completeUnstaking`).
5. Attacker calls `instantWithdrawal(ETH, largeAmount, ...)`, draining the vault to zero.
6. Operator calls `unlockQueue(ETH, firstExcludedIndex, ...)` → reverts with `AmountMustBeGreaterThanZero` at line 297.
7. Queued users cannot complete their withdrawals. Attacker repeats step 5 each time the vault is refilled.

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L235-235)
```text
        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L286-297)
```text
        UnlockParams memory params = _createUnlockParams(lrtOracle, unstakingVault, asset);

        _validatePrices(
            params.rsETHPrice,
            params.assetPrice,
            minimumRsEthPrice,
            maximumRsEthPrice,
            minimumAssetPrice,
            maximumAssetPrice
        );

        if (params.totalAvailableAssets == 0) revert AmountMustBeGreaterThanZero();
```

**File:** contracts/LRTWithdrawalManager.sol (L837-851)
```text
    function _createUnlockParams(
        ILRTOracle lrtOracle,
        ILRTUnstakingVault unstakingVault,
        address asset
    )
        internal
        view
        returns (UnlockParams memory)
    {
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
    }
```

**File:** contracts/LRTUnstakingVault.sol (L43-43)
```text
    mapping(address asset => uint256 buffer) public queuedWithdrawalsBuffer;
```

**File:** contracts/LRTUnstakingVault.sol (L235-237)
```text
        uint256 vaultBalance = balanceOf(asset);
        uint256 reservedBuffer = queuedWithdrawalsBuffer[asset];
        availableAmount = reservedBuffer >= vaultBalance ? 0 : vaultBalance - reservedBuffer;
```
