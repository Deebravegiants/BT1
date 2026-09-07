# [?] Update bytes to 1.11.1 (RUSTSEC-2026-0007).

## Summary
Severity: Unknown
Chain: Zcash
Component: zcash/zcash
Published: 2026-04-15
Source: https://github.com/zcash/zcash/commit/59b5784294d3e7872ce9436d4a625a95edb1ba3b
Type: security-commit

## Details
Update bytes to 1.11.1 (RUSTSEC-2026-0007).

Fix integer overflow in BytesMut::reserve that could cause
out-of-bounds memory access. Only affects the optional Prometheus
metrics exporter when enabled via -prometheusport. On platforms
with 64-bit usize, triggering the overflow would require a request
large enough to overflow 2^64, which is not practically achievable.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
