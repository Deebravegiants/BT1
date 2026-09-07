# [?] fix(ci): Prevent race condition in GCP static IP assignment (#10159)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-01-26
Source: https://github.com/ZcashFoundation/zebra/commit/650d0f25cfcf54200e1ce2d5c8e945025a68951f
Type: security-commit

## Details
fix(ci): Prevent race condition in GCP static IP assignment (#10159)

Use --no-address in instance template so instances start without
ephemeral IPs. This prevents the MIG controller from racing to restore
ephemeral IPs when assigning static IPs.

Closes #10158
