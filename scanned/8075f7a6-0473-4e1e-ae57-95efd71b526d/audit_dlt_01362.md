# [?] miner: fix race condition in tests (#1651)

## Summary
Severity: Unknown
Chain: Polygon
Component: maticnetwork/bor
Published: 2025-07-22
Source: https://github.com/0xPolygon/bor/commit/c302516193cdfa3f0d3b6434ea1aa7e47513169d
Type: security-commit

## Details
miner: fix race condition in tests (#1651)

Use a new config for all tests (some of which run in parallel) instead of using a global test config which can cause race conditions if some fields (like commit interrupt) are modified for some tests.
