# [C] tar-utils Path Traversal vulnerability

## Summary
Severity: Critical
Advisory: GHSA-jpf8-h7h7-3ppm
CVE: CVE-2020-36566
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-jpf8-h7h7-3ppm
Type: github-advisory

## Affected
- Go: `github.com/whyrusleeping/tar-utils` — affected >=0 <0.0.0-20201201191210-20a61371de5b

## Details
Due to improper path sanitization, archives containing relative file paths can cause files to be written (or overwritten) outside of the target directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36566
- https://github.com/whyrusleeping/tar-utils/commit/20a61371de5b51380bbdb0c7935b30b0625ac227
- https://github.com/whyrusleeping/tar-utils
- https://pkg.go.dev/vuln/GO-2021-0106
- https://snyk.io/research/zip-slip-vulnerability
