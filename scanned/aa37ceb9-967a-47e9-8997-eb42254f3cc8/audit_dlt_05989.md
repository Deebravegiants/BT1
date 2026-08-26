# [?] fix: remove panic in contracts and add guards for ica and ibc logic  (#1941)

## Summary
Severity: Unknown
Chain: Cronos
Component: crypto-org-chain/cronos
Published: 2025-12-17
Source: https://github.com/crypto-org-chain/cronos/commit/5cabab487a660e6fbb66c4f9bd5c6eb8228f2b7a
Type: security-commit

## Details
fix: remove panic in contracts and add guards for ica and ibc logic  (#1941)

* return calculated gas instead of panic for RelayerContract, add guards for ica precompile and ibc getSourceChannelId

* add guard for Run method for IcaContract

* remove unnecessary else

* minor change

* update to use DefaultGasRequired
