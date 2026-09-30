# [H] Uninitialized maxTransaction and maxWallet variables prevent trading for non-excluded users

## Summary
Severity: High
Contest weight: 0.2012
Dataset id: 4210
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the RetardedTokenContract, the variables maxTransaction and maxWallet are intended to enforce trading limits during the initial 10 minutes after trading is activated. This is conditional upon the maxBuyStat1 variable being set to true in the constructor. The purpose of these variables is to restrict the maximum transaction size and wallet balance for users who are not excluded from these limits, as defined by the _isExcludedFromMaxTransaction mapping. However, these variables are never initialized within the contract, resulting in their default value being zero. Consequently, if maxBuyStat1 is true, any transaction amount or wallet balance for non-excluded users will be forced to be zero, effectively preventing them from trading during this initial 10 minutes period.

## Recommendation
To resolve this issue, initialize the maxTransaction and maxWallet variables with appropriate values in the constructor.
