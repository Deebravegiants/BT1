# [H] _splitWithdrawRequest will make invalid with-

## Summary
Severity: High
Contest weight: 0.6356
Dataset id: 22974
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function _splitWithdrawRequest(address _from, address _to, uint256 vaultShares) private {
    WithdrawRequest storage w = VaultStorage.getAccountWithdrawRequest()[_from];
    if (w.vaultShares == vaultShares) {
        // If the resulting vault shares is zero, then delete the request.
        // The _from account's
        delete VaultStorage.getAccountWithdrawRequest()[_from];
    }
    WithdrawRequest storage toWithdraw = VaultStorage.getAccountWithdrawRequest()[_to];
    toWithdraw.requestId = w.requestId;
    toWithdraw.vaultShares += vaultShares;
    toWithdraw.amount += _computeAmountForShares(vaultShares);
}
```
When an account is deleveraged, _splitWithdrawRequest is called so that pending withdraw requests of the account that is being liquidated are split between them and the liquidator. However when the account is being fully liquidated, the old withdraw request is deleted which creates an invalid Id for the liquidator's withdrawRequest. In _splitWithdrawRequest the request of the from address is being read by storage: WithdrawRequest storage w = VaultStorage.getAccountWithdrawRequest()[_from]; Then the following check is made to delete the withdraw request of the from account if all the vault tokens are being taken from him: if (w.vaultShares == vaultShares) { // If the resulting vault shares is zero, then delete the request. The _from account's // withdraw request is fully transferred to _to delete VaultStorage.getAccountWithdrawRequest()[_from]; } Here the delete keyword is used to reset the withdraw request of the from account. However the w variable is still a pointer to this place in storage meaning that resetting VaultStorage.getAccountWithdrawRequest()[_from] will also be resetting w. As a result w.requestId=0 and toWithdraw.requestId = w.requestId; Here the new requestId is equal to 0 which is the default value meaning that this withdraw request will not be recognized by _finalizeWithdrawsManual and the other finalize withdraw functions and all these vault shares will be lost. Also if initiateWithdraw is called the old vaultShares will be wiped out for the new shares to be withdrawn. Loss of vaut tokens for the liquidator.

## Recommendation
Store the requestId of the from address in another memory variable.
