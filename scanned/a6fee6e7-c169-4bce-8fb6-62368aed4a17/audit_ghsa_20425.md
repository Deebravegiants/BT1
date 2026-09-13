# [C] Use of Uninitialized Resource in buffoon.

## Summary
Severity: Critical
Advisory: GHSA-v938-qcc9-rwv8
CVE: CVE-2020-36512
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-v938-qcc9-rwv8
Type: github-advisory

## Affected
- crates.io: `buffoon` — affected >=0

## Details
Affected versions of this crate passes an uninitialized buffer to a user-provided Read implementation.
Arbitrary Read implementations can read from the uninitialized buffer (memory exposure) and also can return incorrect number of bytes written to the buffer. Reading from uninitialized memory produces undefined values that can quickly invoke undefined behavior.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36512
- https://github.com/carllerche/buffoon/issues/2
- https://github.com/carllerche/buffoon
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/buffoon/RUSTSEC-2020-0154.md
- https://rustsec.org/advisories/RUSTSEC-2020-0154.html
