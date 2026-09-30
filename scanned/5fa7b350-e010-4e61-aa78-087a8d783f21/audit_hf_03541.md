# [M] GLOBAL-2 | LayerZero Message Blocking

## Summary
Severity: Medium
Contest weight: 0.1309
Dataset id: 19341
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
LayerZero implements blocking functionality such that when a transaction on the destination chain fails, before any new transactions can be executed, the failed transaction has to be retried until success. A malicious user can submit a deposit or withdrawal they know will fail, and will prevent all other deposits and withdrawals from occurring, leading to loss of protocol functionality and loss of funds for those who already deposited. Some methods a malicious user can use to force such a scenario include but are not limited to:
1) Broker is allowed for Vault on srcChain but disallowed on the VaultManager on dstChain. The configuration of these two contracts aren’t atomic.
2) depositTo for an address that is blacklisted for the collateral token. When the blacklisted address triggers a withdraw action, the Vault withdrawal will revert.

## Recommendation
Consider utilizing a non-blocking approach as described in [LayerZero documentation](https://layerzero.gitbook.io/docs/evm-guides/advanced/nonblockinglzapp).
