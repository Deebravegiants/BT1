Audit Report

## Title
ETH Push Payment to Reverting Contract Address Causes Permanent Fund Freeze in `_processWithdrawalCompletion` — (File: contracts/LRTWithdrawalManager.sol)

## Summary
`LRTWithdrawalManager._transferAsset` pushes ETH to the user's address via a low-level `.call`. If the recipient is a contract whose `receive()` reverts, `completeWithdrawal` will always revert, permanently trapping the ETH inside the withdrawal manager. Because rsETH is burned irreversibly in the prior `unlockQueue` transaction, the user loses their rsETH and the ETH can never be recovered by either the user or the protocol.

## Finding Description
The withdrawal lifecycle spans two separate transactions:

**Transaction 1 — `unlockQueue` (operator-only):**
At line 305, rsETH held by the manager is burned: `IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned)`. At line 307, the equivalent ETH is pulled from `LRTUnstakingVault` into `LRTWithdrawalManager`. This burn is final and cannot be reversed.

**Transaction 2 — `completeWithdrawal`:**
`_processWithdrawalCompletion` (lines 699–738) performs state mutations — `popFront` (line 705), `delete withdrawalRequests[requestId]` (line 712), `unlockedWithdrawalsCount[asset]--` (line 717) — and then calls `_transferAsset(asset, user, request.expectedAssetAmount)` at line 734.

`_transferAsset` for ETH (lines 877–879) is:
```solidity
(bool sent,) = payable(to).call{ value: amount }("");
if (!sent) revert EthTransferFailed();
```

If `user` is a contract whose `receive()` reverts, `EthTransferFailed` is thrown, rolling back all state mutations in Transaction 2. The withdrawal request remains in the queue, `unlockedWithdrawalsCount[asset]` stays > 0, and every subsequent call to `completeWithdrawal` or `completeWithdrawalForUser` (line 202, which also calls `_processWithdrawalCompletion` with the same `user` address) will revert identically.

The protocol's only ETH recovery path, `sweepRemainingAssets`, is gated at line 403:
```solidity
if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist();
```
Because `unlockedWithdrawalsCount[asset] > 0` is never decremented (every attempt reverts), `sweepRemainingAssets` is permanently blocked for that asset. No `cancelWithdrawal`, `redirectWithdrawal`, `rescueETH`, or equivalent function exists in the contract.

## Impact Explanation
After `unlockQueue` executes: the user's rsETH is burned (irreversible), the equivalent ETH is held in `LRTWithdrawalManager`, and no code path can deliver or recover it. This is a concrete, permanent freezing of user funds — matching the Critical impact class "Permanent freezing of funds." The frozen ETH also permanently blocks `sweepRemainingAssets` for the entire ETH asset class, potentially affecting other users' recovery paths.

## Likelihood Explanation
The trigger requires the withdrawing address to be a contract that rejects ETH (no `receive()`, or a reverting `receive()`). Smart-contract wallets, multisigs (e.g., Gnosis Safe with ETH rejection policies), protocol-owned treasuries, and contracts upgraded after withdrawal initiation all qualify. No special privileges are required — the freeze is triggered by the normal user-facing `completeWithdrawal` call. The condition is uncommon but realistic in DeFi, and the consequence is irreversible, justifying Critical severity.

## Recommendation
Replace the push-payment pattern with a pull-payment pattern for ETH. Record claimable ETH in a mapping during `_processWithdrawalCompletion` and expose a separate `claimETH()` function:

```solidity
mapping(address user => uint256 ethClaimable) public ethClaimable;

// In _processWithdrawalCompletion, replace _transferAsset call:
if (asset == LRTConstants.ETH_TOKEN) {
    ethClaimable[user] += request.expectedAssetAmount;
} else {
    IERC20(asset).safeTransfer(user, request.expectedAssetAmount);
}

// Separate claim function:
function claimETH() external nonReentrant {
    uint256 amount = ethClaimable[msg.sender];
    if (amount == 0) revert NothingToClaim();
    ethClaimable[msg.sender] = 0;
    (bool sent,) = payable(msg.sender).call{ value: amount }("");
    if (!sent) revert EthTransferFailed();
}
```

This ensures a reverting `receive()` only blocks the individual user's own claim and never corrupts shared accounting state or blocks protocol recovery.

## Proof of Concept
1. Deploy `MaliciousWithdrawer` with `receive() external payable { revert(); }`.
2. From `MaliciousWithdrawer`, approve rsETH and call `initiateWithdrawal(ETH_TOKEN, amount, "")`. rsETH is transferred to `LRTWithdrawalManager`.
3. Operator calls `unlockQueue(ETH_TOKEN, ...)`. Line 305 burns rsETH; line 307 moves ETH from `LRTUnstakingVault` to `LRTWithdrawalManager`. rsETH is now permanently gone.
4. `MaliciousWithdrawer` calls `completeWithdrawal(ETH_TOKEN, "")`. `_transferAsset` at line 878 calls `payable(MaliciousWithdrawer).call{value: amount}("")`, which reverts. `EthTransferFailed` is thrown; all state in `_processWithdrawalCompletion` is rolled back.
5. Repeat step 4 indefinitely — always reverts. rsETH is gone, ETH is stuck in `LRTWithdrawalManager`, `unlockedWithdrawalsCount[ETH_TOKEN] > 0` permanently blocks `sweepRemainingAssets`. Funds are permanently frozen with no recovery path.