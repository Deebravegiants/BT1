# [M] Native.startWithdrawal() can be called repeatedly to queue an infinite number of withdrawals

## Summary
Severity: Medium
Contest weight: 0.4322
Dataset id: 13991
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The maximum amount of ETH a node owner can withdraw through NativeVault.startWithdrawal() is limited by withdrawableWei():
```solidity
if (weiAmount > withdrawableWei(msg.sender)) revert WithdrawMoreThanMax();
```
withdrawableWei(msg.sender) is the minimum between the amount of ETH in the caller's native node and the asset equivalent of his shares, so it doesn't exclude the amount of ETH that are currently in pending withdrawals.
As such, users can queue an infinite amount of ETH for withdrawals by repeatedly calling startWithdrawal() with weiAmount = withdrawableWei(msg.sender). This allows them to bypass MIN_WITHDRAWAL_DELAY for withdrawals in the future as they have an infinite number of pending withdrawals, and can call finishWithdrawal() anytime to instantly perform a withdrawal.

## Recommendation
Consider tracking the amount of ETH in pending withdrawals and subtracting it from withdrawableWei() in startWithdrawal().
In NativeVaultLib, add a new mapping in Storage named nodeOwnerToWithdrawAmount, which represents the total amount of assets in pending withdrawals for each node owner:
```diff
// mapping of node owner to their withdraw nonce
mapping(address nodeOwner => uint256 withdrawNonce) nodeOwnerToWithdrawNonce;
+ // mapping of node owner to their total pending withdrawal amount
+ mapping(address nodeOwner => uint256 withdrawAmount) nodeOwnerToWithdrawAmount;
// mapping of owners' withdraw nonce to pending withdrawals
mapping(bytes32 ownerWithdrawNonce => QueuedWithdrawal withdrawal) withdrawalMap;
```
In startWithdrawal(), subtract nodeOwnerToWithdrawAmount from withdrawableWei(). Additionally, nodeOwnerToWithdrawAmount should be increased by weiAmount whenever a new withdrawal is started:
```diff
- if (weiAmount > withdrawableWei(msg.sender)) revert WithdrawMoreThanMax();
NativeVaultLib.Storage storage self = _state();
+ if (weiAmount > withdrawableWei(msg.sender) - self.nodeOwnerToWithdrawAmount[msg.sender]) {
+
    revert WithdrawMoreThanMax();
+ }
+ self.nodeOwnerToWithdrawAmount[msg.sender] += weiAmount;
```
In finishWithdrawal(), whenever a withdrawal is finished, subtract the amount of assets withdrawn from nodeOwnerToWithdrawAmount:
```diff
if (startedWithdrawal.start == 0) revert WithdrawalNotFound();
if (startedWithdrawal.start + Constants.MIN_WITHDRAWAL_DELAY > block.timestamp) {
    revert MinWithdrawDelayNotPassed();
}
+ self.nodeOwnerToWithdrawAmount[startedWithdrawal.nodeOwner] -= startedWithdrawal.assets;
```
