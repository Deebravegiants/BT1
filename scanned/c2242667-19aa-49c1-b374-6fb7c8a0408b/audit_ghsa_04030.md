# [H] mcstatic directory traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-cxmj-qjv6-vx9p
CVE: CVE-2018-16482
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-02-07
Source: https://github.com/advisories/GHSA-cxmj-qjv6-vx9p
Type: github-advisory

## Affected
- npm: `mcstatic` — affected >=0

## Details
A server directory traversal vulnerability was found on node module mcstatic <=0.0.20 that would allow an attack to access sensitive information in the file system by appending slashes in the URL path.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16482
- https://hackerone.com/reports/330285
- https://github.com/advisories/GHSA-cxmj-qjv6-vx9p
