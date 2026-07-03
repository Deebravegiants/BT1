### Title
User Withdrawals Permanently Frozen Without Operator Calling `unlockQueue()` - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

In `LRTWithdrawalManager`, users can call `initiateWithdrawal()` at any time to queue a withdrawal and transfer their rsETH into the contract. However, completing that withdrawal via `completeWithdrawal()` is permanently blocked unless a privileged operator (`ASSET_TRANSFER_ROLE` or `OPERATOR_ROLE`) first calls `unlockQueue()`. If those roles are lost, compromised, or simply inactive, all queued user rsETH is frozen in the contract with no permissionless escape path.

---

### Finding Description

The withdrawal lifecycle in `LRTWithdrawalManager` is a two-step process:

**Step 1 – User-initiated (permissionless):**
`initiateWithdrawal()` is callable by any user. It transfers rsETH from the user into the contract and records a `WithdrawalRequest` keyed by a monotonically increasing nonce (`nextUnusedNonce[asset]`). [1](#0-0) 

**Step 2 – Operator-gated unlock:**
`unlockQueue()` is restricted to `onlyAssetTransferOrOperatorRole`. It is the only function that advances `nextLockedNonce[asset]`. [2](#0-1) 

**The blocking check in `_processWithdrawalCompletion()`:**
When a user calls `completeWithdrawal()`, the internal function checks whether the user's nonce is below `nextLockedNonce[asset]`. If `unlockQueue()` was never called, `nextLockedNonce[asset]` remains at its initial value (0 for new assets, or the seeded value from `initialize2`/`initialize3`), and every pending withdrawal reverts with `WithdrawalLocked`. [3](#0-2) 

The `onlyAssetTransferOrOperatorRole` modifier confirms that only holders of `ASSET_TRANSFER_ROLE` or `OPERATOR_ROLE` can call `unlockQueue()`: [4](#0-3) 

**No permissionless escape hatch exists.** The only alternative withdrawal path, `instantWithdrawal()`, is also admin-gated: it requires `isInstantWithdrawalEnabled[asset] == true`, which is set exclusively by `onlyLRTManager` via `setInstantWithdrawalEnabled()`. [5](#0-4) [6](#0-5) 

---

### Impact Explanation

If the `ASSET_TRANSFER_ROLE` and `OPERATOR_ROLE` key holders are lost, become inactive, or act maliciously by refusing to call `unlockQueue()`, all rsETH deposited via `initiateWithdrawal()` is permanently frozen in `LRTWithdrawalManager`. Users have no on-chain mechanism to recover their funds. This constitutes **permanent freezing of funds** (Critical) or at minimum **temporary freezing of funds** (Medium) depending on the duration of operator inaction.

---

### Likelihood Explanation

The likelihood is medium. The `OPERATOR_ROLE` and `ASSET_TRANSFER_ROLE` are expected to be active bots/scripts that regularly call `unlockQueue()` as part of normal protocol operation. However, any extended outage, key loss, or governance failure affecting both roles simultaneously would freeze all pending withdrawals indefinitely. Users have no on-chain recourse.

---

### Recommendation

Introduce a time-based escape hatch: if a withdrawal request has been pending for longer than a defined maximum duration (e.g., `withdrawalDelayBlocks` + some grace period) without being unlocked, allow the user to cancel and reclaim their rsETH directly. This mirrors the recommendation in the original Opyn report — set a meaningful expiry on queued requests so that after expiry, users can withdraw without any dependency on a privileged role.

Concretely, add a `cancelWithdrawal()` function that:
1. Checks `block.number >= request.withdrawalStartBlock + maxCancellationDelay`
2. Returns the user's rsETH (still held in the contract)
3. Removes the request from the queue

---

### Proof of Concept

1. Alice calls `initiateWithdrawal(stETH, 1e18, "")`. Her rsETH is transferred to `LRTWithdrawalManager`. Her nonce is recorded as `N`. `nextLockedNonce[stETH]` remains at `N` (not yet advanced).

2. The operator (`ASSET_TRANSFER_ROLE`) loses their key and never calls `unlockQueue()`.

3. Alice calls `completeWithdrawal(stETH, "")`. Internally, `_processWithdrawalCompletion` executes:
   ```solidity
   uint256 usersFirstWithdrawalRequestNonce = userAssociatedNonces[stETH][Alice].popFront(); // = N
   if (N >= nextLockedNonce[stETH]) revert WithdrawalLocked(); // N >= N → always reverts
   ```

4. Alice's rsETH is permanently locked. `instantWithdrawal` is also unavailable because `isInstantWithdrawalEnabled[stETH]` is `false` (default) and only a manager can enable it. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L78-81)
```text
    modifier onlyInstantWithdrawalAllowed(address asset) {
        if (!isInstantWithdrawalEnabled[asset]) revert InstantWithdrawalNotEnabled();
        _;
    }
```

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

**File:** contracts/LRTWithdrawalManager.sol (L360-367)
```text
    function setInstantWithdrawalEnabled(address asset, bool enabled)
        external
        onlySupportedAsset(asset)
        onlyLRTManager
    {
        isInstantWithdrawalEnabled[asset] = enabled;
        emit InstantWithdrawalEnabledUpdated(asset, enabled);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L699-707)
```text
    function _processWithdrawalCompletion(address asset, address user, string calldata referralId) internal {
        if (userAssociatedNonces[asset][user].empty()) {
            revert NoWithdrawalRequests(user, asset);
        }

        // Retrieve and remove the oldest withdrawal request for the user.
        uint256 usersFirstWithdrawalRequestNonce = userAssociatedNonces[asset][user].popFront();
        // Ensure the request is already unlocked.
        if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();
```

**File:** contracts/LRTWithdrawalManager.sol (L780-815)
```text
        // Check that upper limit is in the range of existing withdrawal requests. If it is greater set it to the first
        // nonce with no withdrawal request.
        if (firstExcludedIndex > nextUnusedNonce[asset]) {
            firstExcludedIndex = nextUnusedNonce[asset];
        }

        uint256 nextLockedNonce_ = nextLockedNonce[asset];
        // Revert when trying to unlock a request that has already been unlocked
        if (nextLockedNonce_ >= firstExcludedIndex) revert NoPendingWithdrawals();

        while (nextLockedNonce_ < firstExcludedIndex) {
            bytes32 requestId = getRequestId(asset, nextLockedNonce_);
            WithdrawalRequest storage request = withdrawalRequests[requestId];

            // Check that the withdrawal delay has passed since the request's initiation.
            if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;

            // Calculate the amount user will receive
            uint256 payoutAmount = _calculatePayoutAmount(request, rsETHPrice, assetPrice);

            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request

            assetsCommitted[asset] -= request.expectedAssetAmount;
            // Set the amount the user will receive
            request.expectedAssetAmount = payoutAmount;
            rsETHAmountToBurn += request.rsETHUnstaked;
            availableAssetAmount -= payoutAmount;
            assetAmountToUnlock += payoutAmount;

            unlockedWithdrawalsCount[asset]++;

            unchecked {
                nextLockedNonce_++;
            }
        }
        nextLockedNonce[asset] = nextLockedNonce_;
```

**File:** contracts/utils/LRTConfigRoleChecker.sol (L48-56)
```text
    modifier onlyAssetTransferOrOperatorRole() {
        if (
            !IAccessControl(address(lrtConfig)).hasRole(LRTConstants.ASSET_TRANSFER_ROLE, msg.sender)
                && !IAccessControl(address(lrtConfig)).hasRole(LRTConstants.OPERATOR_ROLE, msg.sender)
        ) {
            revert ILRTConfig.CallerNotLRTConfigOperatorOrAssetTransferRole();
        }
        _;
    }
```
