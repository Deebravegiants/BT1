# [M] GLOBAL-4 | Vault Can Be Drained On Specific Chain

## Summary
Severity: Medium
Contest weight: 0.0545
Dataset id: 19361
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Because a withdrawal message can be sent to a Vault on any supported chain, a malicious user can deposit in a Vault on one chain and withdraw from a vault on another chain. This can be used to drain the Vault on a chain, forcing other users to withdraw their liquidity on other chains.

## Recommendation
Consider restricting what Vault a user can withdraw from, such as only allowing withdrawals from the chain they performed a deposit.
