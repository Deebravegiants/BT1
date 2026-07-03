### Title
Queued Withdrawal Requests Cannot Be Canceled, Permanently Freezing User rsETH When Asset Is Deprecated — (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager.initiateWithdrawal` locks user rsETH inside the contract and enqueues a withdrawal request, but the contract provides **no `cancelWithdrawal` function**. The only path to recover rsETH requires an operator to call `unlockQueue`, which carries an `onlySupportedAsset` guard. If the underlying asset is removed from the supported-asset registry before the request is unlocked, `unlockQueue` permanently reverts for that asset, and the user's rsETH is irrecoverably frozen.

---

### Finding Description

**Step 1 — rsETH is locked on `initiateWithdrawal`.**

When a user calls `initiateWithdrawal`, their rsETH is pulled into the contract and a `WithdrawalRequest` is appended to the per-asset queue: [1](#0-0) 

```solidity
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
...
assetsCommitted[asset] += expectedAssetAmount;
_addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
```

The rsETH is now held by the contract. There is no function anywhere in `LRTWithdrawalManager` or its interface that allows a user to cancel this request and reclaim their rsETH. [2](#0-1) 

**Step 2 — The only unlock path carries `onlySupportedAsset`.**

The sole mechanism that advances `nextLockedNonce[asset]` (i.e., marks requests as claimable) is `unlockQueue`: [3](#0-2) 

```solidity
function unlockQueue(
    address asset,
    ...
)
    external
    nonReentrant
    onlySupportedAsset(asset)   // ← hard gate
    whenNotPaused
    onlyAssetTransferOrOperatorRole
```

If `asset` is removed from the supported-asset registry, every call to `unlockQueue` for that asset reverts. No alternative path exists to advance `nextLockedNonce`.

**Step 3 — `completeWithdrawal` requires the request to already be unlocked.**

`completeWithdrawal` enforces that the request's nonce is below `nextLockedNonce[asset]`: [4](#0-3) 

```solidity
uint256 usersFirstWithdrawalRequestNonce = userAssociatedNonces[asset][user].popFront();
if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();
```

Because `nextLockedNonce` can never advance for a deprecated asset, `completeWithdrawal` always reverts with `WithdrawalLocked`. The user's rsETH is permanently trapped.

**Step 4 — Secondary scenario: queue head blocks all subsequent requests.**

Even without asset deprecation, `_unlockWithdrawalRequests` processes the queue strictly in FIFO order and breaks on the first request it cannot cover: [5](#0-4) 

```solidity
if (availableAssetAmount < payoutAmount) break;
```

A single large request at the head of the queue blocks every later request indefinitely. Without a cancel function, users behind the blocking request have no recourse.

---

### Impact Explanation

**Permanent freezing of user rsETH (Critical)** in the asset-deprecation scenario: the user's rsETH is held by the contract with zero recovery path. In the queue-head-blocking scenario the freeze is **temporary** (Medium) but unbounded in duration, since no cancel escape hatch exists.

---

### Likelihood Explanation

Asset deprecation is a routine protocol operation (e.g., removing a delisted LST strategy). The protocol already supports adding and removing assets via `LRTConfig`. Any deprecation of an asset that has pending withdrawal requests triggers the permanent freeze. The queue-blocking scenario requires only that one user submits a withdrawal larger than the currently available asset balance, which is a normal market condition.

---

### Recommendation

**Short term:** Add a `cancelWithdrawal(address asset)` function that:
1. Pops the caller's oldest **locked** (not yet unlocked) nonce from `userAssociatedNonces[asset][msg.sender]`.
2. Deletes the corresponding `WithdrawalRequest`.
3. Decrements `assetsCommitted[asset]` by `request.expectedAssetAmount`.
4. Returns `request.rsETHUnstaked` rsETH to the caller.

This mirrors the recommendation in the reference report: add a cancel path analogous to `Timelock.cancelTransaction`.

**Long term:** Before deprecating any asset, require that `nextLockedNonce[asset] == nextUnusedNonce[asset]` (i.e., all pending requests have been processed), or provide an admin-callable emergency drain that refunds rsETH to affected users.

---

### Proof of Concept

1. Alice calls `initiateWithdrawal(stETH, 10 ether, "")`. Her 10 rsETH is transferred to `LRTWithdrawalManager`; `nextUnusedNonce[stETH]` advances to 1; `nextLockedNonce[stETH]` remains 0.
2. The protocol governance removes stETH from supported assets (legitimate deprecation).
3. Operator attempts `unlockQueue(stETH, ...)` → reverts on `onlySupportedAsset(stETH)`.
4. Alice attempts `completeWithdrawal(stETH, "")` → `usersFirstWithdrawalRequestNonce (0) >= nextLockedNonce[stETH] (0)` → reverts with `WithdrawalLocked`.
5. Alice has no other function to call. Her 10 rsETH is permanently frozen in `LRTWithdrawalManager`. [6](#0-5) [3](#0-2) [7](#0-6)

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

**File:** contracts/LRTWithdrawalManager.sol (L268-282)
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
    {
```

**File:** contracts/LRTWithdrawalManager.sol (L699-715)
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
```

**File:** contracts/LRTWithdrawalManager.sol (L800-801)
```text
            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request

```

**File:** contracts/interfaces/ILRTWithdrawalManager.sol (L80-110)
```text
    // methods
    function getExpectedAssetAmount(address asset, uint256 amount) external view returns (uint256);

    function getAvailableAssetAmount(address asset) external view returns (uint256 assetAmount);

    function getUserWithdrawalRequest(
        address asset,
        address user,
        uint256 index
    )
        external
        view
        returns (uint256 rsETHAmount, uint256 expectedAssetAmount, uint256 withdrawalStartBlock, uint256 userNonce);

    function initiateWithdrawal(address asset, uint256 withdrawAmount, string calldata referralId) external;

    function completeWithdrawal(address asset, string calldata referralId) external;

    function completeWithdrawalForUser(address asset, address user, string calldata referralId) external;

    function unlockQueue(
        address asset,
        uint256 index,
        uint256 minimumAssetPrice,
        uint256 minimumRsEthPrice,
        uint256 maximumAssetPrice,
        uint256 maximumRsEthPrice
    )
        external
        returns (uint256 rsETHBurned, uint256 assetAmountUnlocked);

```
