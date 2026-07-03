### Title
Withdrawal Queue Permanently Blocked When Asset Strategy Is Removed During Pending Withdrawal Period - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`LRTWithdrawalManager.unlockQueue()` enforces the `onlySupportedStrategy` modifier, which reverts when `lrtConfig.assetStrategy(asset) == address(0)`. `LRTConfig.removeSupportedAsset()` deletes `assetStrategy[asset]`, setting it to `address(0)`. If users have pending withdrawal requests for an asset that is subsequently removed, `unlockQueue` permanently reverts for that asset, and the rsETH already transferred into the withdrawal manager by those users can never be processed or refunded.

---

### Finding Description

The withdrawal flow in `LRTWithdrawalManager` is a two-step process:

**Step 1 – Initiation:** A user calls `initiateWithdrawal(asset, rsETHUnstaked, ...)`. The contract transfers `rsETHUnstaked` from the user, records a `WithdrawalRequest` via `_addUserWithdrawalRequest`, and increments `assetsCommitted[asset]`. [1](#0-0) 

**Step 2 – Unlock:** An operator calls `unlockQueue(asset, ...)` to process queued requests and make them claimable. This function is gated by the `onlySupportedStrategy` modifier: [2](#0-1) 

The modifier checks `lrtConfig.assetStrategy(asset) == address(0)` and reverts with `StrategyNotSupported()` if true.

**The gap:** `LRTConfig.removeSupportedAsset()` is callable by `DEFAULT_ADMIN_ROLE` and executes:

```solidity
delete isSupportedAsset[asset];
delete assetStrategy[asset];   // sets to address(0)
``` [3](#0-2) 

The guard in `removeSupportedAsset` only checks `getTotalAssetDeposits(asset) > maxNegligibleAmount`: [4](#0-3) 

`assetsCommitted[asset]` in `LRTWithdrawalManager` — representing rsETH already burned/committed for withdrawal — is tracked separately from the deposit pool and node delegator balances. If the underlying asset has been fully moved through the unstaking pipeline (so `getTotalAssetDeposits` returns ≤ `maxNegligibleAmount`), the admin can call `removeSupportedAsset` even while users have live, unprocessed withdrawal requests. After removal, every subsequent call to `unlockQueue(asset, ...)` reverts permanently, and `_processWithdrawalCompletion` can never be reached for those requests. [5](#0-4) 

---

### Impact Explanation

**Temporary-to-permanent freezing of funds.** The rsETH transferred by users into `LRTWithdrawalManager` during `initiateWithdrawal` is held in the contract. Because `unlockQueue` is the only path to advance `nextLockedNonce[asset]`, and because `_processWithdrawalCompletion` requires `usersFirstWithdrawalRequestNonce < nextLockedNonce[asset]`, no user can ever claim their withdrawal for the removed asset. There is no fallback refund path. The rsETH remains locked indefinitely.

**Impact rating: Medium** — Temporary (potentially permanent) freezing of user funds.

---

### Likelihood Explanation

**Likelihood: Medium.** The scenario requires:
1. An asset to be in the process of being wound down (assets moved out of EigenLayer strategies, so `getTotalAssetDeposits` is negligible).
2. Users to have initiated withdrawals for that asset before the removal.
3. Admin to call `removeSupportedAsset` while those requests are still pending.

This is a realistic operational sequence during asset deprecation. The admin may not be aware that `assetsCommitted` in the withdrawal manager is not counted by the `getTotalAssetDeposits` guard, making this an easy mistake to make during a legitimate asset removal.

---

### Recommendation

1. **In `LRTConfig.removeSupportedAsset`:** Also check that `LRTWithdrawalManager.assetsCommitted(asset) == 0` before allowing removal, ensuring no pending withdrawal obligations exist for the asset.

2. **In `LRTWithdrawalManager.unlockQueue`:** Remove or relax the `onlySupportedStrategy` modifier so that already-queued requests for a de-listed asset can still be processed and users can receive their funds.

3. **Add a refund path:** Allow users to cancel a pending withdrawal request and reclaim their rsETH if the asset's strategy has been removed.

---

### Proof of Concept

1. stETH is a supported asset with `assetStrategy[stETH] = 0xStrategyAddr`.
2. Alice calls `initiateWithdrawal(stETH, 10e18)` — 10 rsETH is transferred to `LRTWithdrawalManager`, `assetsCommitted[stETH] += X`, and a `WithdrawalRequest` is stored.
3. The protocol winds down stETH: all stETH is unstaked from EigenLayer and moved to the unstaking vault. `getTotalAssetDeposits(stETH)` now returns 0 (or ≤ `maxNegligibleAmount`).
4. Admin calls `LRTConfig.removeSupportedAsset(stETH, idx)`. The guard passes. `assetStrategy[stETH]` is deleted (set to `address(0)`).
5. Operator calls `unlockQueue(stETH, ...)`. The `onlySupportedStrategy` modifier evaluates `lrtConfig.assetStrategy(stETH) == address(0)` → `true` → reverts with `StrategyNotSupported()`.
6. Alice calls `completeWithdrawal(stETH, ...)`. It reverts with `WithdrawalLocked()` because `nextLockedNonce[stETH]` was never advanced.
7. Alice's 10 rsETH is permanently locked in `LRTWithdrawalManager` with no refund mechanism. [2](#0-1) [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L71-76)
```text
    modifier onlySupportedStrategy(address asset) {
        if (asset != LRTConstants.ETH_TOKEN && lrtConfig.assetStrategy(asset) == address(0)) {
            revert StrategyNotSupported();
        }
        _;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L699-717)
```text
    function _processWithdrawalCompletion(address asset, address user, string calldata referralId) internal {
        if (userAssociatedNonces[asset][user].empty()) {
            revert NoWithdrawalRequests(user, asset);
        }

        // Retrieve and remove the oldest withdrawal request for the user.
        uint256 usersFirstWithdrawalRequestNonce = userAssociatedNonces[asset][user].popFront();
        // Ensure the request is already unlocked.
        if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();

        bytes32 requestId = getRequestId(asset, usersFirstWithdrawalRequestNonce);
        WithdrawalRequest memory request = withdrawalRequests[requestId];

        delete withdrawalRequests[requestId];

        // Check that the withdrawal delay has passed since the request's initiation.
        if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();

        unlockedWithdrawalsCount[asset]--;
```

**File:** contracts/LRTWithdrawalManager.sol (L744-759)
```text
    function _addUserWithdrawalRequest(address asset, uint256 rsETHUnstaked, uint256 expectedAssetAmount) internal {
        uint256 nextUnusedNonce_ = nextUnusedNonce[asset];

        // Generate a unique identifier for the new withdrawal request.
        bytes32 requestId = getRequestId(asset, nextUnusedNonce_);

        // Create and store the new withdrawal request.
        withdrawalRequests[requestId] = WithdrawalRequest({
            rsETHUnstaked: rsETHUnstaked, expectedAssetAmount: expectedAssetAmount, withdrawalStartBlock: block.number
        });

        // Map the user to the newly created request index and increment the nonce for future requests.
        userAssociatedNonces[asset][msg.sender].pushBack(nextUnusedNonce_);
        nextUnusedNonce[asset] = nextUnusedNonce_ + 1;

        emit AssetWithdrawalQueued(msg.sender, asset, rsETHUnstaked, nextUnusedNonce_);
```

**File:** contracts/LRTConfig.sol (L66-93)
```text
    function removeSupportedAsset(
        address asset,
        uint256 tokenIndex
    )
        external
        onlySupportedAsset(asset)
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        UtilLib.checkNonZeroAddress(asset);

        if (supportedAssetList[tokenIndex] != asset) {
            revert TokenNotFoundError();
        }

        address depositPool = getContract(LRTConstants.LRT_DEPOSIT_POOL);

        if (ILRTDepositPool(depositPool).getTotalAssetDeposits(asset) > maxNegligibleAmount) {
            revert CannotRemoveAssetWithDeposits(asset);
        }

        delete isSupportedAsset[asset];
        delete assetStrategy[asset];
        depositLimitByAsset[asset] = 0;

        supportedAssetList[tokenIndex] = supportedAssetList[supportedAssetList.length - 1];
        supportedAssetList.pop();

        emit RemovedSupportedAsset(asset);
```
