# [?] chore: bump vitest to fix audit vulnerability (#4715)

## Summary
Severity: Unknown
Chain: Tooling
Component: wevm/viem
Published: 2026-06-04
Source: https://github.com/wevm/viem/commit/a74b05d6e6a4c74ce74990469804858a77af612e
Type: security-commit

## Details
chore: bump vitest to fix audit vulnerability (#4715)

chore: bump vitest to ^4.1.8 to fix audit vulnerability

Resolves the critical advisory GHSA-5xrq-8626-4rwp (vitest <4.1.0), which
was failing the CI `pnpm audit` check.

Amp-Thread-ID: https://ampcode.com/threads/T-019e8cab-fd02-709f-9185-a2766192718b
