# [C] Use of Uninitialized Resource in gfx-auxil

## Summary
Severity: Critical
Advisory: GHSA-ff2r-xpwq-6whj
CVE: CVE-2021-45689
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-ff2r-xpwq-6whj
Type: github-advisory

## Affected
- crates.io: `gfx-auxil` — affected >=0

## Details
Affected versions of this crate passes an uninitialized buffer to a user-provided Read implementation.

Arbitrary Read implementations can read from the uninitialized buffer (memory exposure) and also can return incorrect number of bytes written to the buffer. Reading from uninitialized memory produces undefined values that can quickly invoke undefined behavior.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45689
- https://github.com/gfx-rs/gfx/issues/3567
- https://github.com/gfx-rs/gfx
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/gfx-auxil/RUSTSEC-2021-0091.md
- https://rustsec.org/advisories/RUSTSEC-2021-0091.html
