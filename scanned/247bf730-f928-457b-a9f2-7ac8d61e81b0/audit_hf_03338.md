# [C] GSU-1 | Missing Swap Gas Estimation

## Summary
Severity: Critical
Contest weight: 0.1720
Dataset id: 18189
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The estimateExecuteWithdrawalGasLimit does not account for either the longTokenSwapPath or the shortTokenSwapPath, therefore the keeper will not be remunerated for users using the swap feature on withdrawals. This will lead to the protocol keeper being unexpectedly drained of the native token, potentially stopping execution on the exchange for a period of time. The gas draining can occur due to regular exchange usage or can be easily leveraged by an attacker to maliciously drain the keeper.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/GSU_1.ts

## Recommendation
Add gas estimation logic for the longTokenSwapPath and shortTokenSwapPath in the estimateExecuteWithdrawalGasLimit function, similar to the estimation for deposits.
