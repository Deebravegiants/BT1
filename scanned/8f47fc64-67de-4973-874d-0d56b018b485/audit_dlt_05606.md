# [?] core/rawdb: fix panic in freezer (#30973)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-01-06
Source: https://github.com/ethereum/go-ethereum/commit/c5a8d3485191d15363b9817da1afcac3fce5ddeb
Type: security-commit

## Details
core/rawdb: fix panic in freezer (#30973)

Fixes an issue where the node panics when an LStat fails with something 
other than os.ErrNotExist

closes https://github.com/ethereum/go-ethereum/issues/30968
