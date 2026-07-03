### Title
Immediate `withdrawalDelayBlocks` Increase Retroactively Freezes Pending Withdrawal Requests — (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager.setWithdrawalDelayBlocks()` allows the LRT Manager to update the global withdrawal delay with immediate effect and no grace period. Because both `_unlockWithdrawalRequests` and `_processWithdrawalCompletion` read the live `withdrawalDelayBlocks` value at call time rather than the value that was in effect when a request was created, any increase retroactively extends the lock period for every already-queued withdrawal. Users cannot cancel queued requests (no `cancelWithdrawal` exists), so their rsETH and expected asset amount are frozen for longer than they agreed to when initiating the withdrawal.

---

### Finding Description

`setWithdrawalDelayBlocks` writes the new delay directly to storage with no snapshot or grace period:

```solidity
// LRTWithdrawalManager.sol line 338-343
function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
    if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();
    withdrawalDelayBlocks = withdrawalDelayBlocks_;
    emit WithdrawalDelayBlocksUpdated(withdrawalDelayBlocks);
}
```

Both downstream enforcement points read the current global value, not a per-request snapshot:

**`_unlockWithdrawalRequests` (line 795)** — called by the operator-gated `unlockQueue`:
```solidity
if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;
```

**`_processWithdrawalCompletion` (line 715)** — called by the public `completeWithdrawal`:
```solidity
if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();
```

The `WithdrawalRequest` struct stores only `withdrawalStartBlock`, `rsETHUnstaked`, and `expectedAssetAmount` — no delay snapshot. There is no `cancelWithdrawal` function anywhere in the contract (confirmed by search). Once `initiateWithdrawal` is called, the user's rsETH is transferred to the contract and the user has no exit path.

The protocol's own NatSpec on `instantWithdrawal` (line 210–211) acknowledges the analogous fee-at-execution-time pattern, confirming the developers are aware that live-read parameters affect in-flight users.

---

### Impact Explanation

A user who queued a withdrawal when `withdrawalDelayBlocks` was `57,600` (8 days at 12 s/block) and is one block away from eligibility can have their completion blocked for up to an additional 8 days if the manager raises the delay to the maximum `115,200` blocks (16 days). The user's rsETH is already held by the contract and cannot be reclaimed. This is a **temporary freeze of user funds**.

**Impact: Medium — Temporary freezing of funds.**

---

### Likelihood Explanation

The LRT Manager is an operationally active role that legitimately adjusts protocol parameters. Increasing the withdrawal delay is a plausible response to a security incident or EigenLayer queue changes. No malicious intent is required — a routine, well-intentioned parameter update silently harms all users with in-flight requests. The function has no on-chain constraint preventing retroactive application.

**Likelihood: Medium.**

---

### Recommendation

Snapshot the active delay at request creation time and store it in the `WithdrawalRequest` struct:

```solidity
struct WithdrawalRequest {
    uint256 rsETHUnstaked;
    uint256 expectedAssetAmount;
    uint256 withdrawalStartBlock;
    uint256 withdrawalDelayBlocksSnapshot; // add this
}
```

Replace both live-read checks with the per-request snapshot:

```solidity
// _unlockWithdrawalRequests
if (block.number < request.withdrawalStartBlock + request.withdrawalDelayBlocksSnapshot) break;

// _processWithdrawalCompletion
if (block.number < request.withdrawalStartBlock + request.withdrawalDelayBlocksSnapshot) revert WithdrawalDelayNotPassed();
```

This guarantees users are only subject to the delay that was in effect when they initiated their withdrawal, mirroring the principle that parameter changes should not retroactively harm existing positions.

---

### Proof of Concept

1. `withdrawalDelayBlocks` is initialized to `57,600` blocks (8 days / 12 s).
2. Alice calls `initiateWithdrawal(stETH, amount, "")` at block `N`. Her rsETH is transferred to the contract. `WithdrawalRequest.withdrawalStartBlock = N`.
3. At block `N + 57,599` (one block before Alice is eligible), the LRT Manager calls `setWithdrawalDelayBlocks(115_200)`.
4. Alice calls `completeWithdrawal(stETH, "")`. `_processWithdrawalCompletion` evaluates: `block.number (N+57,599) < N + 115,200` → `true` → `revert WithdrawalDelayNotPassed()`.
5. Alice has no `cancelWithdrawal` path. Her rsETH and committed stETH remain locked in the contract for an additional ~8 days she never agreed to. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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

**File:** contracts/LRTWithdrawalManager.sol (L209-212)
```text
    /// @param referralId The referral identifier for tracking
    /// @dev Uses the fee set at execution time. Managers can raise it right before this call, making withdrawals cost
    /// more than expected.
    function instantWithdrawal(
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

**File:** contracts/LRTWithdrawalManager.sol (L713-716)
```text

        // Check that the withdrawal delay has passed since the request's initiation.
        if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();

```

**File:** contracts/LRTWithdrawalManager.sol (L793-796)
```text

            // Check that the withdrawal delay has passed since the request's initiation.
            if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;

```

**File:** contracts/interfaces/ILRTWithdrawalManager.sol (L39-43)
```text
    struct WithdrawalRequest {
        uint256 rsETHUnstaked;
        uint256 expectedAssetAmount;
        uint256 withdrawalStartBlock;
    }
```
