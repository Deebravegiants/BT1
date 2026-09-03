# [?] Fixed race condition in `ElectrumClient` (#509)

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ACINQ/eclair
Published: 2018-03-24
Source: https://github.com/ACINQ/eclair/commit/64c15b4c4d8e744e3c57d3437f6ad31f5b134862
Type: security-commit

## Details
Fixed race condition in `ElectrumClient` (#509)

This regression caused in 438d8e3 is what caused flaky tests during the past few days.

Calling `sender()` inside a `Props()` leads to undefined behavior.
