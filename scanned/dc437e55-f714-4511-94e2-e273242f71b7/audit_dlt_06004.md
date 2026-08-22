# [?] ethstats: prevent panic if head block is not available (#29020)

## Summary
Severity: Unknown
Chain: Ethereum Classic
Component: etclabscore/core-geth
Published: 2024-02-19
Source: https://github.com/etclabscore/core-geth/commit/034bc4669ffe92b95155c8331334f47fa8bb4333
Type: security-commit

## Details
ethstats: prevent panic if head block is not available (#29020)

This pull request fixes a flaw in ethstats which can lead to node crash

A panic could happens when the local blockchain is reorging which causes the original head block not to be  reachable (since number->hash canonical mapping is deleted). In order to prevent the panic, the block nilness is now checked in ethstats.
