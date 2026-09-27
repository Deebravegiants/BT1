# [?] torrent: cherry-pick from r31 to fix panic on index out of range in torrent lib (#17190)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-09-22
Source: https://github.com/erigontech/erigon/commit/cb9db1ece65494fedaf819180f45fe22c7bac925
Type: security-commit

## Details
torrent: cherry-pick from r31 to fix panic on index out of range in torrent lib (#17190)

cherry-pick of https://github.com/erigontech/erigon/pull/16990 since I
run into the same panic in `main` while running tests
