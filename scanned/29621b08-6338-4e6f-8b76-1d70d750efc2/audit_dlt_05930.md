# [?] core/bootstrap: fix panic without backup bootstrap peer functions (#10029)

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2023-09-21
Source: https://github.com/ipfs/kubo/commit/c46cbecb832b9a25f74a275b946b3a0ff3aefaba
Type: security-commit

## Details
core/bootstrap: fix panic without backup bootstrap peer functions (#10029)

Fix panic when backup bootstrap peer load and save funcs are nil

A panic occurs when the first bootstrap round runs is these functions are not assigned in the configuration:
- `LoadBackupBootstrapPeers`
- `SaveBackupBootstrapPeers`

This fix assumes that it is acceptable for these functions to be nil, as it may be desirable to disable the backup peer load and save functionality.
