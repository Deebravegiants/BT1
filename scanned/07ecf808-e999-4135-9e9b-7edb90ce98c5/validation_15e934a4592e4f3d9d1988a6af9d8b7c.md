### Title
Retroactive Application of Increased `withdrawalDelayBlocks` Temporarily Freezes Already-Unlocked User Withdrawals - (File: contracts/LRTWithdrawalManager.sol)

### Summary

`LRTWithdrawalManager.setWithdrawalDelayBlocks()` allows the manager to update `withdrawalDelayBlocks` at any time with no protection for existing withdrawal requests. Because both the `unlockQueue` path and the `completeWithdrawal` path read the **current** value of `withdrawalDelayBlocks` rather than the value that was in effect when a request was created, increasing the delay retroactively re-locks withdrawals that users already expected to be claimable — including requests that the operator had already explicitly unlocked.

### Finding Description

`withdrawalDelayBlocks` is a global mutable variable initialized to `8 days / 12 seconds` and updatable by the LRT manager with no lower bound and an upper bound of `16 days / 12 seconds`. [1](#0-0) 

The variable is consumed in two critical places:

**1. `_unlockWithdrawalRequests` (operator-facing)** [2](#0-1) 

**2. `_processWithdrawalCompletion` (user-facing)** [3](#0-2) 

Neither path snapshots the delay at request-creation time. Both use the live storage value. A withdrawal request stores only `withdrawalStartBlock`: [4](#0-3) 

**Scenario A — already-unlocked request re-locked for the user:**

1. User calls `initiateWithdrawal` at block N; `withdrawalDelayBlocks = 57,600` (8 days).
2. Operator calls `unlockQueue` at block N + 57,601; the delay check passes, `nextLockedNonce` advances, `unlockedWithdrawalsCount` increments.
3. Manager calls `setWithdrawalDelayBlocks(115_200)` (16 days).
4. User calls `completeWithdrawal`. The check `block.number < N + 115_200` now fails with `WithdrawalDelayNotPassed`, even though the operator already confirmed the request was eligible.

The user's rsETH was burned at step 1 and cannot be recovered until block N + 115,200.

**Scenario B — pending (locked) requests blocked from being unlocked:**

If `withdrawalDelayBlocks` is increased before `unlockQueue` is called, the `break` in `_unlockWithdrawalRequests` fires for every request that passed the old delay but not the new one, stalling the entire unlock queue for those assets. [5](#0-4) 

### Impact Explanation

Users who have already burned rsETH via `initiateWithdrawal` and whose requests have been unlocked by the operator are unable to call `completeWithdrawal` to receive their LST/ETH. Their funds are frozen for up to an additional 8 days (the maximum increase from 8 to 16 days). This constitutes **temporary freezing of funds** (Medium severity per the allowed impact scope).

### Likelihood Explanation

The manager role is a privileged but operationally active role that is expected to tune protocol parameters. Increasing `withdrawalDelayBlocks` is a plausible legitimate action (e.g., in response to a security incident or EigenLayer withdrawal period changes). The absence of any guard against retroactive application makes this a realistic operational mistake, not a theoretical one.

### Recommendation

Snapshot `withdrawalDelayBlocks` into each `WithdrawalRequest` struct at the time `initiateWithdrawal` is called, and use the per-request snapshot in both `_unlockWithdrawalRequests` and `_processWithdrawalCompletion`:

```solidity
struct WithdrawalRequest {
    uint256 rsETHUnstaked;
    uint256 expectedAssetAmount;
    uint256 withdrawalStartBlock;
    uint256 withdrawalDelayBlocksSnapshot; // add this
}
```

Then in `_addUserWithdrawalRequest`:
```solidity
withdrawalRequests[requestId] = WithdrawalRequest({
    rsETHUnstaked: rsETHUnstaked,
    expectedAssetAmount: expectedAssetAmount,
    withdrawalStartBlock: block.number,
    withdrawalDelayBlocksSnapshot: withdrawalDelayBlocks
});
```

And replace both delay checks with `request.withdrawalDelayBlocksSnapshot`.

### Proof of Concept

1. `withdrawalDelayBlocks = 57_600` (8 days at 12 s/block).
2. Alice calls `initiateWithdrawal(ETH, 1 ether, "")` at block 1_000_000. Her rsETH is transferred to the contract.
3. At block 1_057_601, the operator calls `unlockQueue(ETH, ...)`. The check `block.number < 1_000_000 + 57_600` → `1_057_601 < 1_057_600` is false, so Alice's request is unlocked. `nextLockedNonce[ETH]` advances past her nonce.
4. Manager calls `setWithdrawalDelayBlocks(115_200)`.
5. Alice calls `completeWithdrawal(ETH, "")`. Inside `_processWithdrawalCompletion`, the check `block.number < request.withdrawalStartBlock + withdrawalDelayBlocks` evaluates to `1_057_601 < 1_000_000 + 115_200 = 1_115_200` → **true** → reverts with `WithdrawalDelayNotPassed`.
6. Alice cannot recover her ETH until block 1_115_200, approximately 8 additional days beyond her original expectation. [1](#0-0) [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L338-344)
```text
    function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
        // Set an upper limit of no more than 16 days
        if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();

        withdrawalDelayBlocks = withdrawalDelayBlocks_;
        emit WithdrawalDelayBlocksUpdated(withdrawalDelayBlocks);
    }
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

**File:** contracts/LRTWithdrawalManager.sol (L744-757)
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
```

**File:** contracts/LRTWithdrawalManager.sol (L790-795)
```text
        while (nextLockedNonce_ < firstExcludedIndex) {
            bytes32 requestId = getRequestId(asset, nextLockedNonce_);
            WithdrawalRequest storage request = withdrawalRequests[requestId];

            // Check that the withdrawal delay has passed since the request's initiation.
            if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;
```
