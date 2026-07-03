### Title
`withdrawalDelayBlocks` Is Not Cached Per Withdrawal Request, Allowing Retroactive Parameter Changes to Temporarily Freeze Pending Withdrawals - (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager` stores a global `withdrawalDelayBlocks` parameter that determines how many blocks must pass before a queued withdrawal can be completed. This parameter is **not cached at request creation time**; instead, it is read from global state at both unlock time and completion time. If the manager changes `withdrawalDelayBlocks` after users have already initiated withdrawals, the new delay applies retroactively to all pending requests, temporarily freezing user funds beyond what was promised at initiation.

---

### Finding Description

When a user calls `initiateWithdrawal`, the `WithdrawalRequest` struct records only `rsETHUnstaked`, `expectedAssetAmount`, and `withdrawalStartBlock`. The delay parameter itself is never stored per-request. [1](#0-0) 

At completion time, `_processWithdrawalCompletion` reads `withdrawalDelayBlocks` from the current global state: [2](#0-1) 

Similarly, `_unlockWithdrawalRequests` reads the global `withdrawalDelayBlocks` when iterating over pending requests: [3](#0-2) 

The manager can change `withdrawalDelayBlocks` at any time, up to a maximum of 16 days: [4](#0-3) 

The default is 8 days / 12 seconds: [5](#0-4) 

---

### Impact Explanation

**Impact: Medium — Temporary freezing of funds.**

A user who calls `initiateWithdrawal` expecting an 8-day delay (the default) will have their rsETH locked in the contract. If the manager subsequently increases `withdrawalDelayBlocks` to the maximum of 16 days, the user's withdrawal cannot be completed or unlocked until the new, longer delay has elapsed — doubling the lock period retroactively. The user's funds are not permanently lost, but they are frozen beyond the delay that was in effect when the request was made.

The reverse scenario (decreasing `withdrawalDelayBlocks`) allows requests to be unlocked sooner than the delay that was in effect at initiation, which could be exploited to bypass the intended security delay.

---

### Likelihood Explanation

The `setWithdrawalDelayBlocks` function is callable by any address holding the `LRTManager` role. A legitimate security response (e.g., increasing the delay during a suspected exploit) would retroactively affect all pending withdrawal requests. Because the protocol always has many pending withdrawal requests in flight, any change to `withdrawalDelayBlocks` immediately affects real user funds. No attacker-controlled entry is needed beyond the manager role executing a routine parameter update.

---

### Recommendation

Cache `withdrawalDelayBlocks` inside the `WithdrawalRequest` struct at the time `initiateWithdrawal` is called, analogous to how `withdrawalStartBlock` is already cached. Use the per-request cached value in both `_processWithdrawalCompletion` and `_unlockWithdrawalRequests` instead of reading the global state.

```solidity
struct WithdrawalRequest {
    uint256 rsETHUnstaked;
    uint256 expectedAssetAmount;
    uint256 withdrawalStartBlock;
    uint256 withdrawalDelayBlocks; // <-- add this
}
```

Then in `_addUserWithdrawalRequest`:
```solidity
withdrawalRequests[requestId] = WithdrawalRequest({
    rsETHUnstaked: rsETHUnstaked,
    expectedAssetAmount: expectedAssetAmount,
    withdrawalStartBlock: block.number,
    withdrawalDelayBlocks: withdrawalDelayBlocks  // snapshot at creation
});
```

And use `request.withdrawalDelayBlocks` in the delay checks instead of the global `withdrawalDelayBlocks`.

---

### Proof of Concept

1. Alice calls `initiateWithdrawal(ETH, 10 ether, ...)` when `withdrawalDelayBlocks = 8 days / 12 = 57,600 blocks`. Her rsETH is transferred to the contract and her request is queued with `withdrawalStartBlock = N`.
2. The manager calls `setWithdrawalDelayBlocks(16 days / 12)` = 115,200 blocks, doubling the delay (e.g., in response to a security concern).
3. At block `N + 57,600` (8 days later), Alice calls `completeWithdrawal`. The check `block.number < request.withdrawalStartBlock + withdrawalDelayBlocks` evaluates as `N + 57,600 < N + 115,200` → **reverts with `WithdrawalDelayNotPassed`**.
4. Alice must wait an additional 8 days (total 16 days) to recover her funds, despite the 8-day delay being in effect when she initiated the withdrawal.

The same issue applies to `unlockQueue`: the operator cannot unlock Alice's request until the new, longer delay has elapsed, meaning the rsETH burned from Alice is also locked in the contract for the extended period. [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L94-94)
```text
        withdrawalDelayBlocks = 8 days / 12 seconds;
```

**File:** contracts/LRTWithdrawalManager.sol (L338-344)
```text
    function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
        // Set an upper limit of no more than 16 days
        if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();

        withdrawalDelayBlocks = withdrawalDelayBlocks_;
        emit WithdrawalDelayBlocksUpdated(withdrawalDelayBlocks);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L699-716)
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

**File:** contracts/LRTWithdrawalManager.sol (L744-758)
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

**File:** contracts/LRTWithdrawalManager.sol (L790-796)
```text
        while (nextLockedNonce_ < firstExcludedIndex) {
            bytes32 requestId = getRequestId(asset, nextLockedNonce_);
            WithdrawalRequest storage request = withdrawalRequests[requestId];

            // Check that the withdrawal delay has passed since the request's initiation.
            if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;

```
