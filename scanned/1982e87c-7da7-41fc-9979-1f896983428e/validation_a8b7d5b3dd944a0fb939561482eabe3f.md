### Title
`instantWithdrawal` Ignores `assetsCommitted` When Draining the Unstaking Vault, Freezing Queued Withdrawals - (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager.instantWithdrawal` checks vault availability via `LRTUnstakingVault.getAssetsAvailableForInstantWithdrawal`, which relies on a static, manually-set `queuedWithdrawalsBuffer`. This buffer is never automatically synchronized with `assetsCommitted`, the live accounting variable that tracks how much of the protocol's assets are already promised to pending queued-withdrawal users. An unprivileged rsETH holder can therefore drain the unstaking vault of assets that are committed to queued withdrawals, temporarily freezing those withdrawals.

---

### Finding Description

**Two separate, unlinked accounting systems govern the same pool of assets:**

**System 1 — Queued withdrawal commitments (`assetsCommitted`):**

`initiateWithdrawal` increases `assetsCommitted[asset]` by the expected payout and enforces that new requests cannot exceed `getAvailableAssetAmount`:

```
getAvailableAssetAmount = getTotalAssetDeposits(asset) − assetsCommitted[asset]
``` [1](#0-0) 

`assetsCommitted` is only decremented inside `_unlockWithdrawalRequests` when the operator calls `unlockQueue`: [2](#0-1) 

**System 2 — Instant withdrawal vault protection (`queuedWithdrawalsBuffer`):**

`instantWithdrawal` checks a completely different limit:

```solidity
if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset))
    revert CantInstantWithdrawMoreThanAvailable();
``` [3](#0-2) 

`getAssetsAvailableForInstantWithdrawal` returns `vaultBalance − queuedWithdrawalsBuffer[asset]`: [4](#0-3) 

`queuedWithdrawalsBuffer` is a static value set manually by the operator via `setQueuedWithdrawalsBuffer`: [5](#0-4) 

**The gap:** `assetsCommitted` changes dynamically with every `initiateWithdrawal` and `unlockQueue` call. `queuedWithdrawalsBuffer` is never automatically updated to match. Its default value is `0`, meaning the entire vault balance is exposed to instant withdrawals regardless of how much is committed to queued users. Even if an operator sets it once, it becomes stale the moment any queued withdrawal is initiated or completed.

`instantWithdrawal` also does **not** update `assetsCommitted`, so after draining the vault it leaves the committed accounting intact while the underlying assets are gone: [6](#0-5) 

---

### Impact Explanation

**Temporary freezing of funds — Medium.**

Queued-withdrawal users burn their rsETH at `initiateWithdrawal` time. If the unstaking vault is subsequently drained by instant withdrawals before `unlockQueue` is called, `unlockQueue` will find an empty vault and be unable to fulfill those requests. The affected users' rsETH is already destroyed; they cannot recover their assets until the operator re-unstakes from EigenLayer and replenishes the vault. Because the protocol can eventually replenish the vault, the freeze is temporary rather than permanent, but it can be prolonged by EigenLayer's withdrawal delay.

---

### Likelihood Explanation

**Medium.** Three conditions must hold simultaneously:

1. `isInstantWithdrawalEnabled[asset]` is `true` (set by manager — a normal operational state).
2. The unstaking vault holds a non-trivial balance (normal after any EigenLayer unstaking cycle).
3. `queuedWithdrawalsBuffer[asset]` is zero or stale relative to `assetsCommitted[asset]` (the default and the common case between operator updates).

All three are routine protocol states. No privileged key compromise is required; any rsETH holder can call `instantWithdrawal`.

---

### Recommendation

Replace the static `queuedWithdrawalsBuffer` with a dynamic computation that reads `assetsCommitted` from `LRTWithdrawalManager` directly:

```solidity
function getAssetsAvailableForInstantWithdrawal(address asset)
    external view returns (uint256 availableAmount)
{
    uint256 vaultBalance = balanceOf(asset);
    uint256 committed = ILRTWithdrawalManager(withdrawalManager).assetsCommitted(asset);
    availableAmount = vaultBalance > committed ? vaultBalance - committed : 0;
}
```

This mirrors the recommendation in the reference report: the accounting state that limits withdrawals must be transferred (or in this case, read) wherever assets can be redeemed.

---

### Proof of Concept

1. **Setup:** `isInstantWithdrawalEnabled[stETH] = true`; `queuedWithdrawalsBuffer[stETH] = 0` (default).
2. **Alice** calls `initiateWithdrawal(stETH, rsETHAmount)`. `assetsCommitted[stETH] += X` (e.g., X = 100 stETH). Alice's rsETH is transferred to the withdrawal manager.
3. **Operator** unstakes 100 stETH from EigenLayer; 100 stETH lands in `LRTUnstakingVault`.
4. **Bob** (any rsETH holder) calls `instantWithdrawal(stETH, rsETHAmount2)` where the expected payout ≤ 100 stETH. `getAssetsAvailableForInstantWithdrawal` returns `100 − 0 = 100`, so the check passes. Bob receives 100 stETH from the vault; vault balance → 0.
5. **Operator** calls `unlockQueue(stETH, ...)`. `_unlockWithdrawalRequests` calls `unstakingVault.redeem(stETH, payoutAmount)`. The vault has 0 stETH; the call reverts or sends nothing.
6. **Alice** calls `completeWithdrawal(stETH, ...)`. Her request is still locked (`nextLockedNonce` was never advanced). Her rsETH is already burned; she cannot withdraw until the vault is replenished. [7](#0-6) [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L170-173)
```text
        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L212-235)
```text
    function instantWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
        onlyInstantWithdrawalAllowed(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }
        if (IERC20(lrtConfig.rsETH()).balanceOf(msg.sender) < rsETHUnstaked) revert NotEnoughRsETH();
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
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

**File:** contracts/LRTWithdrawalManager.sol (L802-802)
```text
            assetsCommitted[asset] -= request.expectedAssetAmount;
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
