# [C] Out-of-bounds write in stack

## Summary
Severity: Critical
Advisory: GHSA-h45v-vgvp-3h5v
CVE: CVE-2020-35895
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-h45v-vgvp-3h5v
Type: github-advisory

## Affected
- crates.io: `stack` — affected >=0 <0.3.1

## Details
ArrayVec::insert allows insertion of an element into the array object into the specified index. Due to a missing check on the upperbound of this index, it is possible to write out of bounds.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35895
- https://github.com/arcnmx/stack-rs/issues/4
- https://github.com/arcnmx/stack-rs/commit/369e55736f9bd29c37b1712afc2923f4028148c6
- https://github.com/arcnmx/stack-rs
- https://rustsec.org/advisories/RUSTSEC-2020-0042.html
