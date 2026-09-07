# [H] Update unsound DrainFilter and RString::retain

## Summary
Severity: High
Advisory: GHSA-wqxc-qrq4-w5v4
CVE: CVE-2020-36213
CWE: CWE-172
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-wqxc-qrq4-w5v4
Type: github-advisory

## Affected
- crates.io: `abi_stable` — affected >=0 <0.9.1

## Details
An issue was discovered in the abi_stable crate before 0.9.1 for Rust. A retain call can create an invalid UTF-8 string, violating soundness.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36213
- https://github.com/rodrimati1992/abi_stable_crates/issues/44
- https://rustsec.org/advisories/RUSTSEC-2020-0105.html
