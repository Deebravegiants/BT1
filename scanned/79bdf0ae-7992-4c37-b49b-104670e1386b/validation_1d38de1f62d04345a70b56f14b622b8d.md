### Title
LRT Manager Can Retroactively Extend `withdrawalDelayBlocks` to Temporarily Freeze In-Flight rsETH Withdrawal Requests — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager` stores only `withdrawalStartBlock` per request at initiation time but reads the global `withdrawalDelayBlocks` dynamically at completion and unlock time. The LRT manager can call `setWithdrawalDelayBlocks()` at any point to increase the delay up to `16 days / 12 seconds` blocks, retroactively extending the wait for every already-queued withdrawal. Because rsETH is transferred into the contract at initiation, users' funds are locked for longer than the delay in effect when they submitted their request.

---

### Finding Description

When a user calls `initiateWithdrawal`, the contract records only the current block number: [1](#0-0) 

```solidity
withdrawalRequests[requestId] = WithdrawalRequest({
    rsETHUnstaked: rsETHUnstaked, expectedAssetAmount: expectedAssetAmount, withdrawalStartBlock: block.number
});
```

The delay check in `_processWithdrawalCompletion` (called by both `completeWithdrawal` and `completeWithdrawalForUser`) reads the **current global** `withdrawalDelayBlocks`, not a value snapshotted at initiation: [2](#0-1) 

```solidity
if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();
```

The same live read occurs in `_unlockWithdrawalRequests`, which gates the operator-driven unlock step: [3](#0-2) 

```solidity
if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;
```

The manager can raise `withdrawalDelayBlocks` at any time up to the hard cap: [4](#0-3) 

```solidity
function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
    // Set an upper limit of no more than 16 days
    if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();
    withdrawalDelayBlocks = withdrawalDelayBlocks_;
    emit WithdrawalDelayBlocksUpdated(withdrawalDelayBlocks);
}
```

The default is `8 days / 12 seconds` (≈ 57,600 blocks): [5](#0-4) 

```solidity
withdrawalDelayBlocks = 8 days / 12 seconds;
```

Because rsETH is pulled from the user at initiation and held by the contract, the user has no recourse while the delay is extended: [6](#0-5) 

```solidity
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
```

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

A user who initiates a withdrawal when `withdrawalDelayBlocks = 57,600` (8 days) has their rsETH locked in the contract. If the manager immediately raises the delay to `115,200` (16 days), the user's `completeWithdrawal` call will revert for an additional 8 days beyond what was promised at initiation. The `unlockQueue` operator path is equally blocked, so the two-step unlock → complete flow is also stalled. The cap of 16 days prevents indefinite freezing, but the retroactive application to all in-flight requests is the root defect.

---

### Likelihood Explanation

**Medium.** The LRT manager is a privileged but operationally active role (it also controls instant-withdrawal fees, Aave integration, and asset support). A malicious or compromised manager key can silently extend the delay for every pending withdrawal in a single transaction with no on-chain governance check or time-lock. Users have no way to cancel a queued withdrawal and recover their rsETH once it has been transferred in.

---

### Recommendation

Snapshot `withdrawalDelayBlocks` into each `WithdrawalRequest` at initiation time and use that stored value for the delay check, rather than the current global:

```solidity
struct WithdrawalRequest {
    uint256 rsETHUnstaked;
    uint256 expectedAssetAmount;
    uint256 withdrawalStartBlock;
    uint256 withdrawalDelayBlocks; // snapshot at initiation
}
```

Then in `_addUserWithdrawalRequest`:
```solidity
withdrawalRequests[requestId] = WithdrawalRequest({
    ...,
    withdrawalDelayBlocks: withdrawalDelayBlocks
});
```

And in both delay checks:
```solidity
if (block.number < request.withdrawalStartBlock + request.withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();
```

This ensures that changes to `withdrawalDelayBlocks` only affect future requests, not funds already committed.

---

### Proof of Concept

1. Protocol deploys with `withdrawalDelayBlocks = 57,600` (8 days).
2. Alice calls `initiateWithdrawal(ETH, 10e18, "")`. Her 10 rsETH is transferred to `LRTWithdrawalManager`. Her `WithdrawalRequest` records `withdrawalStartBlock = block.number`.
3. The LRT manager calls `setWithdrawalDelayBlocks(115_200)` (16 days), raising the global delay.
4. After 8 days (57,600 blocks), Alice calls `completeWithdrawal`. The check `block.number < withdrawalStartBlock + 115_200` is true → `WithdrawalDelayNotPassed` revert.
5. Alice's rsETH remains locked for an additional 8 days she did not consent to. The operator's `unlockQueue` call also breaks at the same check, so the two-step path is equally blocked.
6. After 16 days total, Alice can finally complete — but only if the manager has not raised the delay again (which they cannot, since 16 days is the cap, and the elapsed block count already exceeds any re-raise).

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L94-94)
```text
        withdrawalDelayBlocks = 8 days / 12 seconds;
```

**File:** contracts/LRTWithdrawalManager.sol (L166-166)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L338-343)
```text
    function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
        // Set an upper limit of no more than 16 days
        if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();

        withdrawalDelayBlocks = withdrawalDelayBlocks_;
        emit WithdrawalDelayBlocksUpdated(withdrawalDelayBlocks);
```

**File:** contracts/LRTWithdrawalManager.sol (L715-715)
```text
        if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();
```

**File:** contracts/LRTWithdrawalManager.sol (L750-753)
```text
        // Create and store the new withdrawal request.
        withdrawalRequests[requestId] = WithdrawalRequest({
            rsETHUnstaked: rsETHUnstaked, expectedAssetAmount: expectedAssetAmount, withdrawalStartBlock: block.number
        });
```

**File:** contracts/LRTWithdrawalManager.sol (L795-795)
```text
            if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;
```
