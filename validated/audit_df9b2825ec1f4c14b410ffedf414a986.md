Audit Report

## Title
Unbounded Withdrawal Queue Enables Griefing of `unlockQueue` Gas and Temporary Freezing of Legitimate Withdrawals - (File: `contracts/LRTWithdrawalManager.sol`)

## Summary
`initiateWithdrawal` accepts requests down to 1 wei of rsETH because `minRsEthAmountToWithdraw` is a mapping that defaults to zero and is never set in `initialize`. An attacker holding rsETH can flood the global FIFO queue with arbitrarily many dust requests ahead of legitimate users. Because `_unlockWithdrawalRequests` uses `break` (not `continue`) on both the delay check and the insufficient-assets check, every attacker entry must be fully processed before any later legitimate request can be unlocked, causing unbounded operator gas consumption and temporary freezing of legitimate users' withdrawals.

## Finding Description
`minRsEthAmountToWithdraw` is declared as a plain mapping at line 35 and is never written in `initialize` (lines 90–98), so it defaults to zero for every asset. The only way to set it is via the admin-only `setMinRsEthAmountToWithdraw` (line 330).

`initiateWithdrawal` (line 162) only rejects `rsETHUnstaked == 0`; with the default minimum of zero, any positive amount—including 1 wei—is accepted. Each accepted request is appended to the global nonce counter with no per-user cap (lines 755–757).

`_unlockWithdrawalRequests` (lines 790–815) iterates from `nextLockedNonce` to `firstExcludedIndex` in strict FIFO order. Both exit conditions use `break`:
- Line 795: `if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) break;`
- Line 800: `if (availableAssetAmount < payoutAmount) break;`

Neither skips an entry; both halt the entire loop. Therefore, N attacker entries at the front of the queue must each be read from storage and written before the pointer advances past them to reach any legitimate request.

With 1 ETH of rsETH and 1-wei requests, an attacker can enqueue up to ~10¹⁸ entries. After the 8-day delay their rsETH is returned via `completeWithdrawal`, allowing the attack to be repeated indefinitely.

## Impact Explanation
**Medium – Unbounded gas consumption:** The operator must spend O(N) gas across one or more `unlockQueue` batches to advance `nextLockedNonce` past all attacker entries. With `minRsEthAmountToWithdraw == 0` and 1-wei requests, N is bounded only by total protocol assets in wei, making the gas cost effectively unbounded. This matches the allowed impact "Medium. Unbounded gas consumption."

**Medium – Temporary freezing of funds:** Legitimate users whose requests are queued after the attacker's cannot have their withdrawals unlocked until the operator has processed all preceding attacker entries. The attacker can sustain the delay by re-submitting after each 8-day cycle, continuously pushing legitimate requests further back. This matches the allowed impact "Medium. Temporary freezing of funds."

## Likelihood Explanation
- `minRsEthAmountToWithdraw` defaults to zero and requires explicit admin action to set; many deployments may leave it unset.
- Any rsETH holder can call `initiateWithdrawal`; no special role is required.
- With 1 ETH of rsETH and 1-wei requests, ~10¹⁸ queue entries are possible. Even at a realistic minimum (e.g., 0.001 ETH), 1 ETH of rsETH yields 1,000 entries per cycle.
- The attacker's only costs are gas and the 8-day opportunity cost; rsETH principal is fully returned.
- The attack is repeatable every 8 days with the same capital.

## Recommendation
1. **Enforce a non-zero minimum at initialization:** In `initialize`, set `minRsEthAmountToWithdraw` to a meaningful floor for each supported asset, or require it to be set before an asset is usable for withdrawals.
2. **Add a per-user pending-request cap:** In `_addUserWithdrawalRequest`, add `require(userAssociatedNonces[asset][msg.sender].length() < MAX_PENDING_PER_USER)` to bound the number of simultaneous pending requests per address.
3. **Consider `continue` instead of `break` for the delay condition:** If a request's delay has not elapsed, skipping it (rather than halting the loop) would allow later, already-matured requests to be processed, reducing the impact of queue flooding.

## Proof of Concept
```solidity
// Precondition: minRsEthAmountToWithdraw[asset] == 0 (default)
// Attacker holds N wei of rsETH

for (uint i = 0; i < N; i++) {
    // Each call locks 1 wei rsETH, commits ~1 wei of asset
    lrtWithdrawalManager.initiateWithdrawal(asset, 1, "");
}

// Legitimate user submits their request — now at global nonce position N
lrtWithdrawalManager.initiateWithdrawal(asset, 1 ether, ""); // victim

// After 8-day delay, operator must call unlockQueue ceil(N / batchSize) times,
// each time paying gas proportional to batchSize, before nextLockedNonce
// reaches position N and the victim's request can be unlocked.
// Attacker then calls completeWithdrawal to recover rsETH and repeats.
```

The attack is permissionless, repeatable, and essentially free beyond gas costs when `minRsEthAmountToWithdraw == 0`.