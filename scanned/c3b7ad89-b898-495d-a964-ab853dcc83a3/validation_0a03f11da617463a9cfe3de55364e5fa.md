### Title
Manager Can Re-Lock Already-Unlocked Withdrawal Requests by Increasing `withdrawalDelayBlocks` — (`contracts/LRTWithdrawalManager.sol`)

---

### Summary

`setWithdrawalDelayBlocks` applies the new delay value globally and retroactively. Because `_processWithdrawalCompletion` reads the **current** `withdrawalDelayBlocks` at claim time rather than the value that was in effect when the request was created or unlocked, the manager can increase the delay after requests have already passed the original window and been marked as unlocked — temporarily freezing user withdrawals that the protocol had already guaranteed were claimable.

---

### Finding Description

The withdrawal lifecycle in `LRTWithdrawalManager` has two distinct "finalization" gates:

1. **Operator unlock gate** (`unlockQueue`): The operator calls `unlockQueue`, which advances `nextLockedNonce[asset]` past requests whose `withdrawalStartBlock + withdrawalDelayBlocks <= block.number`. This increments `unlockedWithdrawalsCount[asset]` and sets the final payout amount.

2. **User claim gate** (`_processWithdrawalCompletion`): When the user calls `completeWithdrawal`, the code first checks that the request nonce is below `nextLockedNonce` (i.e., it was unlocked), then re-checks the block delay using the **current** `withdrawalDelayBlocks`:

```solidity
// line 707 — checks operator-unlock gate
if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();
...
// line 715 — re-checks delay using CURRENT global value
if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();
```

`setWithdrawalDelayBlocks` has no guard preventing it from retroactively affecting already-unlocked requests:

```solidity
function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
    if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();
    withdrawalDelayBlocks = withdrawalDelayBlocks_;   // ← no retroactive-effect check
    emit WithdrawalDelayBlocksUpdated(withdrawalDelayBlocks);
}
```

Because the delay stored in each `WithdrawalRequest` struct is only `withdrawalStartBlock` (not the delay value at creation time), every future call to `_processWithdrawalCompletion` evaluates `request.withdrawalStartBlock + withdrawalDelayBlocks` against the new, larger global value. Requests that had already cleared the original 8-day window and been formally unlocked by the operator are silently re-locked.

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

Users whose withdrawal requests have already been unlocked by the operator (i.e., `nextLockedNonce` has advanced past their nonce and `unlockedWithdrawalsCount` was incremented) are unable to call `completeWithdrawal` until `block.number` catches up to `withdrawalStartBlock + new_withdrawalDelayBlocks`. The manager can extend the delay up to the 16-day cap, imposing up to 8 additional days of freeze on top of the original 8-day window. The user's rsETH has already been transferred to the contract at `initiateWithdrawal` time, so the funds are locked in the contract for the extended period.

---

### Likelihood Explanation

**Low-Medium.** The `MANAGER` role is a live operational key used for routine parameter updates. A manager acting in good faith to tighten security (e.g., responding to a market event by extending the delay) would inadvertently re-lock all already-unlocked requests without any protocol warning. No malicious intent is required; the missing retroactive-effect guard makes this a latent operational hazard.

---

### Recommendation

Store the effective delay at request-creation time inside `WithdrawalRequest` and use that snapshot in both `_unlockWithdrawalRequests` and `_processWithdrawalCompletion`:

```solidity
struct WithdrawalRequest {
    uint256 rsETHUnstaked;
    uint256 expectedAssetAmount;
    uint256 withdrawalStartBlock;
    uint256 withdrawalDelayBlocksSnapshot; // ← add this
}
```

Populate it in `_addUserWithdrawalRequest`:
```solidity
withdrawalDelayBlocksSnapshot: withdrawalDelayBlocks
```

Then replace the global read in `_processWithdrawalCompletion`:
```solidity
if (block.number < request.withdrawalStartBlock + request.withdrawalDelayBlocksSnapshot)
    revert WithdrawalDelayNotPassed();
```

Alternatively, add a guard in `setWithdrawalDelayBlocks` that only allows increases for requests whose `withdrawalStartBlock` is in the future (i.e., not yet queued), though the snapshot approach is cleaner.

---

### Proof of Concept

1. User calls `initiateWithdrawal(ETH, amount)` at block **B**. `withdrawalDelayBlocks` = 57,600 (~8 days). rsETH is transferred to the contract.

2. At block **B + 57,600** the delay has passed. The operator calls `unlockQueue(ETH, ...)`. Inside `_unlockWithdrawalRequests`, line 795 passes (`block.number >= B + 57,600`), `nextLockedNonce[ETH]` advances past the user's nonce, `unlockedWithdrawalsCount[ETH]++`, and the payout amount is finalized. [1](#0-0) 

3. Manager calls `setWithdrawalDelayBlocks(115_200)` (16-day max). No check prevents this from affecting already-unlocked requests. [2](#0-1) 

4. User calls `completeWithdrawal(ETH, ...)`. Inside `_processWithdrawalCompletion`:
   - Line 707 passes (nonce < `nextLockedNonce` — request was unlocked in step 2).
   - Line 715 **reverts**: `block.number (B + 57,600) < B + 115,200`. [3](#0-2) 

5. The user's ETH remains locked in `LRTWithdrawalManager` for up to 8 additional days (until block B + 115,200), despite the protocol having already formally unlocked the request and guaranteed the payout amount.

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

**File:** contracts/LRTWithdrawalManager.sol (L707-715)
```text
        if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();

        bytes32 requestId = getRequestId(asset, usersFirstWithdrawalRequestNonce);
        WithdrawalRequest memory request = withdrawalRequests[requestId];

        delete withdrawalRequests[requestId];

        // Check that the withdrawal delay has passed since the request's initiation.
        if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();
```

**File:** contracts/LRTWithdrawalManager.sol (L794-795)
```text
            // Check that the withdrawal delay has passed since the request's initiation.
            if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;
```
