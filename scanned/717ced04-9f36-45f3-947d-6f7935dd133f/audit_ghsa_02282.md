# [C] Incorrect buffer size calculation in iced-x86

## Summary
Severity: Critical
Advisory: GHSA-jjx5-3f36-6927
CVE: CVE-2021-38188
CWE: CWE-131
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-jjx5-3f36-6927
Type: github-advisory

## Affected
- crates.io: `iced-x86` — affected >=0 <1.11.0

## Details
An issue was discovered in the iced-x86 crate through 1.10.3 for Rust. In Decoder::new(), slice.get_unchecked(slice.length()) is used unsafely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38188
- https://github.com/icedland/iced/issues/168
- https://github.com/icedland/iced/commit/3c607a003e03b773108401d109167d1840487dce
- https://github.com/icedland/iced
- https://rustsec.org/advisories/RUSTSEC-2021-0068.html
