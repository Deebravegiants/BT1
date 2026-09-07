# [M] m-server Vulnerable to Directory Traversal

## Summary
Severity: Medium
Advisory: GHSA-899g-6q6w-7v94
CVE: CVE-2018-16485
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-899g-6q6w-7v94
Type: github-advisory

## Affected
- npm: `m-server` — affected >=0 <1.4.1

## Details
Path Traversal vulnerability in module m-server <1.4.1 allows malicious user to access unauthorized content of any file in the directory tree e.g. /etc/passwd by appending slashes to the URL request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16485
- https://hackerone.com/reports/319795
- https://github.com/advisories/GHSA-899g-6q6w-7v94
