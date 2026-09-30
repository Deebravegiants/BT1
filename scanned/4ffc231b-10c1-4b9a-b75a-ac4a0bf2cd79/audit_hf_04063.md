# [M] RH-4 | Lack Of Slippage On Deposits And Withdrawals

## Summary
Severity: Medium
Contest weight: 0.1691
Dataset id: 20515
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Deposits and withdrawals to/from the asset vaults are a 2 step operation. The user initiates the action, thus creating a pending order and a keeper asynchronously executes that operation.

Although the execution keeper operates relatively fast, between 1-3 blocks since the initial request, there will still exist situations where an operation is initiated exactly before a rebalance is opened. During a rebalance, operations cannot be executed by the keeper, as such the user action will only be executed after the rebalance closes.

An issue is that users expect their deposit/redeem to result in the exact amounts indicated by the previewDeposit and previewRedeem functions at that time, but because of the price being recalculated again at the time the operation is executed, users may experience negative slippage and obtain fewer tokens.

During an epoch, a meaningful difference may not appear due to fast keeper response, but for those transactions that ultimately do become pending during a rebalance, the price difference may be significant enough of a loss. Since these operations flow normally, this situation will occur.

## Recommendation
Add a slippage parameter when users deposit/redeem into the vault which will be passed and used by the RequestHandler when invoked by the keepers. Since the vaults are not meant to be ERC4626 compliant, this alteration does not come with a negative impact on the protocol.
