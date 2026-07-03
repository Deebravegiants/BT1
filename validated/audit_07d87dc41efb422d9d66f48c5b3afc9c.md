Audit Report

## Title
Permanent Freezing of ETH for Contract Recipients Unable to Receive ETH — (`contracts/LRTWithdrawalManager.sol`)

## Summary
Any user whose withdrawal address is a contract that reverts on ETH receipt (no `receive()`, or a conditionally reverting one) will have their ETH permanently frozen in `LRTWithdrawalManager`. Neither `completeWithdrawal` nor `completeWithdrawalForUser` can redirect the ETH to an alternative address, and `sweepRemainingAssets` is blocked by the stuck withdrawal counter. Recovery requires a contract upgrade.

## Finding Description
`_processWithdrawalCompletion` (line 699) performs state mutations — `popFront` on `userAssociatedNonces` (line 705), `delete withdrawalRequests[requestId]` (line 712), and `unlockedWithdrawalsCount[asset]--` (line 717) — before calling `_transferAsset(asset, user, request.expectedAssetAmount)` at line 734.

`_transferAsset` for ETH (lines 876–879) uses a low-level call:
```solidity
(bool sent,) = payable(to).call{ value: amount }("");
if (!sent) revert EthTransferFailed();
```
If `to` is a contract that reverts on ETH receipt, `sent == false` and `EthTransferFailed` is thrown. Solidity reverts all state changes, so the nonce pop, request deletion, and counter decrement are all rolled back. The request remains intact and `unlockedWithdrawalsCount[asset]` stays ≥ 1.

`completeWithdrawalForUser` (lines 192–204) provides no alternative recipient — it passes `user` (the reverting address) directly into `_processWithdrawalCompletion`. The NatSpec comment even acknowledges this: *"Not expected to be used for ETH"*, but provides no recovery path. The ETH transfer will revert identically.

`sweepRemainingAssets` (line 403) is also blocked:
```solidity
if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist();
```
Since the stuck withdrawal keeps `unlockedWithdrawalsCount[asset] > 0`, this guard always fires, preventing any protocol-level recovery.

## Impact Explanation
**Critical — Permanent Freezing of Funds.** ETH redeemed from the unstaking vault into `LRTWithdrawalManager` has no on-chain path to reach the user or be recovered by the protocol under the current unmodified code. A contract upgrade is required to unfreeze the funds.

## Likelihood Explanation
Moderate. Any smart contract wallet, multisig, or custom contract that does not implement `receive() external payable`, or has a `receive()` that conditionally reverts (e.g., a guard, a paused state, or a reentrancy lock), and initiates an ETH withdrawal will trigger this. This is a realistic scenario for protocol integrators and smart-contract-based treasury addresses. The user need only call `initiateWithdrawal` from such a contract — no attacker cooperation is required.

## Recommendation
Add an `alternativeRecipient` parameter to `completeWithdrawalForUser` so operators can redirect ETH to a working address:
```solidity
function completeWithdrawalForUser(
    address asset,
    address user,
    address recipient,   // where to actually send the funds
    string calldata referralId
) external nonReentrant whenNotPaused onlyLRTOperator {
    _processWithdrawalCompletion(asset, user, recipient, referralId);
    emit AssetWithdrawalCompletedBy(msg.sender);
}
```
Pass `recipient` through to `_transferAsset` instead of `user`. For `completeWithdrawal`, default `recipient = msg.sender`. This preserves the existing self-service path while giving operators a recovery mechanism.

## Proof of Concept
```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

contract RevertOnReceive {
    // No receive() — all ETH transfers revert

    function initiateETHWithdrawal(address withdrawalManager, uint256 rsETHAmount) external {
        ILRTWithdrawalManager(withdrawalManager).initiateWithdrawal(ETH_TOKEN, rsETHAmount, "");
    }
}

// Foundry test sequence:
// 1. Deploy RevertOnReceive
// 2. Fund it with rsETH, call initiateETHWithdrawal(wm, amount)
// 3. Operator calls unlockQueue(ETH_TOKEN)
// 4. vm.expectRevert(EthTransferFailed);
//    revertContract.tryComplete(wm);  // completeWithdrawal reverts
// 5. vm.expectRevert(EthTransferFailed);
//    wm.completeWithdrawalForUser(ETH_TOKEN, address(revertContract), "");  // also reverts
// 6. assertGt(wm.unlockedWithdrawalsCount(ETH_TOKEN), 0);  // counter unchanged
// 7. vm.expectRevert(PendingWithdrawalsExist);
//    wm.sweepRemainingAssets(ETH_TOKEN);  // blocked
// → ETH is permanently locked in LRTWithdrawalManager
```