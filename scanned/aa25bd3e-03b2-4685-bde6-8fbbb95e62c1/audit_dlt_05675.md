# [?] eth: fix concurrent map writes panic in witness protocol (#2023)

## Summary
Severity: Unknown
Chain: Polygon
Component: maticnetwork/bor
Published: 2026-01-29
Source: https://github.com/0xPolygon/bor/commit/8dbb965a9bb9dfe5f3deab87c05fa01ced34636e
Type: security-commit

## Details
eth: fix concurrent map writes panic in witness protocol (#2023)

Protect failedRequests map access with mapsMu lock in receiveWitnessPage and buildWitnessRequests to prevent "concurrent map writes" panic when multiple goroutines update retry counts simultaneously.
