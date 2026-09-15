# [M] Out of bounds read in dync

## Summary
Severity: Medium
Advisory: GHSA-qxjq-v4wf-ppvh
CVE: CVE-2020-35903
CWE: CWE-125
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-qxjq-v4wf-ppvh
Type: github-advisory

## Affected
- crates.io: `dync` — affected >=0 <0.5.0

## Details
VecCopy::data is created as a Vec of u8 but can be used to store and retrieve elements of different types leading to misaligned access.

The issue was resolved in v0.5.0 by replacing data being stored by Vec<u8> with a custom managed pointer. Elements are now stored and retrieved using types with proper alignment corresponding to original types.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35903
- https://github.com/elrnv/dync/issues/4
- https://github.com/elrnv/dync
- https://rustsec.org/advisories/RUSTSEC-2020-0050.html
