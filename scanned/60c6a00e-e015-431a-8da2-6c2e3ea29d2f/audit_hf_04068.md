# [C] RH-1 | All Asset Vault Funds Can Be Stolen Through Callbacks

## Summary
Severity: Critical
Contest weight: 0.2542
Dataset id: 20521
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The request that is currently being executed in RequestHandler.executeRequest() is cleared at the end of the function. This presents a critical problem as users can execute a deposit/withdraw request with a callback to an arbitrary address that they pass by using assetVault.depositWithCallback() or assetVault.redeemWithCallback(). This callback will be executed before the request gets removed, leaving room for exploitation. assetVault.cancelRequest() immediately cancels a request and returns the funds to the user.

1. Create a deposit/withdraw request with a callback to an arbitrary contract we control.
2. The keeper picks up the request and executes it.
3. We call assetVault.cancelRequest() in the afterDepositExecution()/afterWithdrawalExecution() callback to cancel the request and return the funds to us immediately.
4. We now have the same funds/vault shares as before the request but have also received the funds from the request.

The exploit described above puts all funds in the asset vaults at risk of being stolen.

## Recommendation
Call aggregateVault.clearRequest(key) before executing the callback.
