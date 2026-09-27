# [?] Add lock around catchpointsMu to avoid race condition (#3944)

## Summary
Severity: Unknown
Chain: Algorand
Component: algorand/go-algorand
Published: 2022-05-03
Source: https://github.com/algorand/go-algorand/commit/cd4015a00c47e3a583ee239ce2ca1145dd73f213
Type: security-commit

## Details
Add lock around catchpointsMu to avoid race condition (#3944)

While upgrading to golang 1.17.9 a couple of race conditions have been detected during E2E tests.
This fixes catchpoint label assignment.
