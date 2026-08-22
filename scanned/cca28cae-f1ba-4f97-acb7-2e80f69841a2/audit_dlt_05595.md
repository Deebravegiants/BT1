# [?] cmd/geth: remove deprecated vulnerability check command (#33498)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-12-30
Source: https://github.com/ethereum/go-ethereum/commit/52ae75afcda074d46a07fb017c334c2862f162be
Type: security-commit

## Details
cmd/geth: remove deprecated vulnerability check command (#33498)

This PR removes the version-check command and its associated logic as
discussed in issue #31222.

Removed versionCheckCommand from misccmd.go and main.go.

Deleted version_check.go and its corresponding tests.

Cleaned up testdata/vcheck directory (~800 lines of JSON/signatures
removed).

Verified build with make geth
