### Title
`instantWithdrawal()` Liquidity Check Does Not Account for Queued Withdrawal Commitments, Enabling Vault Drain That Freezes Queued Withdrawals - (File: contracts/LRTWithdrawalManager.sol)

### Summary

`LRTWithdrawalManager.instantWithdrawal()` checks vault availability using a static, operator-set `queuedWithdrawalsBuffer` rather than the dynamically tracked `assetsCommitted` mapping. This allows any user to drain the `LRTUnstakingVault` of funds that are already committed to pending queued withdrawals, causing `unlockQueue()` to be unable to service those requests and temporarily freezing queued withdrawal users' rsETH.

### Finding Description

The protocol has two withdrawal paths that both draw from `LRTUnstakingVault`:

**Path 1 – Queued withdrawal** (`initiateWithdrawal` → `unlockQueue`):
- `initiateWithdrawal` checks `getAvailableAssetAmount`, which computes `totalAssets - assetsCommitted[asset]` and increments `assetsCommitted[asset]` by the committed amount.
- `unlockQueue` later calls `_createUnlockParams`, which sets `totalAvailableAssets = unstakingVault.balanceOf(asset)` — the raw vault balance — and then calls `unstakingVault.redeem()` to pull funds from the vault.

**Path 2 – Instant withdrawal** (`instantWithdrawal`):
- Checks `unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)`, which computes `vaultBalance - queuedWithdrawalsBuffer[asset]`.
- `queuedWithdrawalsBuffer` is a **static value** set manually by an operator via `setQueuedWithdrawalsBuffer`. It is never automatically updated when `assetsCommitted` grows.

The mismatch: `assetsCommitted` grows every time a user calls `initiateWithdrawal`, but `queuedWithdrawalsBuffer` stays fixed. If `queuedWithdrawalsBuffer` is zero (the default) or stale, `getAssetsAvailableForInstantWithdrawal` returns the full vault balance, allowing instant withdrawals to drain funds that are already committed to queued withdrawal users.

**Concrete scenario:**
1. Vault holds 100 ETH; `queuedWithdrawalsBuffer[ETH]` = 0 (default).
2. Users call `initiateWithdrawal` for a total of 100 ETH → `assetsCommitted[ETH]` = 100 ETH; their rsETH is locked in `LRTWithdrawalManager`.
3. An attacker (or any user) calls `instantWithdrawal` for 100 ETH. The check passes: `getAssetsAvailableForInstantWithdrawal` = 100 − 0 = 100 ETH. The vault is drained to 0.
4. Operator calls `unlockQueue`. `_createUnlockParams` reads `unstakingVault.balanceOf(asset)` = 0, so `totalAvailableAssets` = 0. `_unlockWithdrawalRequests` immediately breaks at `if (availableAssetAmount < payoutAmount)`. No queued withdrawal can be unlocked.
5. Queued withdrawal users' rsETH remains locked in `LRTWithdrawalManager` with no path to completion until the vault is manually refilled by operators.

### Impact Explanation

**Medium – Temporary freezing of funds.**

Queued withdrawal users have already transferred their rsETH into `LRTWithdrawalManager` (line 166) and cannot retrieve it until `unlockQueue` succeeds. With the vault drained, `unlockQueue` cannot unlock any requests. Funds are not permanently lost (the protocol still holds equivalent assets in EigenLayer/NDCs), but users are frozen until operators manually move assets back into the vault. This constitutes a temporary freeze of user funds.

### Likelihood Explanation

**High.** `queuedWithdrawalsBuffer` defaults to 0 for all assets. Any user with rsETH can call `instantWithdrawal` at any time. No special role or privilege is required. The condition is reachable whenever instant withdrawal is enabled for an asset and the vault holds funds committed to queued withdrawals.

### Recommendation

Replace the static `queuedWithdrawalsBuffer` check in `getAssetsAvailableForInstantWithdrawal` with a dynamic check that reads the actual `assetsCommitted` from `LRTWithdrawalManager`. Specifically, `LRTUnstakingVault.getAssetsAvailableForInstantWithdrawal` should subtract the withdrawal manager's `assetsCommitted[asset]` (or an equivalent on-chain committed amount) from the vault balance, rather than a manually maintained buffer that can become stale as new queued withdrawals are initiated.

### Proof of Concept

**Root cause – static buffer vs. dynamic commitments:**

`LRTUnstakingVault.getAssetsAvailableForInstantWithdrawal` uses `queuedWithdrawalsBuffer` (a static operator-set value): [1](#0-0) 

`queuedWithdrawalsBuffer` is only updated by an explicit operator call and never reflects `assetsCommitted`: [2](#0-1) 

**`instantWithdrawal` relies solely on this stale check:** [3](#0-2) 

**`initiateWithdrawal` increments `assetsCommitted` dynamically but does not update `queuedWithdrawalsBuffer`:** [4](#0-3) 

**`unlockQueue` uses raw vault balance as available assets — zero if drained:** [5](#0-4) 

**`_unlockWithdrawalRequests` exits immediately when `availableAssetAmount` is 0:** [6](#0-5)

### Citations

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

**File:** contracts/LRTWithdrawalManager.sol (L168-175)
```text
        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L230-233)
```text
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L800-800)
```text
            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request
```

**File:** contracts/LRTWithdrawalManager.sol (L846-851)
```text
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
    }
```
