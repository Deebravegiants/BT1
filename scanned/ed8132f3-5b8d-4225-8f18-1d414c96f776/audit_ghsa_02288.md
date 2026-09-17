# [H] Overflow in prost-types

## Summary
Severity: High
Advisory: GHSA-x4qm-mcjq-v2gf
CVE: CVE-2021-38192
CWE: CWE-120, CWE-190
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-x4qm-mcjq-v2gf
Type: github-advisory

## Affected
- crates.io: `prost-types` — affected >=0 <0.8.0

## Details
Affected versions of this crate contained a bug in which untrusted input could cause an overflow and panic when converting a Timestamp to SystemTime. It is recommended to upgrade to prost-types v0.8 and switch the usage of From<Timestamp> for SystemTime to TryFrom<Timestamp> for SystemTime.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38192
- https://github.com/tokio-rs/prost/issues/438
- https://github.com/tokio-rs/prost/pull/439
- https://github.com/tokio-rs/prost/commit/59f2a7311dd6540696bfd0145f5281ce495f4385
- https://github.com/tokio-rs/prost/tree/master/prost-types
- https://rustsec.org/advisories/RUSTSEC-2021-0073.html
