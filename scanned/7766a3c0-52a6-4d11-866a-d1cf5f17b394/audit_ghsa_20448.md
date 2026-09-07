# [C] Memory flaw in zeroize_derive

## Summary
Severity: Critical
Advisory: GHSA-c5hx-w945-j4pq
CVE: CVE-2021-45706
CWE: CWE-459
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-c5hx-w945-j4pq
Type: github-advisory

## Affected
- crates.io: `zeroize_derive` — affected >=0 <1.1.1

## Details
An issue was discovered in the zeroize_derive crate before 1.1.1 for Rust. Dropped memory is not zeroed out for an enum.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45706
- https://github.com/iqlusioninc/crates/issues/876
- https://github.com/RustCrypto/utils/tree/master/zeroize/derive
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/zeroize_derive/RUSTSEC-2021-0115.md
- https://rustsec.org/advisories/RUSTSEC-2021-0115.html
