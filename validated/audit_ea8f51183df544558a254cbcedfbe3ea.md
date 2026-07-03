Audit Report

## Title
ETH Permanently Frozen for Contract Depositors Without `receive()` - (File: contracts/LRTWithdrawalManager.sol)

## Summary

`LRTWithdrawalManager` splits the withdrawal lifecycle across two separate transactions: `unlockQueue` (burns rsETH, redeems ETH) and `completeWithdrawal` (transfers ETH to user). If the depositor is a smart contract without a `receive()` or `fallback()` function, `completeWithdrawal` permanently reverts after rsETH has already been irreversibly burned in the prior transaction, permanently freezing the corresponding ETH in the contract with no recovery path available to the user or protocol without an upgrade.

## Finding Description

**Step 1 — `unlockQueue` (separate transaction):** rsETH is burned and ETH is redeemed from `LRTUnstakingVault` into `LRTWithdrawalManager`:

```solidity
// contracts/LRTWithdrawalManager.sol L305-307
if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
unstakingVault.redeem(asset, assetAmountUnlocked);
```

This transaction is final and irreversible.

**Step 2 — `completeWithdrawal` (separate transaction):** Calls `_processWithdrawalCompletion`, which at L734 calls `_transferAsset(asset, user, request.expectedAssetAmount)`. `_transferAsset` uses a low-level call:

```solidity
// contracts/LRTWithdrawalManager.sol L877-879
(bool sent,) = payable(to).call{ value: amount }("");
if (!sent) revert EthTransferFailed();
```

If `user` is a contract without `receive()`/`fallback()`, `sent == false` and the function reverts with `EthTransferFailed`. Because the revert unwinds all state changes within `_processWithdrawalCompletion` (the `popFront`, `delete withdrawalRequests[requestId]`, and `unlockedWithdrawalsCount[asset]--` at L705, L712, L717), the withdrawal request record is fully restored. However, the rsETH burn from Step 1 is in a prior committed transaction and cannot be undone.

**No recovery path exists:**
- `completeWithdrawal` and `completeWithdrawalForUser` both route to `_processWithdrawalCompletion(asset, user, referralId)` — there is no alternative recipient parameter; both always send to `user`.
- `sweepRemainingAssets` is blocked because `hasUnlockedWithdrawals(asset)` returns `true` (since `unlockedWithdrawalsCount[asset] > 0` is preserved by the revert), causing it to revert with `PendingWithdrawalsExist` at L403.

## Impact Explanation

**Critical — Permanent freezing of funds.**

A contract depositor whose address cannot receive ETH will have rsETH permanently burned (Step 1 is irreversible) and ETH permanently locked in `LRTWithdrawalManager` (Step 2 always reverts, sweep is blocked). The ETH cannot be recovered by the user or by the protocol without a contract upgrade. This matches the Critical impact class: "Permanent freezing of funds."

## Likelihood Explanation

Smart contract wallets (Gnosis Safe multisigs, DAO treasuries, protocol-owned accounts) are common depositors in LRT protocols. A contract that holds rsETH and initiates a withdrawal may not implement `receive()`. There is no on-chain check in `initiateWithdrawal` preventing such a contract from queuing a withdrawal. The failure is silent until Step 2, after rsETH is already burned. The condition is fully user-triggerable without any privileged action beyond the normal operator `unlockQueue` call, which is part of the standard withdrawal lifecycle.

## Recommendation

Add an optional `recipient` parameter to `completeWithdrawal` so users can specify an EOA or a contract capable of receiving ETH:

```solidity
function completeWithdrawal(
    address asset,
    address recipient,
    string calldata referralId
) external nonReentrant whenNotPaused {
    _processWithdrawalCompletion(asset, msg.sender, recipient, referralId);
}
```

Update `_processWithdrawalCompletion` to accept a separate `recipient` address and pass it to `_transferAsset` instead of `user`. `completeWithdrawalForUser` should similarly accept a `recipient` parameter. Alternatively, allow users to register a withdrawal recipient address before `unlockQueue` is called, so the recipient is recorded at initiation time.

## Proof of Concept

1. A Gnosis Safe (no `receive()`) calls `initiateWithdrawal(ETH_TOKEN, rsETHAmount, "")`. rsETH is transferred to `LRTWithdrawalManager` and a `WithdrawalRequest` is recorded.
2. Operator calls `unlockQueue(ETH_TOKEN, ...)`. At L305-307, rsETH is burned and ETH is redeemed into `LRTWithdrawalManager`. This transaction commits and is irreversible.
3. The Safe calls `completeWithdrawal(ETH_TOKEN, "")`. `_processWithdrawalCompletion` pops the nonce, deletes the request, decrements `unlockedWithdrawalsCount`, then calls `_transferAsset(ETH_TOKEN, safeAddress, amount)`.
4. `payable(safeAddress).call{value: amount}("")` returns `success = false` (Safe has no `receive()`). The function reverts with `EthTransferFailed`. All state changes in Step 3 are rolled back.
5. Step 3 can be repeated indefinitely — it will always revert. rsETH remains burned. ETH remains in `LRTWithdrawalManager`. `sweepRemainingAssets` reverts with `PendingWithdrawalsExist`. Funds are permanently frozen.

**Foundry test plan:** Deploy `LRTWithdrawalManager` on a fork. Deploy a mock contract with no `receive()` as the depositor. Execute the full lifecycle (deposit → initiateWithdrawal → unlockQueue → completeWithdrawal). Assert that `completeWithdrawal` reverts with `EthTransferFailed`, that `withdrawalRequests[requestId]` is non-zero (request preserved), and that `address(withdrawalManager).balance` equals the expected ETH amount (ETH stuck). Assert `sweepRemainingAssets` also reverts.