### Title
Changing `withdrawalDelayBlocks` Retroactively Affects All Pending Withdrawal Requests — (`contracts/LRTWithdrawalManager.sol`)

### Summary

`LRTWithdrawalManager` stores only the `withdrawalStartBlock` at withdrawal initiation time, but computes the unlock deadline dynamically as `withdrawalStartBlock + withdrawalDelayBlocks` at claim/unlock time. Because `withdrawalDelayBlocks` is a mutable parameter settable by the LRT Manager at any time, any change to it immediately and retroactively affects all in-flight withdrawal requests, potentially freezing user funds beyond the delay they agreed to, or unlocking them prematurely.

### Finding Description

When a user calls `initiateWithdrawal()`, the internal `_addUserWithdrawalRequest()` records only the block number at which the request was created: [1](#0-0) 

The unlock deadline is never stored. Instead, it is recomputed on every check using the **current** value of `withdrawalDelayBlocks`:

In `_unlockWithdrawalRequests()`: [2](#0-1) 

In `_processWithdrawalCompletion()`: [3](#0-2) 

The LRT Manager can update `withdrawalDelayBlocks` at any time with no restriction on whether pending requests exist: [4](#0-3) 

The upper bound is 16 days (in blocks), and the default is 8 days: [5](#0-4) 

### Impact Explanation

**Temporary freezing of funds (Medium).** If the LRT Manager increases `withdrawalDelayBlocks` while withdrawal requests are pending, users who initiated withdrawals expecting an 8-day delay will find their funds locked for up to 16 days instead — double the expected wait. Their rsETH has already been transferred to the contract at `initiateWithdrawal()` time, so they cannot cancel or recover it during the extended lock period. Conversely, a decrease in `withdrawalDelayBlocks` causes the `_unlockWithdrawalRequests()` loop to unlock requests earlier than the delay users were shown at initiation, which may allow the operator to unlock and settle withdrawals at a less favorable exchange rate window than users anticipated.

### Likelihood Explanation

The LRT Manager role is a privileged but non-admin role that can be held by a multisig or operational key. The function `setWithdrawalDelayBlocks()` has no guard checking for pending requests, no timelock, and no event-based warning to users. Any routine parameter adjustment (e.g., responding to EigenLayer queue changes) would silently retroact on all pending withdrawals. This is a realistic operational scenario.

### Recommendation

Store the computed unlock block at request creation time, analogous to the mitigation suggested in the referenced BendDAO report:

```diff
 withdrawalRequests[requestId] = WithdrawalRequest({
     rsETHUnstaked: rsETHUnstaked,
     expectedAssetAmount: expectedAssetAmount,
-    withdrawalStartBlock: block.number
+    withdrawalUnlockBlock: block.number + withdrawalDelayBlocks
 });
```

Then replace both deadline checks:
```diff
- if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();
+ if (block.number < request.withdrawalUnlockBlock) revert WithdrawalDelayNotPassed();
```
```diff
- if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;
+ if (block.number < request.withdrawalUnlockBlock) break;
```

### Proof of Concept

1. Alice calls `initiateWithdrawal(ETH, 1e18, "")` at block 1000. Her rsETH is transferred to the contract. `withdrawalStartBlock = 1000` is stored. With `withdrawalDelayBlocks = 57600` (8 days), she expects to claim at block ~58600.

2. At block 2000, the LRT Manager calls `setWithdrawalDelayBlocks(115200)` (16 days), e.g., to align with a new EigenLayer queue policy.

3. Alice calls `completeWithdrawal(ETH, "")` at block 58600. The check evaluates: `58600 < 1000 + 115200` → `58600 < 116200` → **reverts with `WithdrawalDelayNotPassed`**.

4. Alice's ETH is frozen for an additional ~8 days beyond what she agreed to at initiation, with no recourse since she cannot cancel the withdrawal. [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8) [10](#0-9)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L36-36)
```text
    uint256 public withdrawalDelayBlocks;
```

**File:** contracts/LRTWithdrawalManager.sol (L94-94)
```text
        withdrawalDelayBlocks = 8 days / 12 seconds;
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

**File:** contracts/LRTWithdrawalManager.sol (L338-343)
```text
    function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
        // Set an upper limit of no more than 16 days
        if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();

        withdrawalDelayBlocks = withdrawalDelayBlocks_;
        emit WithdrawalDelayBlocksUpdated(withdrawalDelayBlocks);
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

**File:** contracts/LRTWithdrawalManager.sol (L744-760)
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
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L790-795)
```text
        while (nextLockedNonce_ < firstExcludedIndex) {
            bytes32 requestId = getRequestId(asset, nextLockedNonce_);
            WithdrawalRequest storage request = withdrawalRequests[requestId];

            // Check that the withdrawal delay has passed since the request's initiation.
            if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;
```
