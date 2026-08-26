# [?] fix: resolve TestAddMultipleGCLive race condition (#10916)

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2025-08-18
Source: https://github.com/ipfs/kubo/commit/a81cc2928247829e12c2a76d8b7041232a9fe29c
Type: security-commit

## Details
fix: resolve TestAddMultipleGCLive race condition (#10916)

test was expecting immediate GC lock acquisition after pipe close,
but timing wasn't guaranteed. replaced blocking wait with 5-second
timeout to handle timing variations while still detecting deadlocks.
