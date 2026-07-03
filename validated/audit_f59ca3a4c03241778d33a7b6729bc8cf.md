### Title
FIFO Queue `break` in `_unlockWithdrawalRequests` Allows a Large Withdrawal Request to Freeze All Subsequent Users' Funds - (File: `contracts/LRTWithdrawalManager.sol`)

---

### Summary

`LRTWithdrawalManager._unlockWithdrawalRequests` processes withdrawal requests in strict FIFO order using a global per-asset nonce pointer (`nextLockedNonce`). When the assets available in the unstaking vault are insufficient to cover the payout for the request at the current nonce, the function immediately `break`s and leaves `nextLockedNonce` unchanged. All subsequent requests — regardless of their size — remain permanently locked at that pointer until the blocking request can be satisfied. Because rsETH is transferred from users into the contract at `initiateWithdrawal` time and no cancellation mechanism exists, any user whose request sits behind a large blocking request has their funds frozen with no escape path.

---

### Finding Description

`initiateWithdrawal` pulls rsETH from the caller into the contract immediately:

```solidity
// LRTWithdrawalManager.sol line 166
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
```

Each request is appended to the global sequential nonce for that asset and to the user's personal FIFO deque:

```solidity
// lines 756-757
userAssociatedNonces[asset][msg.sender].pushBack(nextUnusedNonce_);
nextUnusedNonce[asset] = nextUnusedNonce_ + 1;
```

The operator-only `unlockQueue` calls `_unlockWithdrawalRequests`, which iterates from `nextLockedNonce[asset]` upward:

```solidity
// lines 790-815
while (nextLockedNonce_ < firstExcludedIndex) {
    ...
    uint256 payoutAmount = _calculatePayoutAmount(request, rsETHPrice, assetPrice);
    if (availableAssetAmount < payoutAmount) break; // ← blocking point
    ...
    unchecked { nextLockedNonce_++; }
}
nextLockedNonce[asset] = nextLockedNonce_;
```

When the request at nonce N cannot be covered, the loop exits and `nextLockedNonce[asset]` is written back at N. Every future call to `unlockQueue` restarts from N. Requests at nonces N+1, N+2, … are never reached.

`_processWithdrawalCompletion` (called by `completeWithdrawal`) enforces that the user's oldest nonce must be strictly less than `nextLockedNonce[asset]`:

```solidity
// line 707
if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();
```

So any user whose personal queue front is at nonce ≥ N is permanently blocked from completing their withdrawal. There is no `cancelWithdrawal`, no refund path, and no operator function that can skip nonce N and advance the pointer past it.

---

### Impact Explanation

**Temporary (and potentially permanent) freezing of user funds — Medium / Critical.**

- rsETH is already in the contract the moment `initiateWithdrawal` succeeds.
- A user whose request is queued behind a large blocking request cannot complete their withdrawal and cannot recover their rsETH.
- In the normal case this is a **temporary freeze** (Medium): once the protocol accumulates enough of the asset to cover the blocking request, the queue can advance.
- In an extreme case — e.g., the protocol suffers significant slashing for that asset type and can never accumulate enough to cover the blocking request — the freeze becomes **permanent** (Critical: permanent freezing of funds).
- No admin escape hatch exists to skip a specific nonce or return rsETH to users.

---

### Likelihood Explanation

**Medium.** The scenario requires only two ordinary users: one who submits a large withdrawal request first, and one (or many) who submit smaller requests afterward. This is a routine ordering that will occur in any active deployment. The operator has no mechanism to prevent it or to remediate it once it occurs without a contract upgrade.

---

### Recommendation

Replace the `break` on insufficient assets with a `continue` (skip) so that smaller requests behind a large one can still be unlocked. Alternatively, introduce a separate "skip" nonce mechanism that allows the operator to advance `nextLockedNonce` past a request that cannot currently be satisfied, combined with a user-facing `cancelWithdrawal` that returns rsETH when a request is skipped. At minimum, add a cancellation path so users are never permanently trapped.

---

### Proof of Concept

1. Deploy `LRTWithdrawalManager` with a supported asset (e.g., ETHx).
2. **User A** calls `initiateWithdrawal(ETHx, 1_000_000e18, "")` — a very large amount. rsETH is transferred to the contract. This request receives nonce 0.
3. **User B** calls `initiateWithdrawal(ETHx, 1e18, "")` — a small amount. rsETH is transferred to the contract. This request receives nonce 1.
4. The unstaking vault holds only 0.5e18 ETHx (less than User A's payout).
5. Operator calls `unlockQueue(ETHx, 2, ...)`. Inside `_unlockWithdrawalRequests`:
   - nonce 0: `payoutAmount` ≈ large; `availableAssetAmount (0.5e18) < payoutAmount` → **`break`**. `nextLockedNonce[ETHx]` stays at 0.
6. **User B** calls `completeWithdrawal(ETHx, "")`. Inside `_processWithdrawalCompletion`:
   - `usersFirstWithdrawalRequestNonce = 1`; `nextLockedNonce[ETHx] = 0`; `1 >= 0` → **`revert WithdrawalLocked()`**.
7. User B's rsETH remains locked in the contract with no recovery path. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L166-166)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L700-707)
```text
        if (userAssociatedNonces[asset][user].empty()) {
            revert NoWithdrawalRequests(user, asset);
        }

        // Retrieve and remove the oldest withdrawal request for the user.
        uint256 usersFirstWithdrawalRequestNonce = userAssociatedNonces[asset][user].popFront();
        // Ensure the request is already unlocked.
        if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();
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

**File:** contracts/LRTWithdrawalManager.sol (L790-815)
```text
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
