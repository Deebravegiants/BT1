Audit Report

## Title
Push-Payment ETH Transfer in `_processWithdrawalCompletion` Permanently Freezes User ETH After rsETH Is Burned — (`contracts/LRTWithdrawalManager.sol`)

## Summary
`LRTWithdrawalManager` separates rsETH burning (`unlockQueue`) from ETH delivery (`completeWithdrawal`). After rsETH is irreversibly burned and ETH is redeemed into the contract, the only delivery path pushes ETH directly to the user's address via a low-level call. If that address cannot receive ETH, every completion attempt reverts, all state mutations are rolled back, and the ETH is permanently frozen in the contract with no in-protocol recovery path.

## Finding Description
The withdrawal lifecycle has two non-atomic phases:

**Phase 1 — `unlockQueue` (irreversible):** At lines 305–307, rsETH held by the contract is burned via `IRSETH.burnFrom` and the corresponding ETH is pulled from `LRTUnstakingVault` via `unstakingVault.redeem`. Both operations are final.

**Phase 2 — `_processWithdrawalCompletion` (lines 699–738):** The function performs state mutations — `userAssociatedNonces[asset][user].popFront()` (line 705), `delete withdrawalRequests[requestId]` (line 712), `unlockedWithdrawalsCount[asset]--` (line 717) — and then calls `_transferAsset(asset, user, request.expectedAssetAmount)` (line 734).

`_transferAsset` for ETH (lines 877–879) uses:
```solidity
(bool sent,) = payable(to).call{ value: amount }("");
if (!sent) revert EthTransferFailed();
```

If `to` cannot receive ETH, `sent` is `false` and the function reverts with `EthTransferFailed`. Because all state mutations in lines 705, 712, and 717 occur in the same transaction, they are also reverted — the request remains in the queue indefinitely. Every subsequent call to `completeWithdrawal` or `completeWithdrawalForUser` (line 202) passes the same `user` address to `_processWithdrawalCompletion` and hits the identical failure.

No recovery path exists:
- There is no `cancelWithdrawal` function.
- `sweepRemainingAssets` (line 403) is gated behind `if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist()`, which is permanently blocked because `unlockedWithdrawalsCount[asset]` never reaches zero for the stuck slot.
- The developer comment on line 191 acknowledges ETH transfer issues but dismisses them as "non-impactful gas grief," which is incorrect for the post-burn scenario.

## Impact Explanation
After `unlockQueue` executes, the user's rsETH is permanently burned and the corresponding ETH sits in `LRTWithdrawalManager`. If the user's address cannot receive ETH: `completeWithdrawal` always reverts; `completeWithdrawalForUser` always reverts; `sweepRemainingAssets` is permanently blocked for that asset. The ETH is permanently frozen in the contract.

**Impact class: Critical — Permanent freezing of funds.**

## Likelihood Explanation
The user must be a contract address that rejects ETH. The most realistic scenario is accidental: a multisig or contract wallet (e.g., a Safe without a fallback handler) initiates a withdrawal. After the operator runs `unlockQueue`, the ETH cannot be delivered and is permanently frozen. Contract wallets are common among DeFi power users, making this a realistic production risk. An intentional griefing path also exists (deploying a contract with a togglable ETH-rejection flag), though it requires the attacker to sacrifice their own rsETH. **Likelihood: Medium.**

## Recommendation
1. **Pull-over-push**: Record the claimable amount in a `pendingClaims[user]` mapping in `_processWithdrawalCompletion` and let the user pull it in a separate `claimETH()` call. This decouples state finalization from delivery.
2. **Configurable recipient**: Allow the user to specify a recipient address at `completeWithdrawal` time, authenticated by `msg.sender` ownership of the request.
3. **Try/catch with claimable fallback**: Wrap the ETH push in a try/catch; on failure, store the amount in `pendingClaims[user]` rather than reverting, so the request is finalized and the ETH remains claimable.

## Proof of Concept
```
1. Attacker deploys MaliciousReceiver:
     bool public rejectETH = false;
     receive() external payable { require(!rejectETH, "rejected"); }
     function setReject(bool v) external { rejectETH = v; }

2. MaliciousReceiver calls LRTWithdrawalManager.initiateWithdrawal(ETH_TOKEN, amount, "")
   → rsETH transferred from MaliciousReceiver to WithdrawalManager.

3. Operator calls unlockQueue(ETH_TOKEN, ...)
   → rsETH burned (line 305), ETH redeemed into WithdrawalManager (line 307).
   → unlockedWithdrawalsCount[ETH_TOKEN]++

4. Attacker calls MaliciousReceiver.setReject(true).

5. Anyone calls completeWithdrawal(ETH_TOKEN, "") or
   operator calls completeWithdrawalForUser(ETH_TOKEN, MaliciousReceiver, "")
   → _processWithdrawalCompletion pops nonce, deletes request, decrements counter
   → _transferAsset pushes ETH to MaliciousReceiver (line 734)
   → MaliciousReceiver.receive() reverts
   → EthTransferFailed() thrown; entire tx reverts, all state mutations rolled back.

6. Step 5 reverts indefinitely.
   → ETH permanently locked in LRTWithdrawalManager.
   → unlockedWithdrawalsCount[ETH_TOKEN] never decrements.
   → sweepRemainingAssets blocked for ETH_TOKEN (line 403).
```

A Foundry fork test can confirm this by: (a) deploying `MaliciousReceiver`, (b) initiating a withdrawal, (c) running `unlockQueue`, (d) enabling ETH rejection, (e) asserting that `completeWithdrawal` reverts with `EthTransferFailed` on every call and that `address(withdrawalManager).balance` remains unchanged indefinitely.