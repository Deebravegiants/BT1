# [?] fix: excess overflow in `gastime.Time.Tick()` (#297)

## Summary
Severity: Unknown
Chain: Avalanche
Component: ava-labs/avalanchego
Published: 2026-03-25
Source: https://github.com/ava-labs/avalanchego/commit/bdcda4ab0f25242ef63f326e9bf19c599b5dc258
Type: security-commit

## Details
fix: excess overflow in `gastime.Time.Tick()` (#297)

Although this could only occur under extreme circumstances (e.g. scaling
due to min-price change) it still requires handling. The fuzzer could
only find 3 interesting cases for the new `intmath.BoundedAdd()` (more
included via `f.Add()` though) so I had to reduce the minimum required
corpus size.
