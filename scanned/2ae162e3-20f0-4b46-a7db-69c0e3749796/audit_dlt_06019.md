# [?] fix: Leaving Unknown Federation causes panic (#8396)

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-03-20
Source: https://github.com/fedimint/fedimint/commit/182bebcf96c92768e3edd7cafa4b9fc1902a8c73
Type: security-commit

## Details
fix: Leaving Unknown Federation causes panic (#8396)

Currently, if the gateway operator uses the CLI to leave an unknown
federation, the gateway will panic. This fixes the bug by returning an
error instead of panicking.
