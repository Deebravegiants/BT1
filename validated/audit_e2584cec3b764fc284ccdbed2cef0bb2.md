Audit Report

## Title
ETH Permanently Frozen in `LRTWithdrawalManager` When Withdrawing User Contract Lacks `receive()` - (File: `contracts/LRTWithdrawalManager.sol`)

## Summary
The ETH withdrawal lifecycle in `LRTWithdrawalManager` is split across two separate transactions. In the first (`unlockQueue`), rsETH is irreversibly burned and ETH is pulled into the contract. In the second (`completeWithdrawal`/`completeWithdrawalForUser`), ETH is pushed to the user via a raw `.call`. If the user is a non-upgradeable contract without a `receive()` or payable fallback, the push always reverts, the ETH remains in `LRTWithdrawalManager` with no recovery path, and the user's rsETH is permanently gone.

## Finding Description
**Step 1 — `unlockQueue` (separate transaction):** `_unlockWithdrawalRequests` increments `unlockedWithdrawalsCount[asset]` and sets `request.expectedAssetAmount`. Then rsETH is burned (`burnFrom`) and ETH is pulled from `LRTUnstakingVault` (`unstakingVault.redeem`). These are irreversible once the transaction is mined.

**Step 2 — `completeWithdrawal` / `completeWithdrawalForUser`:** Both call `_processWithdrawalCompletion(asset, user, ...)`. Inside, the function calls `_transferAsset(asset, user, request.expectedAssetAmount)`, which for ETH executes:

```solidity
// LRTWithdrawalManager.sol L878-879
(bool sent,) = payable(to).call{ value: amount }("");
if (!sent) revert EthTransferFailed();
```

If `to` is a contract without `receive()`, `sent == false` and the entire `_processWithdrawalCompletion` reverts. The revert rolls back `popFront()` (L705), `delete withdrawalRequests[requestId]` (L712), and `unlockedWithdrawalsCount[asset]--` (L717), leaving the request intact and `unlockedWithdrawalsCount[asset] > 0`.

**No redirect path exists:** `completeWithdrawal` hardcodes `msg.sender` as the recipient (L184), and `completeWithdrawalForUser` hardcodes the `user` parameter (L202) — neither allows specifying an alternate recipient.

**Sweep path is permanently blocked:** `sweepRemainingAssets` checks `hasUnlockedWithdrawals(asset)` (L403), which returns `true` while `unlockedWithdrawalsCount[asset] > 0` (L630). Because the stuck request keeps this count positive, the sweep can never execute.

The NatDoc on `completeWithdrawalForUser` (L191) acknowledges ETH transfer issues ("Not expected to be used for ETH; potential gas grief scenarios are non-impactful for ETH") but provides no recovery mechanism.

## Impact Explanation
**Critical — Permanent freezing of funds.** The user's rsETH is burned in a prior, non-revertible transaction. The corresponding ETH sits in `LRTWithdrawalManager` indefinitely. There is no admin function, no cancel path, and no redirect mechanism. The user suffers a total, unrecoverable loss of their withdrawal value.

## Likelihood Explanation
**Low-Medium.** The affected user must be a non-upgradeable contract without a `receive()` or payable fallback. Realistic cases include: Safe multisigs not configured to accept ETH, protocol-level aggregators or vaults that call `initiateWithdrawal` on behalf of users, and any contract integrator not designed to receive raw ETH. The existence of `completeWithdrawalForUser` (an operator-driven path) explicitly anticipates non-EOA callers, making this scenario plausible in production.

## Recommendation
Replace the push-payment pattern for ETH with a **pull-payment pattern**: record the claimable ETH amount in a per-user mapping inside `_processWithdrawalCompletion` instead of transferring immediately, and add a separate `claimETH(address recipient)` function that lets the user (or a user-specified address) pull the funds. Alternatively, allow `completeWithdrawal` and `completeWithdrawalForUser` to accept an explicit `recipient` address parameter so ETH can be redirected to an EOA the user controls.

## Proof of Concept
1. Deploy `NoReceive` — a contract with no `receive()` or payable fallback that holds rsETH.
2. `NoReceive` approves and calls `LRTWithdrawalManager.initiateWithdrawal(ETH_TOKEN, rsETHAmount, "")`. rsETH is transferred to `LRTWithdrawalManager`; `assetsCommitted[ETH_TOKEN]` increases.
3. Operator calls `unlockQueue(ETH_TOKEN, ...)`. `_unlockWithdrawalRequests` increments `unlockedWithdrawalsCount[ETH_TOKEN]`; rsETH is burned via `burnFrom`; ETH is pulled from `LRTUnstakingVault` into `LRTWithdrawalManager`. This transaction is final.
4. `NoReceive` calls `completeWithdrawal(ETH_TOKEN, "")`. Inside `_processWithdrawalCompletion`, `_transferAsset` executes `payable(NoReceive).call{value: amount}("")`, which returns `false`. The call reverts with `EthTransferFailed`. All state mutations in step 4 are rolled back.
5. Every subsequent call to `completeWithdrawal` or `completeWithdrawalForUser` for `NoReceive` reverts identically — the request is never consumed.
6. `sweepRemainingAssets(ETH_TOKEN)` reverts with `PendingWithdrawalsExist` because `unlockedWithdrawalsCount[ETH_TOKEN] > 0`.
7. The ETH is permanently frozen in `LRTWithdrawalManager`. The rsETH is permanently burned. No recovery path exists.