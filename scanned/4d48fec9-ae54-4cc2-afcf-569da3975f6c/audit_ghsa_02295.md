# [C] Use-after-free in chttp

## Summary
Severity: Critical
Advisory: GHSA-5rrv-m36h-qwf8
CVE: CVE-2019-16140
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-5rrv-m36h-qwf8
Type: github-advisory

## Affected
- crates.io: `chttp` — affected >=0.1.1 <0.1.3

## Details
The From implementation for Vec was not properly implemented, returning a vector backed by freed memory. This could lead to memory corruption or be exploited to cause undefined behavior.

A fix was published in version 0.1.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16140
- https://github.com/sagebind/isahc/issues/2
- https://github.com/sagebind/isahc/commit/9e9f1fb44114078c000c78c72e691eeb9e7ac260
- https://github.com/sagebind/chttp
- https://rustsec.org/advisories/RUSTSEC-2019-0016.html
