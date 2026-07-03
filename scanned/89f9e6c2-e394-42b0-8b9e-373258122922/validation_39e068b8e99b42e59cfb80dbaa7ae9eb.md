### Title
`setWithdrawalDelayBlocks` Retroactively Extends Delay on All Pending Withdrawals, Causing Temporary Fund Freeze - (`contracts/LRTWithdrawalManager.sol`)

### Summary
The `withdrawalDelayBlocks` parameter in `LRTWithdrawalManager` is applied at **completion time** rather than at **initiation time**. A manager calling `setWithdrawalDelayBlocks` to increase the delay retroactively extends the lock period for every already-queued and already-unlocked withdrawal request, temporarily freezing user funds beyond the delay they accepted when initiating.

### Finding Description
When a user calls `initiateWithdrawal`, the request is stored with `withdrawalStartBlock = block.number`. No snapshot of the current `withdrawalDelayBlocks` is taken.

Both gating checks read the **live** `withdrawalDelayBlocks` storage variable at execution time:

In `_unlockWithdrawalRequests` (called by `unlockQueue`): [1](#0-0) 

In `_processWithdrawalCompletion` (called by `completeWithdrawal`): [2](#0-1) 

The manager can raise the delay up to the hard cap of 16 days: [3](#0-2) 

The default delay is 8 days: [4](#0-3) 

A user who initiated a withdrawal under the 8-day delay can have their wait silently doubled to 16 days by a single manager call, with no recourse. Crucially, the user has already transferred their rsETH into the contract at `initiateWithdrawal`: [5](#0-4) 

The rsETH is held by the contract and cannot be reclaimed — the user is locked in.

### Impact Explanation
**Medium — Temporary freezing of funds.** Users who have already surrendered their rsETH to the contract and are waiting for the delay to expire can have their withdrawal window extended by up to 8 additional days (from 8 to 16 days) without consent. The funds are not permanently lost, but they are inaccessible for the extended period. This applies to all pending requests in the queue simultaneously, including requests that have already been processed by `unlockQueue` and are waiting only for the block-delay check in `completeWithdrawal`.

### Likelihood Explanation
The `onlyLRTManager` role is an operational role expected to perform routine parameter updates. A legitimate security-motivated delay extension (e.g., during an incident response) would inadvertently freeze all in-flight withdrawals. No key compromise or collusion is required — a single manager transaction is sufficient. The analog in the external report (PoC 3: admin changes protocol fee mid-draw) follows the same pattern of a routine parameter update retroactively affecting in-flight user operations.

### Recommendation
Snapshot `withdrawalDelayBlocks` into each `WithdrawalRequest` struct at the time `initiateWithdrawal` is called, and use the stored per-request delay in both `_unlockWithdrawalRequests` and `_processWithdrawalCompletion`. New requests would use the updated delay; existing requests would honour the delay in effect when they were created.

```solidity
struct WithdrawalRequest {
    uint256 rsETHUnstaked;
    uint256 expectedAssetAmount;
    uint256 withdrawalStartBlock;
    uint256 withdrawalDelayBlocksSnapshot; // add this
}
```

Then replace:
```solidity
if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) ...
```
with:
```solidity
if (block.number < request.withdrawalStartBlock + request.withdrawalDelayBlocksSnapshot) ...
```

### Proof of Concept

1. Manager sets `withdrawalDelayBlocks = 57,600` (8 days at 12 s/block).
2. Alice calls `initiateWithdrawal(asset, rsETHAmount, "")`. Her rsETH is transferred to the contract; `withdrawalStartBlock = N` is stored.
3. Alice waits 8 days (block `N + 57,600`). She is now eligible to complete.
4. Before Alice calls `completeWithdrawal`, the manager calls `setWithdrawalDelayBlocks(115_200)` (16 days).
5. Alice calls `completeWithdrawal`. The check `block.number < N + 115_200` is true → `WithdrawalDelayNotPassed` revert.
6. Alice must wait an additional 8 days she never agreed to, with her rsETH locked in the contract and no way to cancel. [3](#0-2) [2](#0-1) [6](#0-5)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L94-94)
```text
        withdrawalDelayBlocks = 8 days / 12 seconds;
```

**File:** contracts/LRTWithdrawalManager.sol (L162-175)
```text
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L338-343)
```text
    function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
        // Set an upper limit of no more than 16 days
        if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();

        withdrawalDelayBlocks = withdrawalDelayBlocks_;
        emit WithdrawalDelayBlocksUpdated(withdrawalDelayBlocks);
```

**File:** contracts/LRTWithdrawalManager.sol (L714-715)
```text
        // Check that the withdrawal delay has passed since the request's initiation.
        if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();
```

**File:** contracts/LRTWithdrawalManager.sol (L794-795)
```text
            // Check that the withdrawal delay has passed since the request's initiation.
            if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;
```
