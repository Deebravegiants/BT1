# [M] GLOBAL-5 | Execution Fee DoS

## Summary
Severity: Medium
Contest weight: 0.0638
Dataset id: 17863
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is a potential DoS with createDeposit, createWithdrawal, and createOrder as a malicious address may send a miniscule amount of WNT to the deposit/withdrawal/order store such that another user’s WNT deposit no longer matches the executionFee in their deposit. Thus, the deposit execution reverts and is unable to be created.

## Recommendation
Consider removing the strict equality for the executionFee or handling the accounting in the depositStore such that another address cannot increase the deposit amount for a user.
