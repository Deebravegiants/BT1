# [C] electerm allows unauthorized users to execute arbitrary commands

## Summary
Severity: Critical
Advisory: GHSA-x73w-g8hx-v7rp
CVE: CVE-2020-23256
CWE: CWE-306, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-20
Source: https://github.com/advisories/GHSA-x73w-g8hx-v7rp
Type: github-advisory

## Affected
- npm: `electerm` — affected >=0

## Details
An issue was discovered in Electerm 1.3.22, allows attackers to execute arbitrary commands via unverified request to electerms service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-23256
- https://github.com/electerm/electerm/issues/1686
- https://github.com/electerm/electerm
