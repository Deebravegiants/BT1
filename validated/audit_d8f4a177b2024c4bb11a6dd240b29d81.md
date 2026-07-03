### Title
Queued rsETH Permanently Frozen in `LRTWithdrawalManager` After Asset Removal via `removeSupportedAsset` - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

When a user calls `initiateWithdrawal()`, their rsETH is immediately transferred into `LRTWithdrawalManager`. The subsequent unlock step (`unlockQueue()`) is gated by `onlySupportedAsset(asset)`. If an admin calls `LRTConfig.removeSupportedAsset()` while withdrawal requests are still in the locked queue, `unlockQueue()` becomes permanently uncallable for that asset, and the users' rsETH has no recovery path.

---

### Finding Description

The withdrawal lifecycle in `LRTWithdrawalManager` is a two-step process:

**Step 1 — `initiateWithdrawal()`:** The user's rsETH is pulled into the contract immediately.

```solidity
// LRTWithdrawalManager.sol:166
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
```

The request is stored in `withdrawalRequests` and the nonce is added to `userAssociatedNonces[asset][user]`. The request remains *locked* (`usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]`) until an operator calls `unlockQueue`.

**Step 2 — `unlockQueue()`:** This is the only function that advances `nextLockedNonce[asset]`, burns the held rsETH, and pulls the underlying asset from the vault. It carries the `onlySupportedAsset(asset)` modifier:

```solidity
// LRTWithdrawalManager.sol:268-280
function unlockQueue(
    address asset,
    ...
)
    external
    nonReentrant
    onlySupportedAsset(asset)   // <-- reverts if asset removed
    whenNotPaused
    onlyAssetTransferOrOperatorRole
```

`onlySupportedAsset` is inherited from `LRTConfigRoleChecker` and delegates to `lrtConfig.isSupportedAsset[asset]`.

**The removal path — `LRTConfig.removeSupportedAsset()`:**

```solidity
// LRTConfig.sol:66-93
function removeSupportedAsset(address asset, uint256 tokenIndex)
    external
    onlySupportedAsset(asset)
    onlyRole(DEFAULT_ADMIN_ROLE)
{
    ...
    if (ILRTDepositPool(depositPool).getTotalAssetDeposits(asset) > maxNegligibleAmount) {
        revert CannotRemoveAssetWithDeposits(asset);
    }

    delete isSupportedAsset[asset];
    delete assetStrategy[asset];
    ...
}
```

The only guard is `getTotalAssetDeposits(asset)` on the deposit pool. This function aggregates assets in the deposit pool, NDCs, and EigenLayer strategies. It does **not** inspect:
- `assetsCommitted[asset]` in `LRTWithdrawalManager` (the LST amount promised to locked requests)
- The rsETH balance held in `LRTWithdrawalManager` (already transferred from users in Step 1)

Therefore, it is possible for `getTotalAssetDeposits` to return 0 (or ≤ `maxNegligibleAmount`) while `LRTWithdrawalManager` still holds rsETH for locked withdrawal requests targeting that asset.

Once `removeSupportedAsset` executes:
- `isSupportedAsset[asset]` is deleted → `false`
- Every subsequent call to `unlockQueue(asset, ...)` reverts with `AssetNotSupported`
- `completeWithdrawal(asset)` requires the request to be unlocked first (`usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]` → `WithdrawalLocked`), which can never happen
- There is no escape hatch, no `cancelWithdrawal`, and no admin function to return the stuck rsETH

---

### Impact Explanation

**Critical — Permanent freezing of funds.**

All rsETH transferred into `LRTWithdrawalManager` for locked withdrawal requests targeting the removed asset is permanently unrecoverable. Users cannot complete their withdrawal (request is locked), cannot cancel it (no such function exists), and the operator cannot unlock the queue (gated by `onlySupportedAsset`). The rsETH sits in the contract indefinitely with no code path to retrieve it.

---

### Likelihood Explanation

**Low.** Asset removal is a legitimate operational action (e.g., deprecating a supported LST). The guard `getTotalAssetDeposits > maxNegligibleAmount` provides partial protection but does not cover the withdrawal manager's pending queue. The window exists whenever users have initiated withdrawals for an asset that the protocol subsequently decides to deprecate, and the operator has not yet called `unlockQueue` for those requests before removal.

---

### Recommendation

Before allowing `removeSupportedAsset` to proceed, verify that no locked withdrawal requests exist for the asset in `LRTWithdrawalManager`:

```solidity
// In LRTConfig.removeSupportedAsset, add:
address withdrawalManager = getContract(LRTConstants.LRT_WITHDRAW_MANAGER);
if (ILRTWithdrawalManager(withdrawalManager).assetsCommitted(asset) > 0) {
    revert PendingWithdrawalRequestsExist(asset);
}
```

Alternatively, add a privileged `cancelWithdrawal` function in `LRTWithdrawalManager` that returns rsETH to users when an asset is no longer supported, analogous to the recommendation in the external report to set `redemptionCooldownPeriod` to 0 on sunset.

---

### Proof of Concept

1. Alice calls `initiateWithdrawal(stETH, 10e18, "")`. `LRTWithdrawalManager` receives 10e18 rsETH. The request is stored at nonce `N` with `nextLockedNonce[stETH] = N` (still locked).

2. The protocol decides to deprecate stETH. All stETH has been unstaked from EigenLayer and moved to the unstaking vault. `getTotalAssetDeposits(stETH)` returns 0 (or ≤ `maxNegligibleAmount`).

3. Admin calls `LRTConfig.removeSupportedAsset(stETH, 0)`. The guard passes. `isSupportedAsset[stETH]` is deleted.

4. Operator attempts `unlockQueue(stETH, N+1, ...)` → reverts: `AssetNotSupported`.

5. Alice attempts `completeWithdrawal(stETH, "")` → `_processWithdrawalCompletion` checks `usersFirstWithdrawalRequestNonce (N) >= nextLockedNonce[stETH] (N)` → reverts: `WithdrawalLocked`.

6. Alice's 10e18 rsETH is permanently locked in `LRTWithdrawalManager` with no recovery path. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L150-178)
```text
    function initiateWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        override
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L268-281)
```text
    function unlockQueue(
        address asset,
        uint256 firstExcludedIndex,
        uint256 minimumAssetPrice,
        uint256 minimumRsEthPrice,
        uint256 maximumAssetPrice,
        uint256 maximumRsEthPrice
    )
        external
        nonReentrant
        onlySupportedAsset(asset)
        whenNotPaused
        onlyAssetTransferOrOperatorRole
        returns (uint256 rsETHBurned, uint256 assetAmountUnlocked)
```

**File:** contracts/LRTWithdrawalManager.sol (L700-715)
```text
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
```

**File:** contracts/LRTConfig.sol (L66-94)
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
    }
```
