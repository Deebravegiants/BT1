# [M] M-06 | GLV Used For Atomic Withdrawals

## Summary
Severity: Medium
Contest weight: 0.1489
Dataset id: 21910
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _processMarketWithdrawal function the collected glv amount is converted into a market token amount and withdrawn from the GLV address. However because the marketTokenAmount is determined during the time of execution, a user may abuse the GLV withdrawal to perform an atomic withdrawal while avoiding the atomic withdrawal fee. Consider the following scenario: - address(1) holds 1 GLV - User A holds 1000 GLV - The totalSupply of GLV is 1001 - User A creates a withdrawal for their 1000 GLV - User A watches for the keeper’s execution transaction and frontruns it to donate 50,000 GM tokens to the GLV in the same block - The keeper’s execution transaction now credits User A with 1000/1001 * 50,000 of these GM tokens for their GLV withdrawal - User A is able to withdraw their GM tokens in a single block while only paying the TwoStep swapPricing fee and 10 basis points for their loss to the initial deposit address

## Recommendation
This manipulation is not attractive when there are multiple even holders of a GLV supply, as the donated tokens will be split up amongst each holder. However, be wary of this gaming when launching new GLVs and consider using an internal storage for the tracking of the GM token balance of each GLV rather than relying on the balanceOf.
