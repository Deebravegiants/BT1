# [H] H-1 Incorrect Handling of Fee-on-Transfer Tokens

## Summary
Severity: High
Contest weight: 0.1772
Dataset id: 8656
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The issue arises within the receiveTokens function of the LOB contract.
There is a vulnerability related to the improper handling of fee-on-transfer tokens. The function does not verify that the balances have been adjusted as expected after the safeTransferFrom calls. This oversight can result in incorrect token balances, especially when dealing with tokens that impose transfer fees or employ other mechanisms that alter the expected transfer amount.
The issue is classified as high severity as it can lead to discrepancies in token balances, potentially causing financial inconsistencies and loss.

## Recommendation
We recommend adding a check to ensure that the balances reflect the expected changes after the safeTransferFrom calls. If the balances do not match the expected change, the transaction should be reverted to safeguard against financial irregularities.
