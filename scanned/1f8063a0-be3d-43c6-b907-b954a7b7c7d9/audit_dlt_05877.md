# [?] miner: fix data race during shutdown (#23435)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/go-ethereum
Published: 2021-10-08
Source: https://github.com/scroll-tech/go-ethereum/commit/ee120ef865e9468fef0bbb0a0bcffba93e3e358e
Type: security-commit

## Details
miner: fix data race during shutdown (#23435)

This fixes a data race on worker.current by moving the call to StopPrefetcher
into the main loop.

The commit also contains fixes for two other races in unit tests of unrelated packages.
