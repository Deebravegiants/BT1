# [C] Missing instruction to collect transfer fees accumulated in delegate_token_account

## Summary
Severity: Critical
Contest weight: 0.1026
Dataset id: 5382
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
All transfer fees for the Lingo token are collected into delegate_token_account, owned by the delegate PDA signer. While only the program can transfer tokens from delegate_token_account, there is no instruction to transfer these fees to the Lingo team account. As a result, collected fees become permanently stuck.

## Recommendation
Add an instruction, only callable by Config::authority, that transfers tokens from delegate_token_account to team's account.
