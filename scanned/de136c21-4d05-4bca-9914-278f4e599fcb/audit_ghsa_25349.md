# [C] gitjacker arbitrary code execution

## Summary
Severity: Critical
Advisory: GHSA-4j5x-f394-xx79
CVE: CVE-2021-29417
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4j5x-f394-xx79
Type: github-advisory

## Affected
- Go: `github.com/liamg/gitjacker` — affected >=0 <0.1.0

## Details
gitjacker before 0.1.0 allows remote attackers to execute arbitrary code via a crafted .git directory because of directory traversal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29417
- https://github.com/liamg/gitjacker/compare/v0.0.3...v0.1.0
- https://github.com/liamg/gitjacker/releases/tag/v0.1.0
- https://vuln.ryotak.me/advisories/5
