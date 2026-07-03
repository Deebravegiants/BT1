### Title
Already-Unlocked Withdrawal Requests Become Unclaimable After `withdrawalDelayBlocks` Increase - (File: contracts/LRTWithdrawalManager.sol)

### Summary
`LRTWithdrawalManager` enforces the `withdrawalDelayBlocks` check at two independent points in the withdrawal lifecycle. The unlock stage validates the delay before marking a request as unlocked, and the claim stage re-validates the delay using the **current** (potentially updated) `withdrawalDelayBlocks` value. If the manager legitimately increases `withdrawalDelayBlocks` after requests have already been unlocked, those requests become temporarily unclaimable — users cannot retrieve their funds even though the protocol has already confirmed their withdrawal is ready.

### Finding Description
The withdrawal lifecycle has two distinct stages:

**Stage 1 — Unlock** (`_unlockWithdrawalRequests`, called from `unlockQueue`):

```solidity
// Check that the withdrawal delay has passed since the request's initiation.
if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;
...
unlockedWithdrawalsCount[asset]++;
nextLockedNonce_++;
```

A request is only unlocked if `block.number >= request.withdrawalStartBlock + withdrawalDelayBlocks` at the time `unlockQueue` is called. Once unlocked, `nextLockedNonce[asset]` is advanced past the request.

**Stage 2 — Claim** (`_processWithdrawalCompletion`, called from `completeWithdrawal`):

```solidity
// Ensure the request is already unlocked.
if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();
...
// Check that the withdrawal delay has passed since the request's initiation.
if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();
```

The claim stage first checks the "unlocked" status (primary condition), then re-checks the delay (secondary condition) using the **live** `withdrawalDelayBlocks` storage variable — not the value that was in effect when the request was unlocked.

The manager can update `withdrawalDelayBlocks` at any time via `setWithdrawalDelayBlocks`, up to a maximum of `16 days / 12 seconds` (115,200 blocks):

```solidity
function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
    if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();
    withdrawalDelayBlocks = withdrawalDelayBlocks_;
    ...
}
```

If the manager increases `withdrawalDelayBlocks` from `D` to `D'` (where `D' > D`) after requests have been unlocked at block `B + D`, those requests satisfy the primary condition (`nonce < nextLockedNonce`) but fail the secondary condition (`block.number < B + D'`). The revert rolls back the `popFront` and `delete`, so the request is not lost — but the user is blocked from claiming until block `B + D'`.

This is structurally identical to the reported vulnerability: a function callable when a primary status condition is met is blocked by a secondary check that can independently fail, even though the primary condition was set precisely because the secondary check had already been validated.

### Impact Explanation
Users with already-unlocked withdrawal requests cannot call `completeWithdrawal` successfully. Their rsETH has already been burned (at `unlockQueue` time), and the underlying assets are held in the contract. The funds are temporarily frozen — inaccessible until enough blocks pass to satisfy the new, higher delay. With the maximum delay of 16 days, this freeze can last up to 16 days beyond the original unlock point.

**Impact: Temporary freezing of funds (Medium).**

### Likelihood Explanation
The manager may legitimately increase `withdrawalDelayBlocks` in response to a security incident, a protocol upgrade, or a change in EigenLayer's unbonding period. This is a normal operational action. The manager has no reason to expect that increasing the delay retroactively affects already-unlocked requests, since the unlock process already validated the delay. The action is not malicious — it is a design flaw where a legitimate configuration change has unintended consequences for in-flight withdrawals.

**Likelihood: Low-Medium** (requires a manager delay increase, which is a plausible operational event).

### Recommendation
Remove the redundant delay check from `_processWithdrawalCompletion`. The `_unlockWithdrawalRequests` function already enforces the delay before advancing `nextLockedNonce`. Once a request is unlocked (i.e., its nonce is below `nextLockedNonce`), the delay has been validated and should not be re-evaluated at claim time. Alternatively, snapshot the `withdrawalDelayBlocks` value into the `WithdrawalRequest` struct at unlock time and use that snapshot in `_processWithdrawalCompletion`.

### Proof of Concept
1. Current `withdrawalDelayBlocks = D` (e.g., 57,600 blocks ≈ 8 days).
2. User calls `initiateWithdrawal(asset, rsETHAmount)` at block `B`. `withdrawalStartBlock = B`.
3. Operator calls `unlockQueue(asset, ...)` at block `B + D`. Inside `_unlockWithdrawalRequests`, the check `block.number >= B + D` passes; the request is unlocked and `nextLockedNonce[asset]` is advanced.
4. Manager calls `setWithdrawalDelayBlocks(D')` where `D' = 115_200` (16 days). This is a legitimate security response.
5. User calls `completeWithdrawal(asset)` at block `B + D`:
   - **Check 1** (`usersFirstWithdrawalRequestNonce < nextLockedNonce[asset]`): **PASSES** — request was unlocked in step 3.
   - **Check 2** (`block.number < request.withdrawalStartBlock + withdrawalDelayBlocks`): evaluates as `B + D < B + D'` → **REVERTS** with `WithdrawalDelayNotPassed`.
6. User's funds are frozen until block `B + D'`. The user must wait an additional `D' - D` blocks (up to 8 extra days) despite the protocol having already confirmed the withdrawal as ready. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L338-343)
```text
    function setWithdrawalDelayBlocks(uint256 withdrawalDelayBlocks_) external onlyLRTManager {
        // Set an upper limit of no more than 16 days
        if (withdrawalDelayBlocks_ > 16 days / 12 seconds) revert ExceedWithdrawalDelay();

        withdrawalDelayBlocks = withdrawalDelayBlocks_;
        emit WithdrawalDelayBlocksUpdated(withdrawalDelayBlocks);
```

**File:** contracts/LRTWithdrawalManager.sol (L705-715)
```text
        uint256 usersFirstWithdrawalRequestNonce = userAssociatedNonces[asset][user].popFront();
        // Ensure the request is already unlocked.
        if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();

        bytes32 requestId = getRequestId(asset, usersFirstWithdrawalRequestNonce);
        WithdrawalRequest memory request = withdrawalRequests[requestId];

        delete withdrawalRequests[requestId];

        // Check that the withdrawal delay has passed since the request's initiation.
        if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();
```

**File:** contracts/LRTWithdrawalManager.sol (L790-795)
```text
        while (nextLockedNonce_ < firstExcludedIndex) {
            bytes32 requestId = getRequestId(asset, nextLockedNonce_);
            WithdrawalRequest storage request = withdrawalRequests[requestId];

            // Check that the withdrawal delay has passed since the request's initiation.
            if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;
```
