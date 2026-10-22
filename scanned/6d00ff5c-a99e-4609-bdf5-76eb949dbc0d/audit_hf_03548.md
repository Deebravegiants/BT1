# [M] GLOBAL-3 | Centralization Risk

## Summary
Severity: Medium
Contest weight: 0.1324
Dataset id: 19350
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Throughout the smart contract system there is a lack of validation to prevent privileged addresses from taking malicious actions or even committing errors that have drastic consequences. Executing malicious withdrawals, settlements, ADLs, and liquidations. No validation that the liquidationFee = liquidatorFee + insuranceFee. No validation that the ratio of positionQtyTransfer to costPositionTransfer is accurate to the adlPrice provided. No validation that tokens being actively used as collateral cannot be removed from support, causing liquidations and insolvency. No validation that trade.notional = trade.tradeQty * trade.executedPrice in the executeProcessValidatedFutures function. No cap on configured values such as the maxWithdrawalFee and liquidationFeeMax. No cap on the liquidationFee as the liquidationFeeMax is unused at the contract level.

## Recommendation
Consider implementing validations to prevent any potential errors privileged addresses may make. And be sure to document the risks of these privileged abilities.
