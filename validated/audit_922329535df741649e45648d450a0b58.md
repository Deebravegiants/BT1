### Title
No Cancellation Mechanism for Pending Withdrawal Requests Permanently Locks User rsETH Until Operator Action - (File: `contracts/LRTWithdrawalManager.sol`)

### Summary
Once a user calls `initiateWithdrawal()`, their rsETH is immediately transferred into `LRTWithdrawalManager` and queued. There is no `cancelWithdrawal()` function anywhere in the contract or its interface. The user's rsETH remains locked until an operator calls `unlockQueue()` and the `withdrawalDelayBlocks` delay elapses — a process that can span many days and depends entirely on operator availability.

### Finding Description
`initiateWithdrawal()` pulls rsETH from the caller into the contract and registers a `WithdrawalRequest` keyed by a monotonically incrementing per-asset nonce:

```solidity
// contracts/LRTWithdrawalManager.sol:166
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
...
_addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
``` [1](#0-0) 

The only forward path is:
1. An operator (holding `ASSET_TRANSFER_ROLE` or `LRT_OPERATOR_ROLE`) calls `unlockQueue()`.
2. `withdrawalDelayBlocks` (default ≈ 8 days) elapses from the block the request was created.
3. The user (or an operator) calls `completeWithdrawal()`. [2](#0-1) 

Neither `ILRTWithdrawalManager` nor `LRTWithdrawalManager` exposes any function to cancel a queued-but-not-yet-unlocked request and return the deposited rsETH to the user. [3](#0-2) 

Additionally, `completeWithdrawal` is guarded by `whenNotPaused`, so if the contract is paused while a request is in the locked state, the user can neither cancel nor complete — their rsETH is frozen for the pause duration. [4](#0-3) 

### Impact Explanation
**Medium — Temporary freezing of funds.**

A user who initiates a withdrawal cannot recover their rsETH if circumstances change (e.g., they need liquidity urgently, the rsETH/asset exchange rate moves against them before `unlockQueue` is called, or the protocol is paused). The rsETH is held in the contract for at minimum `withdrawalDelayBlocks` (≈ 8 days, up to 16 days) with no escape hatch. During a pause, the freeze is indefinite from the user's perspective.

### Likelihood Explanation
**Medium.**

Any user who initiates a withdrawal and subsequently wants to reverse the decision — due to changed market conditions, an urgent need for liquidity, or a protocol pause — is affected. The withdrawal queue is a core user-facing flow, and the absence of a cancel path is a structural gap that will be encountered in normal protocol operation.

### Recommendation
Add a `cancelWithdrawal(address asset)` function that:
1. Is callable only by the request owner.
2. Only operates on requests that are still in the **locked** state (i.e., `userNonce >= nextLockedNonce[asset]`).
3. Removes the request from `userAssociatedNonces`, decrements `assetsCommitted[asset]`, and returns the rsETH to the caller.

```solidity
function cancelWithdrawal(address asset) external nonReentrant whenNotPaused {
    if (userAssociatedNonces[asset][msg.sender].empty())
        revert NoWithdrawalRequests(msg.sender, asset);

    uint256 userNonce = userAssociatedNonces[asset][msg.sender].back();
    // Only allow cancellation of still-locked requests
    if (userNonce < nextLockedNonce[asset]) revert WithdrawalAlreadyUnlocked();

    userAssociatedNonces[asset][msg.sender].popBack();
    bytes32 requestId = getRequestId(asset, userNonce);
    WithdrawalRequest memory request = withdrawalRequests[requestId];
    delete withdrawalRequests[requestId];

    assetsCommitted[asset] -= request.expectedAssetAmount;
    IERC20(lrtConfig.rsETH()).safeTransfer(msg.sender, request.rsETHUnstaked);
}
```

### Proof of Concept
1. Alice calls `initiateWithdrawal(stETH, 10e18, "")`. Her 10 rsETH is transferred to `LRTWithdrawalManager`; `assetsCommitted[stETH]` increases.
2. The rsETH/stETH rate moves sharply in Alice's favour. She wants to cancel, re-hold rsETH, and withdraw later at a better rate.
3. Alice searches the ABI — no `cancelWithdrawal` exists.
4. Alice must wait for an operator to call `unlockQueue` and then wait `withdrawalDelayBlocks` (≈ 57,600 blocks / 8 days) before she can call `completeWithdrawal`.
5. If the contract is paused at any point during this window, `completeWithdrawal` reverts with `Pausable: paused`, and Alice has no recourse — her rsETH remains locked for the duration of the pause. [5](#0-4) [6](#0-5)

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

**File:** contracts/LRTWithdrawalManager.sol (L183-185)
```text
    function completeWithdrawal(address asset, string calldata referralId) external nonReentrant whenNotPaused {
        _processWithdrawalCompletion(asset, msg.sender, referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L700-716)
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

**File:** contracts/interfaces/ILRTWithdrawalManager.sol (L80-99)
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
