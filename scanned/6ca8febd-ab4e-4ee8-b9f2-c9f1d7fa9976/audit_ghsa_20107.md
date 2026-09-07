# [M] Echo vulnerable to directory traversal

## Summary
Severity: Medium
Advisory: GHSA-j453-hm5x-c46w
CVE: CVE-2020-36565
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-12-07
Source: https://github.com/advisories/GHSA-j453-hm5x-c46w
Type: github-advisory

## Affected
- Go: `github.com/labstack/echo/v4` — affected >=0 <4.2.0

## Details
Due to improper sanitization of user input on Windows, the static file handler allows for directory traversal, allowing an attacker to read files outside of the target directory that the server has permission to read.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36565
- https://github.com/labstack/echo/pull/1718
- https://github.com/labstack/echo/commit/4422e3b66b9fd498ed1ae1d0242d660d0ed3faaa
- https://github.com/labstack/echo
- https://pkg.go.dev/vuln/GO-2021-0051
