# [?] Fix data race in workflow engine beholder test polling (#22927)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2026-06-24
Source: https://github.com/smartcontractkit/chainlink/commit/bcb30d320b282adb7a0ecb8a723a41a049e65273
Type: security-commit

## Details
Fix data race in workflow engine beholder test polling (#22927)

Fix data race in workflow engine beholder test polling.

Filter beholdertest.Messages by beholder_entity so reads take the RLock
path while the engine emits user logs and base messages concurrently.
