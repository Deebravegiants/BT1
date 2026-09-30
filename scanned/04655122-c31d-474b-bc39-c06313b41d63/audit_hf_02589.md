# [H] assets > withdrawableWei() check in _decreaseBalance() could DOS NativeVault._updateSnapshot()

## Summary
Severity: High
Contest weight: 0.8838
Dataset id: 13960
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Whenever a snapshot is completed, NativeVault._updateSnapshot() calls to update the node owner's balance:
```solidity
_updateBalance(nodeOwner, totalDeltaWei);
```
If totalDeltaWei happens to be negative, _updateBalance() calls _decreaseBalance(), which checks that totalDeltaWei is not greater than withdrawableWei():
```solidity
if (assets > withdrawableWei(_of)) revert WithdrawMoreThanMax();
```
Note that withdrawableWei() returns the minimum between the node owner's native node balance and the assets equivalent of his shares.
However, this check could cause _updateSnapshot() to incorrectly revert when completing a snapshot. For example:
• Assume a node owner has 32 ETH in a validator and no ETH in his native node.
• The following events occur:
– His native node receives 0.3 ETH from validator rewards.
– The beacon chain slashes his validator for 1 ETH, leaving 31 ETH remaining.
• He calls startSnapshot(), which sets nodeBalanceWei = 0.3 ether as his native node gained 0.3 ETH.
• He calls validateSnapshotProofs(), which sets balanceDeltaWei = -1 ether as his validator lost 1 ETH.
• When _updateSnapshot() is called:
– totalDeltaWei = 0.3 ether - 1 ether = -0.7 ether
– _decreaseBalance() is called with assets = 0.7 ether.
– withdrawableWei() returns his native node's balance, which is 0.3 ETH.
– Since assets > withdrawableWei(), the function reverts.
As seen from above, if a node owner's validators are slashed for more than his native node's current balance, _updateSnapshot() will always revert when called. This makes it impossible to update his snapshot, even after it expires.

## Recommendation
Consider removing the assets > withdrawableWei(_of) check from _decreaseBalance():
```solidity
function _decreaseBalance(address _of, uint256 assets) internal {
NativeVaultLib.Storage storage self = _state();
if (assets > withdrawableWei(_of)) revert WithdrawMoreThanMax();
```
This check should be moved into finishWithdrawal() instead to ensure the user cannot withdraw assets than he should be able to.
