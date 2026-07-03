### Title
Instant Withdrawal Drains Assets Committed to Queued Withdrawal Users Due to Unsynchronized Accounting - (File: `contracts/LRTWithdrawalManager.sol`)

### Summary
`LRTWithdrawalManager` maintains two independent accounting systems for queued and instant withdrawals: `assetsCommitted` (tracks assets promised to queued users) and `queuedWithdrawalsBuffer` (a static operator-set value meant to protect those assets from instant withdrawals). Because these systems are never automatically synchronized, an unprivileged user calling `instantWithdrawal` can drain vault assets that were already committed to queued withdrawal users, temporarily freezing their funds.

### Finding Description

`initiateWithdrawal` reserves assets for a user by incrementing `assetsCommitted[asset]`:

```solidity
assetsCommitted[asset] += expectedAssetAmount;
``` [1](#0-0) 

`instantWithdrawal` does not consult `assetsCommitted` at all. Instead it checks `getAssetsAvailableForInstantWithdrawal`, which is computed solely from the static `queuedWithdrawalsBuffer`:

```solidity
if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
    revert CantInstantWithdrawMoreThanAvailable();
}
unstakingVault.redeem(asset, assetAmountUnlocked);
``` [2](#0-1) 

Inside `LRTUnstakingVault`, `getAssetsAvailableForInstantWithdrawal` computes:

```solidity
availableAmount = reservedBuffer >= vaultBalance ? 0 : vaultBalance - reservedBuffer;
``` [3](#0-2) 

`queuedWithdrawalsBuffer` defaults to `0` and is a static value set by an operator:

```solidity
function setQueuedWithdrawalsBuffer(address asset, uint256 buffer) external onlyLRTOperator onlySupportedAsset(asset) {
    queuedWithdrawalsBuffer[asset] = buffer;
``` [4](#0-3) 

Because `queuedWithdrawalsBuffer` is never automatically updated when `assetsCommitted` grows (as more users call `initiateWithdrawal`), the buffer can be zero or stale. When instant withdrawals are enabled, any unprivileged user can call `instantWithdrawal` and drain the entire vault balance — including assets already committed to queued users.

When `unlockQueue` is subsequently called, it reads the vault balance as `totalAvailableAssets`:

```solidity
totalAvailableAssets: unstakingVault.balanceOf(asset)
``` [5](#0-4) 

With the vault empty, `_unlockWithdrawalRequests` exits immediately:

```solidity
if (availableAssetAmount < payoutAmount) break;
``` [6](#0-5) 

Queued withdrawal users cannot complete their withdrawals until the operator manually replenishes the vault from EigenLayer.

This is the direct analog of M-29: two operations (`initiateWithdrawal` / `instantWithdrawal`) share the same underlying vault balance but use separate, unsynchronized accounting systems — exactly as `withdrawReserves()` and `getLoan()` shared the same `withdrawApproval` mapping in the original report.

### Impact Explanation

Queued withdrawal users who have already burned rsETH (via `initiateWithdrawal`) and had their assets committed via `assetsCommitted` cannot complete their withdrawals. Their funds are temporarily frozen in the protocol until an operator replenishes the vault. This matches the **Medium — Temporary freezing of funds** impact category.

### Likelihood Explanation

- `isInstantWithdrawalEnabled[asset]` must be `true` — a deliberate operator action, not an edge case.
- `queuedWithdrawalsBuffer[asset]` defaults to `0`, which is the unsafe state. The operator must proactively set and continuously update it as `assetsCommitted` grows; there is no on-chain enforcement.
- Any unprivileged rsETH holder can call `instantWithdrawal` once enabled.
- The window of vulnerability exists continuously between any `initiateWithdrawal` call and the operator's next buffer update.

Likelihood is **Medium**.

### Recommendation

Replace the static `queuedWithdrawalsBuffer` with a dynamic check against `assetsCommitted` inside `LRTUnstakingVault.getAssetsAvailableForInstantWithdrawal`. The vault should query the withdrawal manager's `assetsCommitted[asset]` and subtract it from the vault balance to compute the truly available amount for instant withdrawals:

```solidity
function getAssetsAvailableForInstantWithdrawal(address asset) external view returns (uint256 availableAmount) {
    uint256 vaultBalance = balanceOf(asset);
    uint256 committed = ILRTWithdrawalManager(withdrawalManager).assetsCommitted(asset);
    availableAmount = committed >= vaultBalance ? 0 : vaultBalance - committed;
}
```

This eliminates the need for a manually maintained buffer and ensures instant withdrawals can never consume assets already committed to queued users.

### Proof of Concept

1. Operator calls `setInstantWithdrawalEnabled(ETH, true)`. `queuedWithdrawalsBuffer[ETH]` remains `0` (default).
2. User A calls `initiateWithdrawal(ETH, 100e18)`. `assetsCommitted[ETH] += X ETH`. The vault holds `X ETH`.
3. User B (unprivileged) calls `instantWithdrawal(ETH, 100e18)`. `getAssetsAvailableForInstantWithdrawal(ETH)` returns `vaultBalance - 0 = X ETH`. The check passes. `unstakingVault.redeem(ETH, X)` drains the vault to zero.
4. Operator calls `unlockQueue(ETH, ...)`. `totalAvailableAssets = unstakingVault.balanceOf(ETH) = 0`. `_unlockWithdrawalRequests` breaks immediately — no requests are unlocked.
5. User A's withdrawal is frozen. Their rsETH was already transferred to the contract in step 2 and cannot be recovered until the operator manually replenishes the vault.

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L170-173)
```text
        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L231-235)
```text
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }

        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L800-800)
```text
            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request
```

**File:** contracts/LRTWithdrawalManager.sol (L847-850)
```text
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
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

**File:** contracts/LRTUnstakingVault.sol (L235-238)
```text
        uint256 vaultBalance = balanceOf(asset);
        uint256 reservedBuffer = queuedWithdrawalsBuffer[asset];
        availableAmount = reservedBuffer >= vaultBalance ? 0 : vaultBalance - reservedBuffer;
    }
```
