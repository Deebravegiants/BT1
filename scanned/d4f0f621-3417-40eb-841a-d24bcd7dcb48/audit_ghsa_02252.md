# [C] Rust Failure Crate Vulnerable to Type confusion

## Summary
Severity: Critical
Advisory: GHSA-r98r-j25q-rmpr
CVE: CVE-2019-25010
CWE: CWE-843
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-r98r-j25q-rmpr
Type: github-advisory

## Affected
- crates.io: `failure` — affected >=0

## Details
Safe Rust code can implement malfunctioning `__private_get_type_id__` and cause type confusion when downcasting, which is an undefined behavior.

Users who derive Fail trait are not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-25010
- https://github.com/rust-lang-nursery/failure/issues/336
- https://github.com/rust-lang-nursery/failure
- https://rustsec.org/advisories/RUSTSEC-2019-0036.html
