# [M] GLOBAL-3 | Vault Frozen On Single Account

## Summary
Severity: Medium
Contest weight: 0.1055
Dataset id: 20533
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a subaccount creates a deposit or withdrawal, the Vault is frozen to prevent misuse such as
borrowing when the underlying funds are not present, putting the protocol at risk. While the Vault is
frozen, all other subaccounts are unable to perform any actions, including depositing, withdrawing,
and borrowing.
This poses a potential problem as a deposit or withdrawal may take a prolonged time to be executed,
and the order cannot be cancelled for the MIN_ORACLE_BLOCK_CONFIRMATIONS. During this
period, a subaccount that is close to liquidation is unable to deposit into the protocol and save their
position.

## Recommendation
Consider allowing users to deposit and withdraw if another subaccount is frozen, but not borrow.
Otherwise, explicitly document to users that if one account is in a frozen state, all other accounts
cannot perform Vault actions.
