# [M] jxl-oxide: integer subtraction overflow panic in cluster_from_table via crafted JXL input (DoS)

## Summary
Severity: Medium
Advisory: GHSA-2v8p-fqpx-2q3w
CWE: CWE-190
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-2v8p-fqpx-2q3w
Type: github-advisory

## Affected
- crates.io: `jxl-modular` — affected >=0 <0.11.3

## Details
### Summary
Logic bug in `decode_simple_table_slow` may cause integer arithmetic overflow when decoding Modular image with certain kind of MA tree, which may panic with `overflow-checks` enabled.

### Impact
Denial of service: any application passing untrusted JXL data to `JxlImage::render_frame` (or equivalent) can be
crashed. Affects all builds with overflow checks enabled, which includes debug builds and any release build
that sets `overflow-checks = true` in Cargo.toml or `[profile.*]`.

No memory corruption is possible — the panic fires before any unsafe code is reached.

## References
- https://github.com/tirr-c/jxl-oxide/security/advisories/GHSA-2v8p-fqpx-2q3w
- https://github.com/tirr-c/jxl-oxide
