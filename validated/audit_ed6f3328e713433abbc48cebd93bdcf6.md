### Title
`getAvailableAssetAmount` Includes Non-Withdrawable Assets, Enabling Withdrawal Queue Desync and Temporary Fund Freeze - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`LRTWithdrawalManager.getAvailableAssetAmount` uses `LRTDepositPool.getTotalAssetDeposits`, which aggregates assets across all protocol locations (deposit pool, NDCs, EigenLayer, unstaking vault). However, actual withdrawal fulfillment at `unlockQueue` time only draws from `LRTUnstakingVault.balanceOf`. This mismatch allows users to queue withdrawals far exceeding what the unstaking vault holds, locking their rsETH in the withdrawal manager until operators complete the full EigenLayer unstaking pipeline.

---

### Finding Description

In `initiateWithdrawal`, the guard against over-commitment is:

```solidity
if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();
assetsCommitted[asset] += expectedAssetAmount;
```

`getAvailableAssetAmount` is defined as:

```solidity
function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
    ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
    uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
    availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
}
``` [1](#0-0) 

`getTotalAssetDeposits` sums assets from every location:

```solidity
return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
        + assetLyingUnstakingVault);
``` [2](#0-1) 

However, when `unlockQueue` is called by an operator, the available assets are sourced exclusively from the unstaking vault:

```solidity
totalAvailableAssets: unstakingVault.balanceOf(asset)
``` [3](#0-2) 

And `_unlockWithdrawalRequests` only unlocks requests up to `availableAssetAmount` (the vault balance):

```solidity
if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request
``` [4](#0-3) 

Assets sitting in the deposit pool or NDCs cannot be directly redeemed to fulfill withdrawal requests — they must first be staked into EigenLayer and then unstaked through the EigenLayer withdrawal queue (subject to EigenLayer's withdrawal delay) before landing in the `LRTUnstakingVault`.

**Concrete scenario:**

1. Protocol holds 800 stETH in the deposit pool and 200 stETH in the unstaking vault. `assetsCommitted = 0`.
2. `getAvailableAssetAmount` returns 1000.
3. User A calls `initiateWithdrawal` for 900 stETH worth of rsETH — passes the check. rsETH is transferred to the withdrawal manager. `assetsCommitted = 900`.
4. User B calls `initiateWithdrawal` for 100 stETH worth of rsETH — passes. `assetsCommitted = 1000`.
5. Operator calls `unlockQueue`: `unstakingVault.balanceOf(stETH) = 200`. Only 200 stETH worth of requests can be unlocked. User A's 900 stETH request cannot be unlocked.
6. User A's rsETH remains locked in the withdrawal manager until operators complete the full EigenLayer unstaking cycle for the remaining 700 stETH.

---

### Impact Explanation

User rsETH is transferred into `LRTWithdrawalManager` at `initiateWithdrawal` time and cannot be recovered until the withdrawal is unlocked via `unlockQueue`. If the unstaking vault lacks sufficient assets (because `getAvailableAssetAmount` counted deposit pool / NDC assets that are not yet in the vault), the withdrawal request remains permanently locked in the queue until operators manually route assets through EigenLayer's withdrawal pipeline. This constitutes **temporary freezing of user funds** (rsETH locked in the withdrawal manager with no self-service exit path). [5](#0-4) 

---

### Likelihood Explanation

This condition is routine. The deposit pool and NDCs routinely hold assets that have not yet been staked into EigenLayer or unstaked to the vault. Any user who calls `initiateWithdrawal` when the deposit pool holds a significant balance relative to the unstaking vault will trigger this desync. No special permissions or adversarial setup are required — any rsETH holder can call `initiateWithdrawal`.

---

### Recommendation

`getAvailableAssetAmount` should only count assets that are actually reachable for withdrawal fulfillment. The simplest fix is to base the available amount on `LRTUnstakingVault.balanceOf(asset)` (minus already-committed amounts) rather than `getTotalAssetDeposits`. Alternatively, track a separate "withdrawable reserve" that is updated only when assets arrive in the unstaking vault.

---

### Proof of Concept

1. Assume stETH: 1000 stETH total — 900 in deposit pool, 100 in unstaking vault. `assetsCommitted[stETH] = 0`.
2. Call `getAvailableAssetAmount(stETH)` → returns 1000 (deposit pool 900 + unstaking vault 100).
3. User calls `initiateWithdrawal(stETH, rsETHFor900stETH, "")`:
   - `expectedAssetAmount = 900`
   - `900 <= 1000` → passes
   - rsETH transferred to withdrawal manager
   - `assetsCommitted[stETH] = 900`
4. Operator calls `unlockQueue(stETH, ...)`:
   - `params.totalAvailableAssets = unstakingVault.balanceOf(stETH) = 100`
   - Loop: first request needs 900, `100 < 900` → `break`
   - No requests unlocked. `rsETHBurned = 0`, `assetAmountUnlocked = 0`.
5. User calls `completeWithdrawal(stETH, "")`:
   - `usersFirstWithdrawalRequestNonce >= nextLockedNonce[stETH]` → `revert WithdrawalLocked()`
6. User's rsETH is frozen in the withdrawal manager. Recovery requires operators to unstake 800 stETH from EigenLayer (subject to EigenLayer's withdrawal delay), move them to the unstaking vault, then call `unlockQueue` again. [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L166-175)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L599-603)
```text
    function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L700-707)
```text
        if (userAssociatedNonces[asset][user].empty()) {
            revert NoWithdrawalRequests(user, asset);
        }

        // Retrieve and remove the oldest withdrawal request for the user.
        uint256 usersFirstWithdrawalRequestNonce = userAssociatedNonces[asset][user].popFront();
        // Ensure the request is already unlocked.
        if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();
```

**File:** contracts/LRTWithdrawalManager.sol (L800-800)
```text
            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request
```

**File:** contracts/LRTWithdrawalManager.sol (L846-850)
```text
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
```

**File:** contracts/LRTDepositPool.sol (L385-397)
```text
    function getTotalAssetDeposits(address asset) public view override returns (uint256 totalAssetDeposit) {
        (
            uint256 assetLyingInDepositPool,
            uint256 assetLyingInNDCs,
            uint256 assetStakedInEigenLayer,
            uint256 assetUnstakingFromEigenLayer,
            uint256 assetLyingInConverter,
            uint256 assetLyingUnstakingVault
        ) = getAssetDistributionData(asset);
        uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
        return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
                + assetLyingUnstakingVault);
    }
```
