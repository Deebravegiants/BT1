Audit Report

## Title
Stuck ETH Withdrawal From Non-Receivable Contract Permanently Blocks `sweepRemainingAssets` - (File: contracts/LRTWithdrawalManager.sol)

## Summary
When a smart contract that reverts on ETH receipt initiates an ETH withdrawal, every subsequent call to `completeWithdrawal` or `completeWithdrawalForUser` reverts inside `_transferAsset`, rolling back the `unlockedWithdrawalsCount[asset]--` decrement. Because the counter is never decremented, `hasUnlockedWithdrawals(ETH)` permanently returns `true`, causing `sweepRemainingAssets(ETH)` to permanently revert with `PendingWithdrawalsExist`. There is no admin escape hatch to cancel the stuck request or redirect the ETH.

## Finding Description
Inside `_processWithdrawalCompletion`, state mutations occur in this order:

1. **L705** – `userAssociatedNonces[asset][user].popFront()` removes the nonce from the queue.
2. **L712** – `delete withdrawalRequests[requestId]` clears the request.
3. **L717** – `unlockedWithdrawalsCount[asset]--` decrements the counter.
4. **L734** – `_transferAsset(asset, user, request.expectedAssetAmount)` pushes ETH to the user.

`_transferAsset` for ETH performs a low-level call and reverts with `EthTransferFailed` if the recipient rejects the transfer:

```solidity
// L876-L883
(bool sent,) = payable(to).call{ value: amount }("");
if (!sent) revert EthTransferFailed();
```

Because Solidity reverts roll back all state changes in the transaction, the `popFront`, `delete`, and `--` at steps 1–3 are all undone. The withdrawal request is restored to the queue and `unlockedWithdrawalsCount[ETH]` returns to its pre-call value (still > 0).

`sweepRemainingAssets` gates on `hasUnlockedWithdrawals`:

```solidity
// L403
if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist();
```

`hasUnlockedWithdrawals` simply checks:

```solidity
// L629-L631
return unlockedWithdrawalsCount[asset] > 0;
```

With the counter permanently > 0, `sweepRemainingAssets(ETH)` is permanently blocked. No privileged function exists to cancel the stuck request, force-decrement the counter, or redirect the ETH to a different address.

Additionally, the user's own ETH (whose corresponding rsETH was already burned during `unlockQueue` at L305) is permanently frozen in the contract with no recovery path.

## Impact Explanation
**Medium – Permanent freezing of unclaimed yield.**

Any residual ETH that accumulates in the withdrawal manager (Aave interest withdrawn via `_withdrawFromAave`, rounding dust, or direct ETH sends) cannot be swept to the treasury because `sweepRemainingAssets(ETH)` is permanently blocked. The `collectInterestToTreasury` path handles Aave aWETH interest separately, but raw ETH balance accumulation has no other recovery mechanism once `sweepRemainingAssets` is blocked. The ETH committed to the stuck withdrawal is also permanently frozen with no admin recovery path.

## Likelihood Explanation
**Low-to-Medium.** The scenario arises whenever a smart contract wallet (multisig, proxy, or intentionally crafted contract) calls `initiateWithdrawal` for ETH without implementing a `receive()` function, or with one that reverts. This can happen accidentally (e.g., a Gnosis Safe that has not enabled ETH receipt) or deliberately as a griefing attack. No privileged role is required; `initiateWithdrawal` is open to any supported asset holder. The attacker sacrifices their own rsETH/ETH to permanently block the sweep function.

## Recommendation
1. **Add an admin escape hatch**: Introduce a manager-only function that can cancel a stuck withdrawal request (returning the rsETH to the user or burning it) and decrement `unlockedWithdrawalsCount` without attempting the ETH transfer.
2. **Allow withdrawal redirection**: Let the user or an operator specify an alternative recipient address for the ETH transfer, bypassing a stuck contract address.
3. **Decouple the counter decrement from the transfer**: Move `unlockedWithdrawalsCount[asset]--` to after a successful `_transferAsset`, or adopt a pull-based pattern where the request is marked "claimable" and the user pulls funds rather than having them pushed.

## Proof of Concept
```solidity
// 1. Deploy a contract with no receive() — any ETH transfer to it reverts.
// 2. Fund it with rsETH; call initiateWithdrawal(ETH_TOKEN, rsETHAmount, "").
// 3. Operator calls unlockQueue(ETH, ...) — unlockedWithdrawalsCount[ETH] becomes 1,
//    rsETH is burned, ETH is redeemed from the unstaking vault into the withdrawal manager.
// 4. Call completeWithdrawal(ETH, "") from the non-receivable contract.
//    → _transferAsset reverts with EthTransferFailed
//    → entire tx reverts; unlockedWithdrawalsCount[ETH] stays 1
// 5. Assert: hasUnlockedWithdrawals(ETH) == true  (permanently)
// 6. Manager calls sweepRemainingAssets(ETH)
//    → reverts with PendingWithdrawalsExist  (permanently)
// 7. ETH balance in withdrawal manager grows with no recovery path.
//
// completeWithdrawalForUser (operator path) also fails because it calls
// _processWithdrawalCompletion(asset, user, ...) with the same non-receivable user address.
```