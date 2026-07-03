### Title
`setWithdrawalDelayBlocks()` Retroactively Extends Delay on In-Flight Withdrawals, Temporarily Freezing User Funds - (File: contracts/LRTWithdrawalManager.sol)

### Summary
The `setWithdrawalDelayBlocks()` function in `LRTWithdrawalManager.sol` updates the global `withdrawalDelayBlocks` parameter without any guard for already-queued withdrawal requests. Because both the unlock step and the completion step evaluate the delay against the **current** value of `withdrawalDelayBlocks` rather than the value at the time of initiation, a manager increasing the delay after users have already initiated withdrawals retroactively extends the waiting period for those users, temporarily freezing their rsETH inside the contract with no cancellation path.

### Finding Description
When a user calls `initiateWithdrawal()`, their rsETH is transferred to `LRTWithdrawalManager` and a `WithdrawalRequest` is stored with `withdrawalStartBlock = block.number`. The user expects to complete the withdrawal after the current `withdrawalDelayBlocks` have elapsed.

The manager can call `setWithdrawalDelayBlocks()` at any time to change the global delay (up to `16 days / 12 seconds`):

```solidity
// LRTWithdrawalManager.sol
function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
    if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();
    withdrawalDelayBlocks = withdrawalDelayBlocks_;
    emit WithdrawalDelayBlocksUpdated(withdrawalDelayBlocks);
}
```

This change is applied retroactively to all existing requests because both critical paths read the **live** `withdrawalDelayBlocks`:

**Unlock path** (`_unlockWithdrawalRequests()`):
```solidity
if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;
```

**Completion path** (`_processWithdrawalCompletion()`):
```solidity
if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();
```

Neither path snapshots the delay at initiation time. There is no `cancelWithdrawal()` function, so users cannot recover their rsETH once it has been transferred into the contract.

### Impact Explanation
Users who have initiated withdrawals have their rsETH locked inside `LRTWithdrawalManager`. If the delay is increased after initiation, those users cannot unlock or complete their withdrawal until the new (longer) delay elapses from their original `withdrawalStartBlock`. The maximum retroactive extension is from the current default of `8 days / 12 seconds` up to `16 days / 12 seconds` — an additional 8 days of inaccessibility. This constitutes **temporary freezing of funds** (Medium impact).

### Likelihood Explanation
The LRT Manager may legitimately increase the delay in response to a security event or protocol upgrade without realising the change retroactively affects all in-flight requests. Because there is no on-chain check preventing the update while withdrawals are pending, and because the manager role is expected to adjust operational parameters, this scenario can arise from a good-faith administrative action rather than a malicious one. Likelihood is **medium** given the protocol's active withdrawal queue and the plausibility of parameter updates during normal operations.

### Recommendation
Snapshot `withdrawalDelayBlocks` at the time of initiation by storing it inside the `WithdrawalRequest` struct, and use that stored value in both `_unlockWithdrawalRequests()` and `_processWithdrawalCompletion()`. This ensures that new delay values apply only to future requests, mirroring the fix pattern suggested in the reference report (apply the corrective state only going forward, not retroactively).

### Proof of Concept
1. `withdrawalDelayBlocks` is `57,600` (≈ 8 days). User A calls `initiateWithdrawal()` at block `N`; rsETH is locked in `LRTWithdrawalManager`.
2. At block `N + 50,400` (≈ 7 days elapsed, 1 day remaining), the LRT Manager calls `setWithdrawalDelayBlocks(115_200)` (≈ 16 days) — a legitimate security response.
3. The operator attempts `unlockQueue()` for User A's request. The check `block.number < N + 115_200` evaluates to `true` → the loop `break`s; the request is not unlocked.
4. User A calls `completeWithdrawal()`. The check `block.number < N + 115_200` reverts with `WithdrawalDelayNotPassed`.
5. User A's rsETH remains locked for an additional ≈ 9 days beyond their original expectation, with no cancellation path available. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** contracts/LRTWithdrawalManager.sol (L793-796)
```text

            // Check that the withdrawal delay has passed since the request's initiation.
            if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;

```
