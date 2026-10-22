# [C] C-01 | Total DoS Of Epochs

## Summary
Severity: Critical
Contest weight: 0.2370
Dataset id: 1963
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can create redemption requests for their vault shares using the requestRedeem function, which will increase the totalPendingWithdrawals variable. The only requirement regarding the request amount is that the users' balance must be sufficient. Users’ shares are neither transferred nor burned at the creation of the request. Since these shares are transferable, a user can create a request using requestRedeem, transfer shares to another address, create another request, and repeat this process as many times as desired. As a result, totalPendingWithdrawals will be inflated. This allows users to manipulate pendingSharesToBurn and totalSupply, or even cause a complete DoS in the system due to an underflow [here](https://github.com/GuardianAudits/foil-1/blob/5b3416a28dfaa24ba3844e10081e55425d0a286a/packages/protocol/src/vault/Vault.sol#L301C13-L307C15) in the _reconcilePendingTransactions function.

## Recommendation
The redeem workflow should transfer tokens during the request creation process, similar to the deposit flow. The requestRedeem function should transfer shares from the user to the vault. And then, the _redeemShares function should burn these shares from the vault instead of burning from the owner.
