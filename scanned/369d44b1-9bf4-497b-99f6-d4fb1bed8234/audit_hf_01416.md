# [M] Destination token decimals cannot be updated after initial setting

## Summary
Severity: Medium
Contest weight: 0.0981
Dataset id: 7305
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In hyperlane-monorepo/move/synthetic-tokens/sources/hyper_coin.move and hyper_coin_collateral.move, in the set_destination_token_decimal function, the use of table::add is designed to abort if an entry for the key already exists, as per the Move Table implementation. Once a decimal value is set for a destination domain, any attempt to modify it will cause the transaction to revert. This provides no mechanism to update decimals in case of misconfiguration or legitimate changes. On the other hand, this could be needed for example in case of a mistake, or an upgrade of the target token on the remote destination.

## Recommendation
Use table::upsert instead of table::add if decimal modifications should be supported.
