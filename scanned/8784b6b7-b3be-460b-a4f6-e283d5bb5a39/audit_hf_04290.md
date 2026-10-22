# [M] M-05 | Dangerous Atomic Withdrawal Invocation Pattern

## Summary
Severity: Medium
Contest weight: 0.1311
Dataset id: 21429
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The executeAtomicWithdrawal function is intended to be called by users or integrators on the WithdrawalHandler after depositing market tokens into the WithdrawalVault through the ExchangeRouter. However users are not able to use a multicall on the ExchangeRouter to do so seamlessly in a single transaction, as the executeAtomicWithdrawal function is only available through the WithdrawalHandler contract. This promotes a dangerous pattern where users may send their market tokens to the WithdrawalVault through the ExchangeRouter and call the executeAtomicWithdrawal function on the WithdrawalHandler in separate transactions. In this case the user is exposed to risk of total loss of funds if another actor frontruns their second transaction to executeAtomicWithdrawal, by malicious intent or on accident.

## Recommendation
Consider only exposing the executeAtomicWithdrawal functionality through the ExchangeRouter, this way it can be invoked through a multicall. Additionally, be sure to document this risk to users and integrators, advising them to use the multicall feature.
