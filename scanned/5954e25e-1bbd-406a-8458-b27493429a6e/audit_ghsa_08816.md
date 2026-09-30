# [H] rust-zserio has Unbounded Memory Allocation

## Summary
Severity: High
Advisory: GHSA-fpf5-4jw8-67x8
CWE: CWE-789
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-fpf5-4jw8-67x8
Type: github-advisory

## Affected
- crates.io: `rust-zserio` — affected >=0 <0.5.4

## Details
### Impact

When deserializing arrays, strings or bytes (blob) types zserio first reads the size of the variable, and then allocates sufficient memory to load data. Since the size is always trusted this can be abused by creating a data file with a large size value, causing the zserio runtime to allocate large amounts of memory.

### Patches

Please cherry-pick [57f5fb](https://github.com/Danaozhong/rust-zserio/commit/57f5fb4a2a8611d58dbcc1a9221349206dd99c3c).

### Workarounds

- Do not accept `zserio`-encoded messages from non-trusted sources.
- Allocate a maximum heap amount to `rust-zerio` to avoid impacting other applications.

## References
- https://github.com/Danaozhong/rust-zserio/security/advisories/GHSA-fpf5-4jw8-67x8
- https://github.com/ndsev/zserio/security/advisories/GHSA-cwq5-8pvq-j65j
- https://github.com/Danaozhong/rust-zserio/commit/57f5fb4a2a8611d58dbcc1a9221349206dd99c3c
- https://github.com/Danaozhong/rust-zserio
