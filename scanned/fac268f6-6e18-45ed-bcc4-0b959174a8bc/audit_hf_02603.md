# [M] assets > withdrawableWei() check in _decreaseBalance() causes NativeVault.finishWithdrawal() to revert when slashing occurs

## Summary
Severity: Medium
Contest weight: 0.5871
Dataset id: 13992
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When finishing a withdrawal, NativeVault.finishWithdrawal() calls _decreaseBalance() to decrease the node owner's asset balance:
```solidity
_decreaseBalance(startedWithdrawal.nodeOwner, startedWithdrawal.assets);
```
_decreaseBalance() checks that startedWithdrawal.assets is not greater than withdrawableWei():
```solidity
if (assets > withdrawableWei(_of)) revert WithdrawMoreThanMax();
```
Note that withdrawableWei() returns the minimum between the node owner's native node balance and the assets equivalent of his shares.
However, if Karak operator or the beacon chain slashes the node owner's ETH balance before a withdrawal is finished, it might become impossible for the withdrawal to be executed using finishWithdrawal() due to this check.
For example:
• Assume that:
– A node owner holds 32e18 shares that corresponds to 32 ETH.
– He is the only node owner in the entire protocol, so totalSupply and totalAssets are both 32e18 as well.
• Node owner calls startWithdrawal() with weiAmount = 32e18 to withdraw his entire balance.
• Karak operator calls slashAssets() to slash 1 ETH, so totalAssets = 31e18.
• Node owner calls finishWithdrawal() to finish the withdrawal. In _decreaseBalance():
– withdrawableWei() returns 31 ETH.
– startedWithdrawal.assets = 32e18 is greater than withdrawableWei(), so the check reverts.
If a withdrawal can never be completed using finishWithdrawal(), as demonstrated above, the node owner will have to go through the full MIN_WITHDRAWAL_DELAY period again to withdraw his assets.

## Recommendation
Consider removing the assets > withdrawableWei(_of) check from _decreaseBalance():
```diff
function _decreaseBalance(address _of, uint256 assets) internal {
    NativeVaultLib.Storage storage self = _state();
    if (assets > withdrawableWei(_of)) revert WithdrawMoreThanMax();
```
In finishWithdrawal(), consider limiting the amount of assets withdrawn to withdrawableWei() instead of reverting:
```diff
+ uint256 withdrawableAssets = withdrawableWei(startedWithdrawal.nodeOwner);
+ if (startedWithdrawal.assets > withdrawableAssets) {
+
    startedWithdrawal.assets = withdrawableAssets;
+ }
_decreaseBalance(startedWithdrawal.nodeOwner, startedWithdrawal.assets);
INativeNode(self.ownerToNode[startedWithdrawal.nodeOwner].nodeAddress).withdraw(
    startedWithdrawal.to, startedWithdrawal.assets
);
```
