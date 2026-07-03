### Title
No Cancel/Refund Mechanism for Queued Withdrawal Requests Permanently Locks User rsETH - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`LRTWithdrawalManager.initiateWithdrawal()` transfers rsETH from the user into the contract and enqueues a withdrawal request, but provides no `cancelWithdrawal()` path. If the queue cannot be unlocked — because the unstaking vault holds insufficient assets, or because the contract is paused — the user's rsETH is frozen in the contract with no on-chain recovery path.

---

### Finding Description

When a user calls `initiateWithdrawal()`, their rsETH is immediately pulled into `LRTWithdrawalManager`:

```solidity
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
``` [1](#0-0) 

The request is placed in a FIFO queue keyed by `nextUnusedNonce[asset]`. Completion requires two independent operator/protocol steps:

1. An account with `ASSET_TRANSFER_ROLE` or `OPERATOR_ROLE` must call `unlockQueue()`, which is gated by `whenNotPaused` and requires `totalAvailableAssets > 0` in the unstaking vault.
2. The `withdrawalDelayBlocks` (default 8 days, max 16 days) must elapse since the request's `withdrawalStartBlock`. [2](#0-1) 

`_unlockWithdrawalRequests` processes requests strictly in FIFO order and breaks out of the loop the moment `availableAssetAmount < payoutAmount`:

```solidity
if (availableAssetAmount < payoutAmount) break;
``` [3](#0-2) 

A grep across the entire repository for `cancelWithdrawal`, `cancelRequest`, `refundRsETH`, and `withdrawalCancel` returns **zero matches**. There is no cancel function, no `recoverTokens` inherited from `Recoverable`, and no admin escape hatch that returns rsETH to the original depositor. [4](#0-3) 

---

### Impact Explanation

**Temporary freezing of funds (Medium)** — confirmed reachable.

A user's rsETH is locked for at least `withdrawalDelayBlocks` (up to 16 days) with no ability to cancel. If the `LRTUnstakingVault` holds insufficient assets (e.g., assets are still queued in EigenLayer's withdrawal pipeline), `unlockQueue()` either reverts on `AmountMustBeGreaterThanZero` or breaks before reaching the user's request. The user cannot reclaim their rsETH during this period.

**Permanent freezing of funds (Critical edge case)** — if the contract is paused indefinitely, `unlockQueue()`, `completeWithdrawal()`, and `initiateWithdrawal()` are all blocked by `whenNotPaused`, yet the rsETH already transferred to the contract has no admin-accessible recovery function. There is no `recoverTokens` or equivalent in `LRTWithdrawalManager`. [5](#0-4) 

---

### Likelihood Explanation

The temporary freeze scenario is **high likelihood**: EigenLayer withdrawal queues routinely take days to weeks to complete, meaning the unstaking vault will frequently have zero available assets for a given LST. Any user who initiates a withdrawal during such a period has their rsETH locked with no recourse. The permanent freeze scenario requires a prolonged pause, which is lower likelihood but non-zero given the protocol has a `PAUSER_ROLE`.

---

### Recommendation

Add a `cancelWithdrawal(address asset)` function that:
1. Pops the user's oldest pending nonce from `userAssociatedNonces[asset][msg.sender]`.
2. Verifies the request has **not** yet been unlocked (i.e., its nonce ≥ `nextLockedNonce[asset]`).
3. Decrements `assetsCommitted[asset]` by `request.expectedAssetAmount`.
4. Deletes the `withdrawalRequests[requestId]` entry.
5. Returns the locked rsETH to `msg.sender`.

This mirrors the Axelar sponsor's own suggested mitigation: application-level cancel paths that return funds to the originating address when conditions make completion meaningless or impossible.

---

### Proof of Concept

1. Alice calls `initiateWithdrawal(stETH, 10e18, "")`. Her 10 rsETH is transferred to `LRTWithdrawalManager`. [6](#0-5) 

2. The `LRTUnstakingVault` currently holds 0 stETH (all assets are in EigenLayer's withdrawal queue). The operator calls `unlockQueue(stETH, ...)` — it reverts at `if (params.totalAvailableAssets == 0) revert AmountMustBeGreaterThanZero()`. [7](#0-6) 

3. Alice's request nonce remains below `nextLockedNonce[stETH]` — it is never unlocked. `completeWithdrawal()` reverts with `WithdrawalLocked`. [8](#0-7) 

4. Alice has no `cancelWithdrawal()` to call. Her 10 rsETH (representing real ETH value) is frozen in the contract for an unbounded duration. There is no admin function to return it to her. [9](#0-8)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L26-31)
```text
contract LRTWithdrawalManager is
    ILRTWithdrawalManager,
    LRTConfigRoleChecker,
    PausableUpgradeable,
    ReentrancyGuardUpgradeable
{
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

**File:** contracts/LRTWithdrawalManager.sol (L268-303)
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
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));

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

        // Updates and unlocks withdrawal requests up to a specified upper limit or until allocated assets are fully
        // utilized.
        (rsETHBurned, assetAmountUnlocked) = _unlockWithdrawalRequests(
            asset, params.totalAvailableAssets, params.rsETHPrice, params.assetPrice, firstExcludedIndex
        );
```

**File:** contracts/LRTWithdrawalManager.sol (L346-354)
```text
    /// @dev Triggers stopped state. Contract must not be paused.
    function pause() external onlyRole(LRTConstants.PAUSER_ROLE) {
        _pause();
    }

    /// @dev Returns to normal state. Contract must be paused.
    function unpause() external onlyLRTAdmin {
        _unpause();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L706-707)
```text
        // Ensure the request is already unlocked.
        if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();
```

**File:** contracts/LRTWithdrawalManager.sol (L800-800)
```text
            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request
```

**File:** contracts/interfaces/ILRTWithdrawalManager.sol (L80-98)
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
```
