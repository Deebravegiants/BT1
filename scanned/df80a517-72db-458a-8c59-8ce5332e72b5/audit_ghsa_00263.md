# [H] Path Traversal in hekto

## Summary
Severity: High
Advisory: GHSA-x26f-26qw-hhhx
CVE: CVE-2018-3725
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-07-26
Source: https://github.com/advisories/GHSA-x26f-26qw-hhhx
Type: github-advisory

## Affected
- npm: `hekto` — affected >=0 <0.2.3

## Details
Versions of `hekto` before 0.2.3 are vulnerable to path traversal. This allows a remote attacker to read content of arbitrary files.


## Recommendation

Update to version 0.2.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3725
- https://hackerone.com/reports/311218
- https://github.com/advisories/GHSA-x26f-26qw-hhhx
- https://www.npmjs.com/advisories/586
