### Title
Strict FIFO Queue in `_unlockWithdrawalRequests` Allows a Large Head-of-Queue Request to Block All Subsequent Smaller Withdrawal Requests - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`LRTWithdrawalManager._unlockWithdrawalRequests` processes withdrawal requests in strict FIFO order. When the head-of-queue request requires more assets than are currently available in the unstaking vault, the loop immediately `break`s, permanently blocking all subsequent requests — including those that could be fully satisfied with the available balance. This is a direct structural analog to Perennial M-11, where a pending "requested" oracle version blocked all "non-requested" commits.

---

### Finding Description

`unlockQueue` calls `_unlockWithdrawalRequests`, which iterates from `nextLockedNonce[asset]` upward:

```solidity
// contracts/LRTWithdrawalManager.sol lines 790–815
while (nextLockedNonce_ < firstExcludedIndex) {
    bytes32 requestId = getRequestId(asset, nextLockedNonce_);
    WithdrawalRequest storage request = withdrawalRequests[requestId];

    if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;

    uint256 payoutAmount = _calculatePayoutAmount(request, rsETHPrice, assetPrice);

    if (availableAssetAmount < payoutAmount) break; // <-- hard stop for ALL subsequent requests

    ...
    nextLockedNonce_++;
}
nextLockedNonce[asset] = nextLockedNonce_;
``` [1](#0-0) 

The `break` at line 800 exits the entire loop and writes the unchanged `nextLockedNonce_` back to storage. There is no mechanism to skip the blocking request and process smaller ones behind it. The operator-supplied `firstExcludedIndex` only sets the upper bound of the range; it cannot skip the head. [2](#0-1) 

The available asset amount passed to the loop comes from `unstakingVault.balanceOf(asset)` — the balance of assets that have already been unstaked from EigenLayer and are sitting in the vault: [3](#0-2) 

Meanwhile, `initiateWithdrawal` allows users to queue requests as long as `expectedAssetAmount <= getAvailableAssetAmount(asset)`, which is computed against total protocol deposits (including assets still delegated in EigenLayer), not the vault's liquid balance: [4](#0-3) 

This creates a gap: a user can legitimately queue a large withdrawal (e.g., 1 000 ETH) when total deposits are high, but the vault may only hold 500 ETH of liquid assets at any given time. When `unlockQueue` is called, the 1 000 ETH request sits at the head and the loop breaks immediately, freezing every smaller request queued behind it — even requests for 1 ETH that could be trivially satisfied.

---

### Impact Explanation

Users whose withdrawal requests are queued behind a large head-of-queue request cannot complete their withdrawals until the vault accumulates enough assets to satisfy the blocking request. Because EigenLayer unstaking has a multi-day delay and the vault fills incrementally, this freeze can persist for an extended period. The affected users' rsETH has already been transferred to the contract at `initiateWithdrawal` time, so their funds are locked with no recourse.

**Impact: Medium — Temporary freezing of funds.** [5](#0-4) 

---

### Likelihood Explanation

Any unprivileged rsETH holder can call `initiateWithdrawal` with a large amount. Because the availability check at initiation time uses total protocol deposits (not the vault's liquid balance), a large request can always be queued when the protocol has significant TVL. The vault's liquid balance is routinely lower than total deposits because most assets remain staked in EigenLayer. This scenario is therefore a normal operating condition, not an edge case.

---

### Recommendation

Replace the hard `break` on insufficient assets with a `continue` (skip the current request and attempt the next one), or introduce a separate "skip-and-requeue" path that allows the operator to advance `nextLockedNonce` past a request that cannot currently be fulfilled, without permanently blocking it. Alternatively, process requests in order of size or allow out-of-order unlocking when the head request is provably under-funded.

---

### Proof of Concept

1. Protocol has 2 000 ETH total deposits; unstaking vault holds 500 ETH liquid.
2. **Alice** calls `initiateWithdrawal(ETH, rsETH_for_1000_ETH)`. Check passes (`1000 < 2000 - 0`). Nonce 0 assigned. `assetsCommitted[ETH] = 1000`.
3. **Bob** calls `initiateWithdrawal(ETH, rsETH_for_1_ETH)`. Check passes (`1 < 2000 - 1000`). Nonce 1 assigned. `assetsCommitted[ETH] = 1001`.
4. Operator calls `unlockQueue(ETH, 2, ...)`. `_createUnlockParams` returns `totalAvailableAssets = 500`.
5. Loop iteration for nonce 0: `payoutAmount ≈ 1000 ETH`, `500 < 1000` → **`break`**. `nextLockedNonce[ETH]` stays at 0.
6. Bob's nonce-1 request is never evaluated. Bob cannot call `completeWithdrawal` because `usersFirstWithdrawalRequestNonce (1) >= nextLockedNonce[ETH] (0)` — wait, actually `1 >= 0` is true, so `revert WithdrawalLocked()`. [6](#0-5) 

Bob's 1 ETH is frozen until the vault accumulates ≥ 1 000 ETH to unblock Alice's request first.

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L162-176)
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

**File:** contracts/LRTWithdrawalManager.sol (L599-603)
```text
    function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L704-707)
```text
        // Retrieve and remove the oldest withdrawal request for the user.
        uint256 usersFirstWithdrawalRequestNonce = userAssociatedNonces[asset][user].popFront();
        // Ensure the request is already unlocked.
        if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();
```

**File:** contracts/LRTWithdrawalManager.sol (L786-815)
```text
        uint256 nextLockedNonce_ = nextLockedNonce[asset];
        // Revert when trying to unlock a request that has already been unlocked
        if (nextLockedNonce_ >= firstExcludedIndex) revert NoPendingWithdrawals();

        while (nextLockedNonce_ < firstExcludedIndex) {
            bytes32 requestId = getRequestId(asset, nextLockedNonce_);
            WithdrawalRequest storage request = withdrawalRequests[requestId];

            // Check that the withdrawal delay has passed since the request's initiation.
            if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;

            // Calculate the amount user will receive
            uint256 payoutAmount = _calculatePayoutAmount(request, rsETHPrice, assetPrice);

            if (availableAssetAmount < payoutAmount) break; // Exit if not enough assets to cover this request

            assetsCommitted[asset] -= request.expectedAssetAmount;
            // Set the amount the user will receive
            request.expectedAssetAmount = payoutAmount;
            rsETHAmountToBurn += request.rsETHUnstaked;
            availableAssetAmount -= payoutAmount;
            assetAmountToUnlock += payoutAmount;

            unlockedWithdrawalsCount[asset]++;

            unchecked {
                nextLockedNonce_++;
            }
        }
        nextLockedNonce[asset] = nextLockedNonce_;
```

**File:** contracts/LRTWithdrawalManager.sol (L837-851)
```text
    function _createUnlockParams(
        ILRTOracle lrtOracle,
        ILRTUnstakingVault unstakingVault,
        address asset
    )
        internal
        view
        returns (UnlockParams memory)
    {
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
    }
```
