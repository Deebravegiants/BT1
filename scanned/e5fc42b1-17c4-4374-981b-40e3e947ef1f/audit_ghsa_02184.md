# [M] Data race in atomic-option

## Summary
Severity: Medium
Advisory: GHSA-8gf5-q9p9-wvmc
CVE: CVE-2020-36219
CWE: CWE-662
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-8gf5-q9p9-wvmc
Type: github-advisory

## Affected
- crates.io: `atomic-option` — affected >=0

## Details
An issue was discovered in the atomic-option crate through 2020-10-31 for Rust. Because AtomicOption<T> implements Sync unconditionally, a data race can occur.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36219
- https://github.com/reem/rust-atomic-option/issues/4
- https://github.com/reem/rust-atomic-option
- https://rustsec.org/advisories/RUSTSEC-2020-0113.html
