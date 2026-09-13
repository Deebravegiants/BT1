# [C] Incorrect cast in anymap

## Summary
Severity: Critical
Advisory: GHSA-hc92-9h3m-c39j
CVE: CVE-2021-38187
CWE: CWE-681, CWE-704
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-hc92-9h3m-c39j
Type: github-advisory

## Affected
- crates.io: `anymap` — affected >=0

## Details
An issue was discovered in the anymap crate through 0.12.1 for Rust. It violates soundness via conversion of a *u8 to a *u64.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38187
- https://github.com/chris-morgan/anymap/issues/37
- https://github.com/chris-morgan/anymap
- https://rustsec.org/advisories/RUSTSEC-2021-0065.html
